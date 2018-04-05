import numpy
import sklearn.preprocessing
import krico.core.configuration
import krico.core.database
import krico.core.exception
import krico.core.logger
import krico.analysis.categories

__author__ = 'porzech'

_logger = krico.core.logger.get(__name__)
_configuration = krico.core.configuration.root


class _Instance(object):
    def __init__(self, name, category, metrics=None):
        object.__init__(self)
        self._name = name
        self._category = category
        self._metrics = metrics

    @property
    def name(self):
        return self._name

    @property
    def metrics(self):
        return self._metrics

    @metrics.setter
    def metrics(self, value):
        self._metrics = value

    @property
    def category(self):
        return self._category

    def __str__(self):
        return self._name


class InstancesSet(object):
    def __init__(self):
        object.__init__(self)
        self._categories = {}

    def add_instance(self, document):
        instance = _InstanceMapper.map_instance(document)
        if instance.category not in self._categories:
            self._categories[instance.category] = []
        self._categories[instance.category].append(instance)

    def category_count(self, category):
        return len(self._categories[category])

    def update_category_data(self, category, param):

        if len(param) != len(self._categories[category]):
            raise krico.core.exception.Error(
                'Number of instances {} for category {} is not equal size of data to update {}'.format(
                    len(self._categories[category]), category, len(param)))

        for instance, data in zip(self._categories[category], param):
            instance.metrics = data

    def category_names(self, category):
        names = []
        for instance in self._categories[category]:
            names.append(instance.name)
        return names

    def category_data(self, category):
        data = []
        for instance in self._categories[category]:
            data.append(instance.metrics)
        return numpy.array(data)


class ClassifierInstancesSet(InstancesSet):
    def __init__(self):
        InstancesSet.__init__(self)

    def add_instances(self, data):
        for document in data:
            self.add_instance(document)

    def add_instance(self, document):
        instance = _InstanceMapper.map_classifier_instance(document)
        if instance.category not in self._categories:
            self._categories[instance.category] = []
        self._categories[instance.category].append(instance)

    def normalize(self):
        data = self.__get_data()
        sklearn.preprocessing.normalize(data, copy=False)
        self.__update_data(data)

    def scale(self):
        data = self.__get_data()
        sklearn.preprocessing.scale(data, copy=False)
        self.__update_data(data)

    def __get_data(self):
        data = []
        for category_name in krico.analysis.categories.names:
            data.extend(self.category_data(category_name))
        return numpy.array(data, dtype=numpy.float64)

    def __update_data(self, data):
        start_idx = 0
        for category_name in krico.analysis.categories.names:
            end_idx = self.category_count(category_name) + start_idx
            self.update_category_data(category_name, data[start_idx:end_idx])
            start_idx = end_idx

    def select_learning_sets(self, partitioning_coefficients):

        metrics_number = len(_configuration.analysis.classifier.metrics)

        learning_set = {
            'train': [
                numpy.empty((0, metrics_number), dtype=numpy.float32),
                numpy.empty((0,), dtype=numpy.int32),
            ],
            'validation': [
                numpy.empty((0, metrics_number), dtype=numpy.float32),
                numpy.empty((0,), dtype=numpy.int32),
            ],
            'test': [
                numpy.empty((0, metrics_number), dtype=numpy.float32),
                numpy.empty((0,), dtype=numpy.int32),
            ],
        }

        for category in krico.analysis.categories.names:
            _logger.debug('Get classifier data for category: {}'.format(category))
            category_sets = self._select_category_learning_sets(category, partitioning_coefficients)

            for key, value in category_sets.iteritems():
                learning_set[key][0] = numpy.append(learning_set[key][0], value[0], axis=0)
                learning_set[key][1] = numpy.append(learning_set[key][1], value[1], axis=0)
        return learning_set

    def _select_category_learning_sets(self, category_name, partitioning_coefficients):

        slices = ClassifierInstancesSet.compute_partitioning_indexes(partitioning_coefficients,
                                                                     self.category_count(category_name))

        _logger.info('Samples count: {}, slices: {}'.format(self.category_count(category_name), slices))

        input_data = numpy.array(self._categories[category_name])
        numpy.random.shuffle(input_data)
        classifier_data = {}

        for label in slices:
            classifier_data[label] = ClassifierInstancesSet.slice_data(input_data, slices[label], label, category_name)

        return classifier_data

    @staticmethod
    def slice_data(samples, sl, label, category_name):
        samples_subset = samples[sl[0]:sl[1]]
        samples_subset = numpy.array([instance.metrics for instance in samples_subset])
        _logger.info('Sample subset for label {} has size {}'.format(label, samples_subset.shape))
        results_subset = numpy.full((len(samples_subset),), krico.analysis.categories.names.index(category_name),
                                    dtype=numpy.int32)
        return tuple((samples_subset, results_subset))

    @staticmethod
    def compute_partitioning_indexes(partitioning_coefficients, count):
        starts = numpy.floor(numpy.cumsum(count * numpy.hstack([0, partitioning_coefficients[:-1]])))
        slices = {
            'train': (int(starts[0]), int(starts[1])),
            'validation': (int(starts[1]), int(starts[2])),
            'test': (int(starts[2]), None)}
        return slices

    def __str__(self):
        output = ''
        for category_name in krico.analysis.categories.names:
            category = self._categories[category_name]
            output += '{} {}\n'.format(category_name, len(category))
        return output


class _InstanceMapper(object):
    @staticmethod
    def map_instance(data):
        return _Instance(name=data.name, category=data.category)

    @staticmethod
    def map_classifier_instance(data):
        name = data.name
        category = data.category
        keys = sorted(_configuration.analysis.classifier.metrics)

        sample = [
            data.metrics[metric]
            for metric in keys
            ]

        return _Instance(name=name, category=category, metrics=numpy.array(sample))


def process(instance_info, monitor_samples):
    _logger.debug('Importing data for instance: {}.'.format(instance_info.name))

    load_measured = compute_load(monitor_samples)

    instance = krico.core.lexicon.Lexicon({
        'instance_id': instance_info.instance_id,
        'name': instance_info.name,
        'image': instance_info.image,
        'start_time': instance_info.start_time,
        'stop_time': instance_info.stop_time,
        'host': instance_info.host,
        'flavor': instance_info.flavor,
        'category': instance_info.category,
        'parameters': instance_info.parameters,
        'load_measured': load_measured,
        'availability_zone': instance_info.availability_zone
    })

    krico.core.database.Analysis.classifier_instances.save_one({'instance_id': instance_info.instance_id}, instance)


def compute_load(monitor_samples):
    metrics_names = sorted(_configuration.analysis.classifier.metrics)

    metrics_raw = {
        metric: [
            sample.metrics[metric] for sample in monitor_samples
            ]
        for metric in metrics_names
        }

    metrics_filtered = _filter_peaks(metrics_raw)

    metrics = {
        metric: float(numpy.mean(metrics_filtered[metric]))
        for metric in metrics_names
        }
    return metrics


def _filter_peaks(metrics):
    threshold = 3.0

    metrics_filtered = {}

    for metric, metric_samples in metrics.items():
        threshold_low = numpy.percentile(metric_samples, 3) / threshold
        threshold_high = numpy.percentile(metric_samples, 97) * threshold

        metrics_filtered[metric] = filter(lambda value: threshold_low <= value <= threshold_high, metric_samples)

    return metrics_filtered
