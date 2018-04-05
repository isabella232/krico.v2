import krico.analysis.predictor.instance
import krico.analysis.classifier.instance

import krico.core.configuration
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


def process(instance_info, instance_samples):
    _logger.info('Processing {} samples from instance {} ({})...'.format(
        len(instance_samples),
        instance_info.name, instance_info.instance_id
    ))
    krico.analysis.classifier.instance.process(instance_info, instance_samples)
    krico.analysis.predictor.instance.process(instance_info, instance_samples)
