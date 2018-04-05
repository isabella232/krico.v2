import krico.analysis.predictor.instance

import krico.core.configuration
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


def filter_parameters(workload_info):
    parameters_filtered = {}
    for parameter_name in parameters[workload_info.category]:
        if parameter_name in workload_info.parameters:
            parameters_filtered[parameter_name] = workload_info.parameters[parameter_name]
        else:
            raise KeyError('Workload parameter not specified: {}'.format(parameter_name))
    return parameters_filtered


names = [
    category.name
    for category in _configuration.analysis.workloads.categories
    ]

parameters = {
    category.name: category.parameters
    for category in _configuration.analysis.workloads.categories
    }
