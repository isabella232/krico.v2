"""Metrics importer module."""

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4

from krico import core
from krico.core.exception import NotEnoughResourcesError
from krico.database import\
    HostAggregate, ClassifierInstance, Host, Flavor, PredictorInstance

METRIC_NAMES_MAP = {
    'cputime': 'cpu:time',
    'memory/rss': 'ram:used',
    'cache-references': 'cpu:cache:references',
    'cache-misses': 'cpu:cache:misses',
    'wrbytes': 'disk:bandwidth:read',
    'rdbytes': 'disk:bandwidth:write',
    'wrreq': 'disk:operations:read',
    'rdreq': 'disk:operations:write',
    'txbytes': 'network:bandwidth:send',
    'rxbytes': 'network:bandwidth:receive',
    'txpackets': 'network:packets:send',
    'rxpackets': 'network:packets:receive'
}


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
        ).allow_filtering()


def _get_parameters(metric):
    parameters = {}

    for param in core.PARAMETERS[metric.tags['category']]:
        parameters[param] = metric.tags[param]

    return parameters


def _change_keys(metrics):

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


def import_from_swan_experiment(experiment_id):
    """Insert metric from SWAN experiment.

    Keyword arguments:
    ------------------
    experiment_id : string
        Experiment id."""

    # Get metric query.
    metrics = Metrics.get_by_experiment_id(experiment_id)
    metric_count = metrics.count()

    # Check if metrics are available.
    if metric_count <= 0:
        raise NotEnoughResourcesError(
            "No metrics found for experiment: {0}".format(experiment_id)
        )

    # Count batch number.
    metric_batch_size = len(core.METRICS)
    batch_count = int(metric_count) / metric_batch_size

    # Check if there are available all batches with metrics.
    if batch_count * metric_batch_size != metric_count:
        raise NotEnoughResourcesError(
            "Not all batches with metrics are available!"
        )

    # Save host aggregate from first metric.
    metric = metrics.first()

    HostAggregate(
        configuration_id=metric.tags['host_aggregate_configuration_id'],
        name=metric.tags['host_aggregate_name'],
        disk={
            'iops': metric.tags['host_aggregate_disk_iops'],
            'size': metric.tags['host_aggregate_disk_size']
        },
        ram={
            'bandwidth': metric.tags['host_aggregate_ram_bandwidth'],
            'size': metric.tags['host_aggregate_ram_size']
        },
        cpu={
            'performance': metric.tags['host_aggregate_cpu_performance'],
            'threads': metric.tags['host_aggregate_cpu_threads']
        }
    ).save()

    # Save metrics.
    classifier_instances = []
    predictor_instances = []
    load_measured = {}
    iter_counter = 0

    for i in range(0, metric_batch_size):
        key = metrics[i*batch_count].ns
        load_measured[key] = list()

    for metric in metrics:

        load_measured[metric.ns].append(metric.doubleval)

        if iter_counter % metric_batch_size == 0:
            classifier_instances.append(ClassifierInstance(
                id=uuid4(),
                category=metric.tags['category'],
                name=metric.tags['name'],
                configuration_id=metric.tags[
                    'host_aggregate_configuration_id'],
                parameters=_get_parameters(metric),
                host_aggregate=Host(
                    name=metric.tags['host_aggregate_name'],
                    configuration_id=metric.tags[
                        'host_aggregate_configuration_id'],
                    disk={
                        'iops':
                            metric.tags['host_aggregate_disk_iops'],
                        'size':
                            metric.tags['host_aggregate_disk_size']
                    },
                    ram={
                        'bandwidth':
                            metric.tags['host_aggregate_ram_bandwidth'],
                        'size':
                            metric.tags['host_aggregate_ram_size']
                    },
                    cpu={
                        'performance':
                            metric.tags['host_aggregate_cpu_performance'],
                        'threads':
                            metric.tags['host_aggregate_cpu_threads']
                    }
                ),
                flavor=Flavor(
                    vcpus=metric.tags['flavor_vcpus'],
                    disk=metric.tags['flavor_disk'],
                    ram=metric.tags['flavor_ram'],
                    name=metric.tags['flavor_name']
                ),
                image=metric.tags['image'],
                host=metric.host,
                instance_id=metric.tags['instance_id'],
            ))

            predictor_instances.append(PredictorInstance(
                id=uuid4(),
                image=metric.tags['image'],
                instance_id=metric.tags['name'],
                category=metric.tags['category'],
                parameters=_get_parameters(metric)
            ))

        iter_counter += 1

    # Change metric names from SNAP to KRICO standards.
    _change_keys(load_measured)

    # Fill database.
    for i in range(0, batch_count-1):
        for name in METRIC_NAMES_MAP.values():
            classifier_instances[i].load_measured[name] =\
                load_measured[name][i]

        classifier_instances[i].save()

        predictor_instances[i].requirements = _get_requirements(
            classifier_instances[i].load_measured
        )
        predictor_instances[i].save()
