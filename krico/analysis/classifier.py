"""Workload classification component."""

import collections
import pickle
import keras
import numpy
import logging

from krico.analysis.converter import prepare_mean_sample

from krico import core
from krico.core.exception import NotFoundError
from krico.database \
    import ClassifierInstance, Sample, ClassifierNetwork, HostAggregate

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
        y = keras.utils.to_categorical(
            y=data[1],
            num_classes=len(core.CATEGORIES)
        )

        epochs = len(data[0])

        self.model.fit(
            x=x,
            y=y,
            batch_size=core.configuration['classifier']['batch_size'],
            epochs=epochs,
            validation_split=core.configuration
            ['classifier']['validation_split']
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
        input_size = len(core.METRICS)
        output_size = len(core.CATEGORIES)

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

    samples = Sample.objects.filter(
        instance_id=instance_id).allow_filtering().all()

    configuration_id = samples.first().configuration_id

    classifier = _load_classifier(configuration_id)

    metrics = []

    for sample in samples:
        metrics.append(sample.metrics)

    mean_load = prepare_mean_sample(metrics, core.METRICS)

    prediction = classifier.predict(mean_load)

    log.info('Category predicted for {} is: {}({})'.format(
        instance_id,
        core.CATEGORIES[prediction],
        prediction
    ))

    return core.CATEGORIES[prediction]


def refresh():
    """Refresh all classifier networks."""
    log.info('Refreshing classifiers.')

    for network in ClassifierNetwork.all():
        network.delete()

    for host_aggregate in HostAggregate.get_host_aggregates():
        log.info('Refreshing classifier for "{}" host aggregate.'.format(
            host_aggregate.configuration_id))

        for category in core.CATEGORIES:

            if _enough_samples(category, host_aggregate.configuration_id):
                _create_and_save_classifier(
                    category, host_aggregate.configuration_id)

            else:
                log.warning('Not enough samples for "{}" category '
                            'in "{}" host aggregate.')


def _create_and_save_classifier(category, configuration_id):

    learning_set = ClassifierInstance.\
        get_classifier_learning_set(category, configuration_id)

    classifier = ClassifierNetwork.objects.filter(
        configuration_id=configuration_id
    ).allow_filtering().first()

    if not classifier:
        classifier = _Classifier(configuration_id)
    else:
        classifier = pickle.load(classifier.network)

    classifier.train(learning_set)

    ClassifierNetwork.create(
        configuration_id=configuration_id,
        network=pickle.dumps(classifier)
    )


def _load_classifier(configuration_id):
    classifier = ClassifierNetwork.objects.filter(
        configuration_id=configuration_id
    ).allow_filtering().first()

    if not classifier:
        classifier = ClassifierNetwork.objects.filter(
            configuration_id=core.configuration
            ['classifier']['default_configuration_id']
        ).allow_filtering().first()

    if not classifier:
        raise(NotFoundError(
            'Cannot find classifier network for "{}" configuration'.
            format(configuration_id)))

    return pickle.loads(classifier.network)


def _enough_samples(category, configuration_id):
    sample_count = ClassifierInstance.objects.filter(
        configuration_id=configuration_id,
        category=category
    ).allow_filtering().count()

    if sample_count < core.configuration['classifier']['minimal_samples']:
        return False

    return True
