import krico.core.configuration
import krico.core.exception
import krico.core.logger

__author__ = 'porzech'

_logger = krico.core.logger.get('krico.analysis.classifier.dataprovider')
_configuration = krico.core.configuration.root


def get_max_metrics_values(configuration_id=None):
    _logger.debug('Getting maximal values of metrics {}.'.format(configuration_id))

    filters = list()

    group_filter = {
        '$group': {
            '_id': '$availability_zone.configuration_id'
        }
    }

    for metric in _configuration.analysis.classifier.metrics:
        group_filter['$group'][metric] = {'$max': '$load_measured.{}'.format(metric)}

    if configuration_id:
        match_filter = {
            '$match': {
                'availability_zone.configuration_id': {
                    '$eq': configuration_id
                }
            }
        }
        filters.append(match_filter)

    filters.append(group_filter)

    if configuration_id:
        return list(krico.core.database.Analysis.classifier_instances.aggregate(filters))[0]

    return list(krico.core.database.Analysis.classifier_instances.aggregate(filters))


def count_instances_for_configuration_by_category(configuration_id):
    _logger.debug('Count instances for configuration {}'.format(configuration_id))

    filters = list()

    if not configuration_id:
        raise krico.core.exception.Error('Configuration id could not be None.')

    filters.append({
        '$match': {
            'availability_zone.configuration_id': {
                '$eq': configuration_id
            }
        }
    })
    filters.append({
        '$group': {
            '_id': '$category',
            'count': {
                '$sum': 1
            }
        }
    })

    return list(krico.core.database.Analysis.classifier_instances.aggregate(filters))
