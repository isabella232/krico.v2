import numpy
import random
import theanets

import krico.analysis.categories
import krico.analysis.predictor.statistics

import krico.core.configuration
import krico.core.database
import krico.core.exception
import krico.core.lexicon
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


class _PredictorNetwork(object):
    def __init__(self, predictor_data_object):
        object.__init__(self)
        self.__data = predictor_data_object

    def predict(self, inputs):
        inputs_normalized = _normalize(inputs, self.__data.inputs_maxima)
        inputs_array = _create_array([inputs_normalized])

        outputs_array = self.__data.network.data.predict(inputs_array)
        outputs_normalized = _create_dictionaries(self.__data.outputs_maxima.keys(), outputs_array)[0]
        outputs_denormalized = _denormalize(outputs_normalized, self.__data.outputs_maxima)

        return krico.core.lexicon.Lexicon(outputs_denormalized)

    @property
    def error(self):
        return self.__data.error


class NotEnoughDataError(krico.core.exception.Error):
    def __init__(self, message=None):
        krico.core.exception.Error.__init__(self, message)


class _ImageType(object):
    default = 'default'


def refresh():
    _logger.info('Refreshing all predictor networks...')

    for category in krico.analysis.categories.names:
        category_images = {
            instance.image for instance in krico.core.database.Analysis.predictor_instances.load_many({'category': category})
            }

        for image in {_ImageType.default} | category_images:
            try:
                _construct_predictor_network(category, image)

            except NotEnoughDataError:
                _logger.info(
                    'Not enough data to construct a predictor for: category={}, image={}.'.format(category, image))


def prepare(category, image):
    _logger.debug('Preparing predictor network: category={}, image={}.'.format(category, image))
    predictor_data_object = krico.core.database.Analysis.predictor_networks.load_one(
        _create_predictor_filter(category, image))

    if predictor_data_object:
        _logger.debug('Found predictor network in the database.')
        return _PredictorNetwork(predictor_data_object)

    else:
        _logger.info('Predictor network not found, constructing...')
        try:
            return _construct_predictor_network(category, image)

        except NotEnoughDataError:
            if image != _ImageType.default:
                _logger.info('Not enough data for image-specific predictor, using the general category predictor.')
                return prepare(category, _ImageType.default)
            else:
                raise


def _create_predictor_filter(category, image):
    return {
        'category': category,
        'image': image
    }


def _construct_predictor_network(category, image):
    _logger.info('Constructing predictor: category={}, image={}...'.format(category, image))

    split_training = 1.0 / 3.0
    split_validation = 1.0 / 3.0

    parameters_maxima = krico.analysis.predictor.statistics.get_parameters_maxima(category)
    requirements_maxima = krico.analysis.predictor.statistics.get_requirements_maxima()

    # loading samples, grouped by image
    instance_filter = {'category': category}
    if image != _ImageType.default:
        instance_filter['image'] = image

    samples_by_image = {}

    for instance in krico.core.database.Analysis.predictor_instances.load_many(instance_filter):
        sample_inputs = _normalize(instance.parameters, parameters_maxima)
        sample_outputs = _normalize(instance.requirements, requirements_maxima)

        if instance.image not in samples_by_image:
            samples_by_image[instance.image] = []

        samples_by_image[instance.image].append((sample_inputs, sample_outputs))

    # splitting samples into sets
    samples_training = []
    samples_validation = []
    samples_testing = []

    for image_name, image_samples in samples_by_image.items():
        random.shuffle(image_samples)

        split_index_training = int(split_training * len(image_samples) + 0.5)
        split_index_validation = int((split_training + split_validation) * len(image_samples) + 0.5)

        _logger.debug('Found {} samples for image {} (splitting: {}/{}/{}).'.format(
            len(image_samples),
            image_name,
            split_index_training,
            split_index_validation - split_index_training,
            len(image_samples) - split_index_validation
        ))

        samples_training.extend(image_samples[:split_index_training])
        samples_validation.extend(image_samples[split_index_training:split_index_validation])
        samples_testing.extend(image_samples[split_index_validation:])

    _logger.debug('Prepared sample sets: Training ({}), Validation ({}), Testing ({}).'.format(
        len(samples_training), len(samples_validation), len(samples_testing)
    ))

    # training the predictor model
    network, error = _train_network(samples_training, samples_validation, samples_testing)

    # saving the model
    predictor_data_object = krico.core.lexicon.Lexicon({
        'category': category,
        'image': image,
        'inputs_maxima': parameters_maxima,
        'outputs_maxima': requirements_maxima,
        'network': krico.core.database.BinaryObjectWrapper(network),
        'error': error
    })

    _logger.info('Saving predictor model: category={}, image={}...'.format(category, image))
    krico.core.database.Analysis.predictor_networks.save_one(
        _create_predictor_filter(category, image),
        predictor_data_object
    )

    return _PredictorNetwork(predictor_data_object)


