"""Requirements prediction component."""

import collections
from itertools import izip as zip
import keras
import numpy
import logging
import pickle
import uuid

from krico.analysis.converter import prepare_prediction_for_host_aggregate

from krico import core
from krico.core.exception import NotEnoughResourcesError, NotFoundError

from krico.database \
    import PredictorInstance, PredictorNetwork, HostAggregate, Image


log = logging.getLogger(__name__)


class _Predictor(object):
    def __init__(self, category, image):
        self.image = image
        self.category = category
        self.x_maxima = []
        self._create_model()
        self._compile_model()

    def train(self, data):
        # Save maxima needed for prediction input
        self.x_maxima = numpy.amax(data[0], axis=0)

        # Data normalization
        x = keras.utils.normalize(data[0])

        y = data[1]

        epochs = len(data[0])

        self.model.fit(
            x=x,
            y=y,
            batch_size=core.configuration['predictor']['batch_size'],
            validation_split=core.configuration
            ['predictor']['validation_split'],
            epochs=epochs
        )

    def predict(self, parameters):
        parameters = collections.OrderedDict(sorted(parameters.items()))

        # Prediction operates on matrix (ndim=2)
        data = numpy.array(parameters.values(), ndmin=2)

        # Normalize input
        data = numpy.true_divide(data, self.x_maxima)

        return self.model.predict(data)[0]

    def _create_model(self):
        input_size = len(core.PARAMETERS[self.category])
        output_size = len(core.REQUIREMENTS)

        self.model = keras.Sequential([
            keras.layers.Dense(
                input_size, input_shape=(input_size,), activation='relu'),
            keras.layers.Dense(
                int((input_size + output_size + 1) / 2), activation='relu'),
            keras.layers.Dense(output_size)
        ])

    def _compile_model(self, learning_rate=0.05, momentum=0.9):
        optimizer = keras.optimizers.SGD(learning_rate, momentum)
        self.model.compile(loss='mean_squared_error', optimizer=optimizer)
        log.info('Model compiled')


def predict(category, image, parameters,
            configuration_id=None, allocation_mode=None):
    """Predict requirements for specific workload.

    Keyword arguments:
    ------------------
    category : string
        A name of workload category.
    image : string
        A name of workload image.
    parameters : map<string,int>
        A workload parameters.
    configuration_id : string
        A name of host aggregate. If not specified, predict requirements for
        all.
    allocation_mode : string
        A allocation mode for workload.

    Returns:
    --------
    predictions : list
        A list with OpenStack flavor, information about host aggregate and
        predicted requirements.

    Example:
    -------
    >> predict('bigdata', 'krico-bigdata-hadoop', {'data': 1, 'processors': 1,
    'memory': 1, 'disk': 100})

    ```{
        'requirements': {
            'disk_iops': 195.47426
            'network_bandwidth': 28.257107,
            'ram_size': 46.33694,
            'cpu_threads': 7.6579447
        },
        'flavor': {
            'disk': 100,
            'vcpus': 8,
            'ram': 48128,
            'name': 'krico-8c-47m-100d'
        },
        'host_aggregate': {
            'disk': {u'iops': 400, u'size': 1780},
            'ram': {u'bandwidth': 42, u'size': 64},
            'cpu': {u'performance': 10, u'threads': 48}}
    }
        }```
    """
    predictor = _get_predictor(category, image)

    # Separate disk because it's only needed to prepare OpenStack flavor
    disk = parameters['disk']
    del(parameters['disk'])

    # Predict requirements
    requirements = dict(zip(
        sorted(core.configuration['predictor']['requirements']),
        predictor.predict(parameters)))

    # Get back disk because it's needed to prepare OpenStack flavor
    requirements['disk'] = disk

    aggregates = HostAggregate.get_host_aggregates(
        configuration_id)

    if not aggregates:
        raise NotFoundError('Missing host aggregate')

    predictions = []

    for aggregate in aggregates:
        prediction = \
            prepare_prediction_for_host_aggregate(
                dict(aggregate),
                requirements,
                allocation_mode)
        predictions.append(prediction)

    return predictions


def refresh():
    """Delete all predictor networks, build new and save it in database."""
    log.info('Refreshing predictors.')

    for network in PredictorNetwork.all():
        network.delete()

    for category in core.CATEGORIES:

        # First create general predictor for category
        if _enough_samples(category):
            _create_predictor(category)

        # Second create specific predictor for image
        for image in Image.get_images_names(category):

            if _enough_samples(category, image):
                _create_predictor(category, image)


def _create_predictor(category, image=None):

    learning_set = PredictorInstance.get_predictor_learning_set(
        category, image)

    # All predictors include image field, if create general predictor,
    # set this field with default_image.
    if image is None:
        image = core.configuration['predictor']['default_image']

    predictor = _Predictor(category, image)
    predictor.train(learning_set)

    PredictorNetwork.create(
        id=uuid.uuid4(),
        image=image,
        category=category,
        network=pickle.dumps(predictor)
    )

    return predictor


def _get_predictor(category, image):

    # Start with check if there's specific predictor for image
    image_predictor = PredictorNetwork.objects.filter(
        image=image,
        category=category
    ).allow_filtering().first()

    if image_predictor:
        return pickle.loads(image_predictor.network)

    # If not, check if can create
    if _enough_samples(category, image):
        return _create_predictor(category, image)

    # If not, check if there's general predictor for category
    category_predictor = PredictorNetwork.objects.filter(
        image=core.configuration['predictor']['default_image'],
        category=category
    ).allow_filtering().first()

    if category_predictor:
        return pickle.loads(category_predictor.network)

    # If not, check if can create
    if _enough_samples(category):
        return _create_predictor(category)

    # If not, raise error
    raise NotEnoughResourcesError(
        'Cannot prepare predictor for category: {} '
        'image: {}'.format(category, image))


def _enough_samples(category, image=None):

    if image is None:
        sample_count = PredictorInstance.objects.filter(
            category=category
        ).allow_filtering().count()

    else:
        sample_count = PredictorInstance.objects.filter(
            category=category,
            image=image
        ).allow_filtering().count()

    return sample_count >= core.configuration['predictor']['minimal_samples']
