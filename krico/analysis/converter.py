"""Data converting component."""
import math
import numpy
import logging

from krico import core
from krico.core.exception import NotEnoughResourcesError

log = logging.getLogger(__name__)


def prepare_prediction_for_host_aggregate(
        aggregate,
        requirements,
        allocation='shared'):
    """Prepare prediction for host aggregate.

    Keyword arguments:
    ------------------
    aggregate : dict()
        Basic information about host aggregate. Needed fields:
            - ['cpu']['threads'] : Number of cpu threads.
            - ['ram']['size'] : Amount of RAM (in gigabytes).
            - ['disk']['size'] : Amount of disk space (in gigabytes).
            - ['configuration_id'] : Name of configuration.

    allocation : string
        Allocation mode to prepare flavor. Implemented modes:
            - 'shared'
            - 'exclusive'

    requirements : dict()
        Requirements of workload. Needed fields:
            - ['cpu_threads'] : Number of cpu threads.
            - ['ram_size'] : Required amount of RAM (in megabytes).
            - ['disk'] : Amount of disk space.

    Returns:
    --------
    prediction: dict()
        Information about prediction. Included prepared flavor, passed host
        aggregate and requirements information.
        - ['host_aggregate']['cpu'] : Cpu performance and threads.
        - ['host_aggregate']['ram'] : RAM bandwidth and size.
        - ['host_aggregate']['disk'] : Disk iops and size.
        - ['flavor']['name'] : Flavor name.
        - ['flavor']['vcpus'] : Number of virtual cpus.
        - ['flavor']['ram'] : Ram size (in megabytes).
        - ['flavor']['disk'] : Disk size.
        - ['requirements'] : Disk iops, network bandwidth, ram size,
        cpu threads required to run workload.
    """
    flavor_vcpus_max = int(
        aggregate['cpu']['threads'] *
        core.configuration['converter']['flavor']['free']['vcpus']
    )

    flavor_ram_max = int(
        aggregate['ram']['size'] *
        core.configuration['converter']['flavor']['free']['ram']
    ) * 1024

    flavor_disk_max = int(
        aggregate['disk']['size'] *
        core.configuration['converter']['flavor']['free']['disk'])

    if allocation == \
            core.configuration['converter']['allocation_mode']['shared']:
        flavor_vcpus = int(math.ceil(requirements['cpu_threads']))
        flavor_ram = int(math.ceil(requirements['ram_size'])) * 1024
        flavor_disk = int(math.ceil(requirements['disk']))

        if flavor_vcpus > flavor_vcpus_max or \
                flavor_ram > flavor_ram_max or \
                flavor_disk > flavor_disk_max:
            message = "Cannot launch VM using {} host aggregate."\
                .format(aggregate['configuration_id'])
            log.warning(message)
            raise NotEnoughResourcesError(message)

    elif allocation == \
            core.configuration['converter']['allocation_mode']['exclusive']:
        flavor_vcpus = flavor_vcpus_max
        flavor_ram = flavor_ram_max
        flavor_disk = flavor_disk_max

    else:
        message = "Cannot prepare prediction. " \
                  "Allocation mode {} is not implemented.".format(allocation)
        log.warning(message)
        raise NotImplementedError(message)

    prediction = dict()
    prediction['host_aggregate'] = dict()
    prediction['host_aggregate']['cpu'] = aggregate['cpu']
    prediction['host_aggregate']['ram'] = aggregate['ram']
    prediction['host_aggregate']['disk'] = aggregate['disk']
    prediction['flavor'] = dict()
    prediction['flavor']['name'] = 'krico-{}c-{}m-{}d'.format(
        flavor_vcpus,
        flavor_ram / 1024,
        flavor_disk
    )

    prediction['flavor']['vcpus'] = flavor_vcpus
    prediction['flavor']['ram'] = flavor_ram
    prediction['flavor']['disk'] = flavor_disk

    prediction['requirements'] = requirements

    return prediction


def prepare_mean_sample(samples, metrics):
    """Prepare mean sample needed to classification.

    Keyword arguments:
    ------------------
    samples : list of dictionaries
            List of dictionaries of metrics names and values.

    metrics : list of string
            List of metric names.

    Returns:
    --------
    metrics : dict()
            Dictionary with mean samples.
    """
    metrics_raw = {
        metric: [
            sample[metric] for sample in samples
        ]
        for metric in metrics
    }

    metric_filtered = _filter_peaks(metrics_raw)

    metrics_prepared = {
        metric: float(numpy.mean(metric_filtered[metric]))
        for metric in metrics
    }
    return metrics_prepared


def _filter_peaks(metrics):
    metrics_filtered = dict()

    for metric, metric_samples in metrics.items():
        threshold_low = numpy.percentile(
            metric_samples, core.configuration['converter']['threshold_low'])

        threshold_low = \
            threshold_low / core.configuration['converter']['threshold']

        threshold_high = numpy.percentile(
            metric_samples, core.configuration['converter']['threshold_high'])

        threshold_high = \
            threshold_high * core.configuration['converter']['threshold']

        metrics_filtered[metric] = filter(
            lambda value: threshold_low <= value <= threshold_high,
            metric_samples)

    return metrics_filtered
