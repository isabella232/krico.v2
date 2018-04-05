import numpy
import krico.core.configuration
import krico.core.database
import krico.core.lexicon
import krico.core.logger

import krico.analysis.categories
import krico.analysis.classifier.instance

__author__ = 'porzech'

_logger = krico.core.logger.get(__name__)
_configuration = krico.core.configuration.root


def prepare_statistics(configuration_id):
    _logger.debug('Fetching all instances for configuration: {}'.format(configuration_id))

    metrics_names = sorted(_configuration.analysis.classifier.metrics)
    instances_metrics = krico.analysis.classifier.instance.InstancesSet()

    data = []
    for category in krico.analysis.categories.names:
        instances = krico.core.database.Analysis.classifier_instances.load_many(
            {'category': category, 'availability_zone.configuration_id': configuration_id})
        for instance in instances:
            instances_metrics.add_instance(instance)

            metrics = {
                metric: instance.load_measured[metric]
                for metric in metrics_names
                }
            data.append(metrics)

    _logger.info('{}'.format(instances_metrics))

    maxima = krico.analysis.classifier.dataprovider.get_max_metrics_values(configuration_id)
    norm_data = _create_normalized_array(metrics_names, maxima, data)

    experiments_index = 0
    for category in krico.analysis.categories.names:
        category_count = instances_metrics.category_count(category)
        instances_metrics.update_category_data(category,
                                               norm_data[experiments_index:experiments_index + category_count])
        experiments_index += category_count

        names = instances_metrics.category_names(category)
        data = instances_metrics.category_data(category)

        samples = [
            _generate_sample(category, name, data, metrics_names, configuration_id)
            for name, data in zip(names, data)]

        krico.core.database.Analysis.classifier_statistics.insert_many(samples)


def _create_normalized_array(keys, maxima, sequence):
    return numpy.array([_normalize_sample(keys, maxima, sample) for sample in sequence])


def _normalize_sample(keys, maxima, sample):
    return [float(sample[key]) / maxima[key] for key in keys]


def _generate_sample(category_name, name, data, metrics_names, configuration_id):
    return krico.core.lexicon.Lexicon(
        document={
            'category': category_name,
            'name': name,
            'metrics': dict(zip(metrics_names, list(data))),
            'configuration_id': configuration_id
        })
