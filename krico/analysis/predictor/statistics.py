import krico.analysis.categories

import krico.core.configuration
import krico.core.database
import krico.core.lexicon
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


class _StatisticsType(object):
    parameters_maxima = 'parameters-maxima'
    requirements_maxima = 'requirements-maxima'


def get_requirements_maxima():
    requirements_maxima_object = krico.core.database.Analysis.predictor_statistics.load_one({
        'type': _StatisticsType.requirements_maxima
    })

    if not requirements_maxima_object:
        requirements_maxima_object = _compute_requirements_maxima()

    return requirements_maxima_object.metrics


def _compute_requirements_maxima():
    requirements_per_instance = [
        instance.requirements
        for instance in krico.core.database.Analysis.predictor_instances.load_many({})
        ]

    requirements_maxima = _find_maxima(requirements_per_instance)

    requirements_maxima_object = krico.core.lexicon.Lexicon({
        'type': _StatisticsType.requirements_maxima,
        'metrics': requirements_maxima
    })

    krico.core.database.Analysis.predictor_statistics.save_one(
        {
            'type': _StatisticsType.requirements_maxima
        },
        requirements_maxima_object
    )

    return requirements_maxima_object


def get_parameters_maxima(category):
    parameters_maxima_object = krico.core.database.Analysis.predictor_statistics.load_one({
        'type': _StatisticsType.parameters_maxima,
        'category': category
    })

    if not parameters_maxima_object:
        parameters_maxima_object = _compute_parameters_maxima(category)

    return parameters_maxima_object.parameters


def _compute_parameters_maxima(category):
    parameters_per_instance = [
        instance.parameters
        for instance in krico.core.database.Analysis.predictor_instances.load_many({'category': category})
        ]

    parameters_maxima = _find_maxima(parameters_per_instance)

    parameters_maxima_object = krico.core.lexicon.Lexicon({
        'type': _StatisticsType.parameters_maxima,
        'category': category,
        'parameters': parameters_maxima
    })

    krico.core.database.Analysis.predictor_statistics.save_one(
        {
            'type': _StatisticsType.parameters_maxima,
            'category': category
        },
        parameters_maxima_object
    )

    return parameters_maxima_object


def _find_maxima(sequence):
    maxima = {}
    for item in sequence:
        for key, value in item.items():
            if key not in maxima:
                maxima[key] = value

            elif maxima[key] < value:
                maxima[key] = value

    return maxima


def refresh():
    _logger.info('Refreshing predictor statistics...')
    _compute_requirements_maxima()

    for category in krico.analysis.categories.names:
        _compute_parameters_maxima(category)