def _train_network(samples_training, samples_validation, samples_testing):
    min_samples = 10
    max_iterations = 1e6

    # abort if not enough samples are provided
    # could add some more sophisticated heuristics if needed
    if len(samples_training) < min_samples or len(samples_validation) < min_samples:
        raise NotEnoughDataError('Not enough samples to train a network.')

    training_inputs, training_outputs = zip(*samples_training)
    validation_inputs, validation_outputs = zip(*samples_validation)

    training_set = (_create_array(training_inputs), _create_array(training_outputs))
    validation_set = (_create_array(validation_inputs), _create_array(validation_outputs))

    _logger.info('Training predictor with {} training and {} validation samples ({} total).'.format(
        len(training_inputs), len(validation_inputs), len(training_inputs) + len(validation_inputs)
    ))

    inputs_count = len(training_inputs[0])
    outputs_count = len(training_outputs[0])

    experiment = theanets.Experiment(
        theanets.Regressor,
        layers=(
            inputs_count,
            int((inputs_count + outputs_count + 1) / 2),
            outputs_count
        ))

    iteration = 0
    for training_result, validation_result in experiment.itertrain(
            training_set,
            validation_set,
            algorithm='sgd',  # consider looking into other algorithms
            learning_rate=0.05,  # default: 0.01
            momentum=0.9,  # default: 0.9
            min_improvement=1.0e-4  # default: 0.00001
    ):
        iteration += 1

        if iteration > max_iterations:
            raise krico.core.exception.Error('Learning process failed.')

        if iteration % 100 == 1:
            _logger.debug('Iteration {:7d}: Training loss = {:10.7f}, Validation loss = {:10.7f}'.format(
                iteration,
                training_result['loss'],
                validation_result['loss']
            ))

    # testing the model
    if not samples_testing:
        _logger.warning('No testing samples provided. Using the validation samples for testing.')
        samples_testing = samples_validation

    outputs = sorted(training_outputs[0].keys())

    testing_inputs, testing_outputs_actual = zip(*samples_testing)
    testing_inputs_array = _create_array(testing_inputs)
    testing_outputs_predicted_array = experiment.network.predict(testing_inputs_array)
    testing_outputs_predicted = _create_dictionaries(outputs, testing_outputs_predicted_array)

    error_cumulative = {output: 0.0 for output in outputs}

    for output_actual, output_predicted in zip(testing_outputs_actual, testing_outputs_predicted):
        for output in outputs:
            error_cumulative[output] += abs(output_predicted[output] - output_actual[output])

    error = {
        output: error_cumulative[output] / float(len(samples_testing))
        for output in outputs
        }

    _logger.info('Predictor model absolute errors:')
    for output in outputs:
        _logger.info('{:12}: {:1.4f}'.format(output, error[output]))

    return experiment.network, error


def _normalize(sample, maxima):
    return {
        key: float(sample[key]) / float(maxima[key])
        for key in sample.keys()
        }


def _denormalize(sample, maxima):
    return {
        key: float(sample[key]) * float(maxima[key])
        for key in sample.keys()
        }


def _create_array(samples):
    keys = sorted(samples[0].keys())
    return numpy.array([
                           [sample[key] for key in keys]
                           for sample in samples
                           ])


def _create_dictionaries(keys, array):
    keys_sorted = sorted(keys)

    return [
        {
            key: value
            for key, value in zip(keys_sorted, row)
            }
        for row in array
        ]
