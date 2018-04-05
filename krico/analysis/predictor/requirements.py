import krico.analysis.categories
import krico.analysis.predictor.networks
import krico.analysis.predictor.normalizer

import krico.core.configuration
import krico.core.lexicon
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


def predict(workload_info, hardware_info):
    predictor_network = krico.analysis.predictor.networks.prepare(workload_info.category, workload_info.image)
    parameters = krico.analysis.categories.filter_parameters(workload_info)
    requirements_normalized = predictor_network.predict(parameters)
    requirements = krico.analysis.predictor.normalizer.denormalize(requirements_normalized, hardware_info)

    return requirements
