"""Metrics importer module."""
import logging

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4

from krico import core
from krico.core.exception import NotEnoughMetricsError, NotFoundError
from krico.database import\
    HostAggregate, ClassifierInstance, Host, Flavor, PredictorInstance, \
    Sample, Image

METRIC_NAMES_MAP = {
    'cputime': 'cpu:time',
    'memory/rss': 'ram:used',
    'cache-references': 'cpu:cache:references',
    'cache-misses': 'cpu:cache:misses',
    'rdbytes': 'disk:bandwidth:read',
    'wrbytes': 'disk:bandwidth:write',
    'rdreq': 'disk:operations:read',
    'wrreq': 'disk:operations:write',
    'txbytes': 'network:bandwidth:send',
    'rxbytes': 'network:bandwidth:receive',
    'txpackets': 'network:packets:send',
    'rxpackets': 'network:packets:receive'
}

CPU_TIME_SCALE = 1.0e9  # ns -> s
RAM_USED_SCALE = 1024.0 ** 2.0  # kB -> GB
BANDWIDTH_SCALE = 1024.0 ** 2.0  # B -> MB


log = logging.getLogger(__name__)


class Metrics(Model):
    """Cassandra model that's represents metric from SWAN.

    Variables:
    ------------------
    ns: Namespace of metric.

    ver: Collector plugin version.

    disk: Host name.

    time: Time when metric was collected.

    boolval: Boolean value of metric.

    doubleval: Double value of metric.

    strval: String value of metric.

    tags: Tags in <key,value>.

    valtype: Value type of metric."""

    ns = columns.Text(partition_key=True)
    ver = columns.Integer(partition_key=True)
    host = columns.Text(partition_key=True)
    time = columns.DateTime(partition_key=True)
    boolval = columns.Boolean()
    doubleval = columns.Double()
    strval = columns.Text()
    tags = columns.Map(columns.Text(), columns.Text())
    valtype = columns.Text()

    @staticmethod
    def get_by_experiment_id(experiment_id):
        """Return metrics from experiment.

        Keyword arguments:
        ------------------
        experiment_id : string
            Experiment id.

        Returns:
        --------
        host_aggregates: list of Metric objects."""

        return Metrics.objects().filter(
            tags__contains=experiment_id
        ).allow_filtering().limit(None)


def _get_parameters(metric, category):
    parameters = {}

    for param in core.PARAMETERS[category]:
        try:
            parameters[param] = float(metric.tags[param])
        except KeyError:
            raise NotFoundError(
                'Parameter "{}" for metric "{}" not found!'.
                format(param, metric.ns))

    return parameters


def _remap_metrics_names(metrics):

    for old_key in metrics.keys():
        for map_key in METRIC_NAMES_MAP.keys():
            if map_key in old_key:
                new_key = METRIC_NAMES_MAP[map_key]
                metrics[new_key] = metrics.pop(old_key)
                break

    return metrics


def _get_requirements(metrics):
    return {
        'cpu_threads': metrics['cpu:time'],
        'ram_size': metrics['ram:used'],
        'disk_iops':
            metrics['disk:operations:read'] +
            metrics['disk:operations:write'],
        'network_bandwidth':
            metrics['network:bandwidth:send'] +
            metrics['network:bandwidth:receive']
    }


def _prepare_resource_usage(metric_batch_size, batch_count, metrics):
    resource_usage = {}

    # Metrics from SWAN are wrote in batches.
    # Example: [m1,m1,m1,m2,m2,m2,m3,m3,m3]
    for i in range(0, metric_batch_size):
        key = metrics[i*batch_count].ns
        resource_usage[key] = list()

    for metric in metrics:
        resource_usage[metric.ns].append(metric.doubleval)

    return resource_usage


def _transform_cpu_time(metric, prev):
    return (prev - metric) / (CPU_TIME_SCALE * core.INTERVAL)


def _transform_ram_used(metric, prev):
    return metric / RAM_USED_SCALE


def _transform_bandwidth(metric, prev):
    return (prev - metric) / (BANDWIDTH_SCALE * core.INTERVAL)


def _transform_prev(metric, prev):
    return (prev - metric) / core.INTERVAL


def _transform_interval(metric, prev):
    return metric / core.INTERVAL


def _transform_metric(metric, key, prev):

    metric_transform_map = {
        'cpu:time': _transform_cpu_time,
        'ram:used': _transform_ram_used,
        'cpu:cache:references': _transform_interval,
        'cpu:cache:misses': _transform_interval,
        'disk:bandwidth:read': _transform_bandwidth,
        'disk:bandwidth:write': _transform_bandwidth,
        'disk:operations:read': _transform_prev,
        'disk:operations:write': _transform_prev,
        'network:bandwidth:send': _transform_bandwidth,
        'network:bandwidth:receive': _transform_bandwidth,
        'network:packets:send': _transform_prev,
        'network:packets:receive': _transform_prev
    }

    return metric_transform_map[key](metric, prev)


def _transform_resource_usage(usage, length):

    prev_usage = {}
    transformed_usage = {}

    for key in usage.keys():
        transformed_usage[key] = list()
        prev_usage[key] = usage[key][0]

    for i in range(1, length):

        for key in prev_usage.keys():
            transformed_metric = _transform_metric(usage[key][i],
                                                   key,
                                                   prev_usage[key])
            transformed_usage[key].append(transformed_metric)
            prev_usage[key] = usage[key][i]

    return transformed_usage


