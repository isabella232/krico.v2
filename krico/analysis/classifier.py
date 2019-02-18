"""Workload classification component."""

import collections
import pickle
import uuid
import keras
import numpy
import logging

from krico.analysis.converter import prepare_mean_sample

from krico.core import configuration as config, METRICS, CATEGORIES

from krico.database \
    import ClassifierInstance, MonitorSample, ClassifierNetwork, HostAggregate

log = logging.getLogger(__name__)


class _Classifier(object):
    def __init__(self, configuration_id):
        self.configuration_id = configuration_id
        self.x_maxima = []
        self._create_model()
        self._compile_model()

    def train(self, data):
        # Save maxima needed for prediction input
        self.x_maxima = numpy.amax(data[0], axis=0)

        # Data normalization
        x = keras.utils.normalize(data[0])

        # Convert y for categorical_crossentropy loss function
        y = keras.utils.to_categorical(data[1])

        epochs = len(data[0])

        self.model.fit(
            x=x,
            y=y,
            batch_size=config['classifier']['batch_size'],
            epochs=epochs,
            validation_split=config['classifier']['validation_split']
        )

    def predict(self, sample):
        sample = collections.OrderedDict(sorted(sample.items()))

        # Prediction operates on matrix (ndim=2)
        sample = numpy.array(sample.values(), ndmin=2)

        # Normalize input
        sample = numpy.true_divide(sample, self.x_maxima)

        # Return best prediction
        return numpy.argmax(self.model.predict(sample))

    def _create_model(self):
        input_size = len(METRICS)
        output_size = len(CATEGORIES)

        self.model = keras.Sequential([
            keras.layers.Dense(
                input_size,
                input_shape=(input_size,),
                activation='softmax'
            ),
            keras.layers.Dense(18, activation='sigmoid'),
            keras.layers.Dense(output_size, activation='softmax')
        ])

    def _compile_model(self, learning_rate=0.01, momentum=0.9, decay=1e-4):
        optimizer = keras.optimizers.SGD(learning_rate, momentum, decay)
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=optimizer,
            metrics=['accuracy']
        )
        log.info('Model compiled')


def classify(instance_id):
    """Predict requirements for specific workload.

    Keyword arguments:
    ------------------
    instance_id : string
        A name of instance.

    Returns:
    --------
    category: string
        A predicted category for workload.

    Example:
    -------
    >> classify('my_instance')

    bigdata
    """
    instance = ClassifierInstance.objects.filter(
        instance_id=instance_id).allow_filtering().first()

    monitor_samples = MonitorSample.objects.filter(
        instance_id=instance_id.host_aggregate.configuration_id).all()

    classifier = _load_classifier(instance.host_aggregate.configuration_id)

    mean_load = prepare_mean_sample(monitor_samples, METRICS)

    prediction = classifier.predict(mean_load)

    log.info('Category predicted for {} is: {}({})'.format(
        instance.instance_id,
        CATEGORIES[prediction],
        prediction
    ))

    return CATEGORIES[prediction]


def refresh():
    """Refresh all classifier networks."""
    log.info('Refreshing classifiers.')

    for network in ClassifierNetwork.all():
        network.delete()

    for host_aggregate in HostAggregate.get_host_aggregates():
        if _enough_samples(host_aggregate.configuration_id):
            _create_and_save_classifier(host_aggregate.configuration_id)


def _create_and_save_classifier(configuration_id):

    learning_set = ClassifierInstance.\
        get_classifier_learning_set(configuration_id)

    classifier = _Classifier(configuration_id)
    classifier.train(learning_set)

    ClassifierNetwork.create(
        id=uuid.uuid4(),
        configuration_id=configuration_id,
        network=pickle.dumps(classifier)
    )


def _load_classifier(configuration_id):
    classifier = ClassifierNetwork.objects.filter(
        configuration_id=configuration_id
    ).allow_filtering().first()

    if not classifier:
        classifier = ClassifierNetwork.objects.filter(
            configuration_id=config['classifier']['default_configuration_id']
        ).allow_filtering().first()

    return pickle.loads(classifier.network)


def _enough_samples(configuration_id):
    for category in CATEGORIES:

        sample_count = ClassifierInstance.objects.filter(
            configuration_id=configuration_id,
            category=category
        ).allow_filtering().count()

        if sample_count < config['classifier']['minimal_samples']:
            return False

    return True
