import krico.core.cloud.client
import krico.core.configuration
import krico.core.database
import krico.core.exception
import krico.core.lexicon
import krico.core.logger

import krico.analysis.hosts

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


# TODO: This file needs to be reworked after updating old neural network with Keras and removing OS deps from model


def setup():
    _logger.info('Setting up host aggregates...')

    _delete_krico_aggregates()

    try:
        global_metadata = _configuration.service.zones.metadata.dictionary()

    except AttributeError:
        global_metadata = {}

    hosts = list(krico.core.database.Service.monitor_hosts.load_many({}))
    clusters = krico.analysis.hosts.clusterize(hosts)

    for cluster in clusters:
        aggregate_metadata = {
            'krico_priority': '1',
            'krico_configuration_id': cluster.configuration_id,
            'krico_cpu_threads': str(cluster.cpu_threads),
            'krico_cpu_performance': str(cluster.cpu_performance),
            'krico_ram_size': str(cluster.ram_size),
            'krico_ram_bandwidth': str(cluster.ram_bandwidth),
            'krico_disk_size': str(cluster.disk_size),
            'krico_disk_iops': str(cluster.disk_iops)
        }
        aggregate_metadata.update(global_metadata)

        _logger.info('Creating aggregate: {}'.format(cluster.configuration_id))
        _logger.info('Hosts: {}'.format(cluster.hosts))
        _logger.info('Metadata:\n{}'.format(aggregate_metadata))

        krico.core.cloud.client.default.aggregates.assure(
            cluster.configuration_id,
            cluster.hosts,
            availability_zone=None,
            metadata=aggregate_metadata
        )


def find(zone_name=None):
    if zone_name:
        _logger.debug('Looking for host aggregates in zone: {}'.format(zone_name))
    else:
        _logger.debug('Looking for host aggregates in all zones')

    aggregates = []
    for aggregate in krico.core.cloud.client.default.aggregates.find_all():
        if _is_krico_aggregate(aggregate) and (aggregate.availability_zone == zone_name or not zone_name):
            new_aggregate = _construct_aggregate_info(aggregate)
            aggregates.append(new_aggregate)

    if not aggregates:
        raise krico.core.exception.Error('No host aggregates found for zone {}!'.format(zone_name))

    aggregates.sort(key=lambda aggregate: aggregate.priority, reverse=True)
    return aggregates        


def _is_krico_aggregate(aggregate):
    return 'krico_priority' in aggregate.metadata


def _construct_aggregate_info(aggregate):
    return krico.core.lexicon.Lexicon({
        'name': aggregate.name,
        'availability_zone': aggregate.metadata['availability_zone'],
        'priority': float(aggregate.metadata['krico_priority']),
        'configuration_id': aggregate.metadata['krico_configuration_id'],
        'cpu': {
            'threads': int(aggregate.metadata['krico_cpu_threads']),
            'performance': float(aggregate.metadata['krico_cpu_performance'])
        },
        'ram': {
            'size': float(aggregate.metadata['krico_ram_size']),
            'bandwidth': float(aggregate.metadata['krico_ram_bandwidth'])
        },
        'disk': {
            'size': float(aggregate.metadata['krico_disk_size']),
            'iops': float(aggregate.metadata['krico_disk_iops'])
        }
    })


def _delete_krico_aggregates():
    _logger.info('Deleting all KRICO host aggregates...')
    for aggregate in krico.core.cloud.client.default.aggregates.find_all():
        if _is_krico_aggregate(aggregate):
            _logger.debug('Deleting aggregate {}...'.format(aggregate.name))
            krico.core.cloud.client.default.aggregates.delete(aggregate)
