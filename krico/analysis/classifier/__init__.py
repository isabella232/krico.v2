import theanets
import numpy
import sklearn.metrics

import krico.core.configuration
import krico.core.database
import krico.core.lexicon
import krico.core.logger

import krico.analysis.categories

import krico.analysis.classifier.converter
import krico.analysis.classifier.dataprovider
import krico.analysis.classifier.instance

__author__ = 'porzech'

_logger = krico.core.logger.get(__name__)
_configuration = krico.core.configuration.root


class ClassifierDataError(RuntimeError):
    def __init__(self, message):
        RuntimeError.__init__(self, message)
        _logger.error(message)

    def __str__(self):
        return 'KRICO Classifier Data Error: {}'.format(self.message)


class _Classifier(object):
    def __init__(self, lexicon):
        self._data = lexicon

    def train(self, dataset, algorithm='sgd', learning_rate=0.01, momentum=0.9, min_improvement=1.0e-4):
        max_iterations = 1e6
        iteration = 0

        for training_result, validation_result in self._data.experiment.data.itertrain(
                dataset['train'],
                dataset['validation'],
                algorithm=algorithm,
                learning_rate=learning_rate,
                momentum=momentum,
                min_improvement=min_improvement
        ):
            iteration += 1

            if iteration > max_iterations:
                raise ClassifierDataError('Learning process failed.')

            if iteration % 100 == 1:
                _logger.debug('Iteration {:7d}: Training loss = {:10.7f}, Validation loss = {:10.7f}'.format(iteration,
                                                                                                             training_result[
                                                                                                                 'loss'],
                                                                                                             validation_result[
                                                                                                                 'loss']))

        result = self._data.experiment.data.network.predict(dataset['test'][0])
        self._score_prediction(result, dataset['test'][1])

    def predict(self, test_data):
        data = self._normalize_test_data(test_data)
        return self._data.experiment.data.network.predict(data)

    def data(self):
        return self._data

    def _normalize_test_data(self, sample):

        _logger.debug('Normalizing sample to prediction.')

        normalized_sample = numpy.array(
            [[
                 float(sample[metric]) / self._data.maxima[metric]
                 for metric in self._data.metrics_names
                 ]])

        return normalized_sample

    @staticmethod
    def _score_prediction(prediction, expected):
        _, _, f1, s = sklearn.metrics.precision_recall_fscore_support(expected, prediction, labels=range(0, 6))
        _logger.info('\nAverage: {}'.format(numpy.average(f1, weights=s)))

        categories = krico.analysis.categories.names
        categories_count = len(categories)

        report = sklearn.metrics.classification_report(expected, prediction, range(0, categories_count), categories)
        _logger.debug('\n{}'.format(report))

        confusion_matrix = sklearn.metrics.confusion_matrix(expected, prediction, range(0, categories_count))
        _logger.debug('\n{}'.format(confusion_matrix))


def classify(instance, monitor_samples):
    _logger.info('classify()')

    configuration_id = instance.host_aggregate.configuration_id
    classifier = _get_classifier(configuration_id)
    mean_load = krico.analysis.classifier.instance.compute_load(monitor_samples)

    prediction = classifier.predict(mean_load)[0]

    _logger.info(
        'Category predicted for {} is: {}({})'.format(instance.instance_id, krico.analysis.categories.names[prediction],
                                                      prediction))

    return prediction


def refresh():
    _logger.info('Refreshing classifiers.')

    configurations = krico.core.database.Analysis.classifier_instances.distinct('availability_zone.configuration_id')
    classifier_networks = []

    for configuration in configurations:
        _logger.info('Refreshing classifier for configuration: {}'.format(configuration))
        categories_count = krico.analysis.classifier.dataprovider.count_instances_for_configuration_by_category(
            configuration)

        min_count_per_category = _configuration.analysis.classifier.minimal_instances_per_category
        ready_categories = len(filter(lambda category: category['count'] > min_count_per_category, categories_count))
        _logger.info(
            'Configuration {} has {} number of categories with minimal value of instances.'.format(configuration,
                                                                                                   ready_categories))

        if ready_categories == len(krico.analysis.categories.names):
            try:
                classifier_networks.append(_create_classifier(configuration))
            except Exception as ex:
                _logger.error('Cannot create classifier network for configuration {}: {}'.format(configuration, ex))
        else:
            _logger.info('Not enough data to create classifier for configuration.')

    if classifier_networks:
        _logger.debug('Deleting classifier networks and statistics data')
        krico.core.database.Analysis.classifier_networks.delete_many({})                                                                                   
        krico.core.database.Analysis.classifier_statistics.delete_many({})

        _logger.debug('Inserting generated classifier networks to database')
        for network in classifier_networks:    
            krico.core.database.Analysis.classifier_networks.insert_one(network)
    else:
        _logger.error('No classifier networks generated')


def _create_classifier(configuration):
    krico.analysis.classifier.converter.prepare_statistics(configuration)

    classifier_lexicon = krico.core.lexicon.Lexicon()
    classifier_lexicon.maxima = krico.analysis.classifier.dataprovider.get_max_metrics_values(configuration)
    classifier_lexicon.metrics_names = sorted(_configuration.analysis.classifier.metrics)
    classifier_lexicon.experiment = krico.core.database.BinaryObjectWrapper(
        theanets.Experiment(
            theanets.Classifier,
            layers=(
                len(classifier_lexicon.metrics_names),
                (18, 'sigmoid'),
                len(krico.analysis.categories.names)
            )))
    # layers=(
    # 	len(classifier_lexicon.metrics_names),
    # 	(99, 'sigmoid'),
    # 	(55, 'logistic'),
    # 	len(_configuration.workloads.categories)
    # )))
    classifier = _Classifier(classifier_lexicon)
    learning_data = _get_classifier_learning_set(configuration)
    classifier.train(learning_data)

    network = krico.core.lexicon.Lexicon({
        'configuration_id': configuration,
        'network': classifier.data()
    })

    return network


def _get_classifier_learning_set(configuration_id):
    data = krico.core.database.Analysis.classifier_statistics.load_many({'configuration_id': configuration_id})
    instances_set = krico.analysis.classifier.instance.ClassifierInstancesSet()
    instances_set.add_instances(data)

    instances_set.normalize()

    coefficients = _configuration.analysis.classifier.partitioning_coefficients
    learning_set = instances_set.select_learning_sets(coefficients)

    for key, value in learning_set.iteritems():
        _logger.info('{} {} {}'.format(key, value[0].shape, value[1].shape))

    return learning_set


def _get_classifier(configuration_id):
    """
    Load classifier for given configuration or default if classifier for given configuration doesn't exists and return.
    :rtype: _Classifier
    :param configuration_id:
    :return: classifier object
    """

    document = krico.core.database.Analysis.classifier_networks.load_one({'configuration_id': configuration_id})

    if not document:
        document = krico.core.database.Analysis.classifier_networks.load_one(
            {'configuration_id': _configuration.analysis.classifier.default})

    return _Classifier(document.network)