def import_metrics_from_swan_experiment(experiment_id):
    """Insert metric from SWAN experiment.

    Keyword arguments:
    ------------------
    experiment_id : string
        Experiment id."""

    # Get metric query.
    metrics = Metrics.get_by_experiment_id(experiment_id)

    # Check metrics.
    metric_count = metrics.count()
    metric_batch_size = len(core.METRICS)

    try:
        _check_metrics(metric_count, metric_batch_size)
    except NotEnoughMetricsError as e:
        log.error('For experiment "{0}": {1}'.format(experiment_id, e.message))
        return

    # Count batch number.
    batch_count = int(metric_count) / metric_batch_size

    # Gather information from first metric.
    metric = metrics.first()

    try:
        category = metric.tags['category']
        name = metric.tags['name']
        configuration_id = metric.tags['host_aggregate_configuration_id']
        parameters = _get_parameters(metric, category)
        host_aggregate = Host(
            name=metric.tags['host_aggregate_name'],
            configuration_id=metric.tags[
                'host_aggregate_configuration_id'],
            disk={
                'iops':
                    int(metric.tags['host_aggregate_disk_iops']),
                'size':
                    int(metric.tags['host_aggregate_disk_size'])
            },
            ram={
                'bandwidth':
                    int(metric.tags['host_aggregate_ram_bandwidth']),
                'size':
                    int(metric.tags['host_aggregate_ram_size'])
            },
            cpu={
                'performance':
                    int(metric.tags['host_aggregate_cpu_performance']),
                'threads':
                    int(metric.tags['host_aggregate_cpu_threads'])
            }
        )
        flavor = Flavor(
            vcpus=int(metric.tags['flavor_vcpus']),
            disk=int(metric.tags['flavor_disk']),
            ram=int(metric.tags['flavor_ram']),
            name=metric.tags['flavor_name']
        )
        image = metric.tags['image']
        host = metric.host
        instance_id = metric.tags['instance_id']
    except KeyError as e:
        raise NotFoundError(
            'No basic parameters found: {}'.format(e.message))

    # Save host aggregate information.
    HostAggregate(
        name=host_aggregate.name,
        configuration_id=host_aggregate.configuration_id,
        cpu=host_aggregate.cpu,
        ram=host_aggregate.ram,
        disk=host_aggregate.disk
    ).save()

    # Get metrics.
    resource_usage = _prepare_resource_usage(
        metric_batch_size, batch_count, metrics)

    # Change metrics names from SNAP to KRICO standards.
    _remap_metrics_names(resource_usage)

    # Transform metrics.
    resource_usage = _transform_resource_usage(resource_usage, batch_count)

    # Skip one metric row because of transformation.
    batch_count = batch_count - 1

    # Fill database.
    for i in range(0, batch_count):

        # Calculate resources usage.
        usage = {}
        for name in METRIC_NAMES_MAP.values():
            usage[name] = resource_usage[name][i]

        ClassifierInstance(
            id=uuid4(),
            category=category,
            name=name,
            configuration_id=configuration_id,
            parameters=parameters,
            host_aggregate=host_aggregate,
            flavor=flavor,
            image=image,
            host=host,
            instance_id=instance_id,
            resource_usage=usage
        ).save()

        PredictorInstance(
            id=uuid4(),
            image=image,
            category=category,
            parameters=parameters,
            requirements=_get_requirements(usage),
            instance_id=instance_id
        ).save()

        Image(
            image=image,
            category=category
        ).save()


def _check_metrics(metric_count, metric_batch_size):
    # Check if metrics are available.
    if metric_count <= 0:
        raise NotEnoughMetricsError("No metrics found!")

    # Check if there are available all batches with metrics.
    if metric_count % metric_batch_size != 0:
        raise NotEnoughMetricsError(
            "Not all batches with metrics are available!")


def import_samples_from_swan_experiment(experiment_id):
    """Insert samples from SWAN experiment.

    Keyword arguments:
    ------------------

        experiment_id : string
            Experiment id."""

    # Get metric query.
    metrics = Metrics.get_by_experiment_id(experiment_id)

    # Check metrics.
    metric_count = metrics.count()
    metric_batch_size = len(core.METRICS)

    try:
        _check_metrics(metric_count, metric_batch_size)
    except NotEnoughMetricsError as e:
        log.error('For experiment "{0}": {1}'.format(experiment_id, e.message))
        return

    # Count batch number.
    batch_count = int(metric_count) / metric_batch_size

    # Gather information from first metric.
    metric = metrics.first()

    try:
        instance_id = metric.tags['instance_id']
        configuration_id = metric.tags['host_aggregate_configuration_id']
    except KeyError as e:
        raise NotFoundError(
            'No basic parameters found: {}'.format(e.message))

    # Get metrics.
    resource_usage = _prepare_resource_usage(
        metric_batch_size, batch_count, metrics)

    # Change metrics names from SNAP to KRICO standards.
    _remap_metrics_names(resource_usage)

    # Fill database.
    for i in range(0, batch_count):
        # Calculate resources usage.
        usage = {}
        for name in METRIC_NAMES_MAP.values():
            usage[name] = resource_usage[name][i]

        Sample(
            id=uuid4(),
            instance_id=instance_id,
            configuration_id=configuration_id,
            metrics=usage
        ).save()
