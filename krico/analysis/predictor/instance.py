import numpy

import krico.analysis.categories
import krico.analysis.predictor.normalizer

import krico.core.configuration
import krico.core.database
import krico.core.lexicon
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


def process(instance_info, instance_samples):
    _logger.info('Processing {} samples from instance {} ({})...'.format(
        len(instance_samples),
        instance_info.name, instance_info.instance_id
    ))

    requirements = _compute_requirements(instance_info, instance_samples)

    parameters = krico.analysis.categories.filter_parameters(instance_info)

    instance_data = krico.core.lexicon.Lexicon({
        'instance_id': instance_info.instance_id,
        'image': instance_info.image,

        'category': instance_info.category,
        'parameters': parameters,
        'requirements': requirements
    })

    _logger.debug('Saving instance data: {}'.format(instance_data))

    krico.core.database.Analysis.predictor_instances.save_one(
        {'instance_id': instance_data.instance_id},
        instance_data
    )


def _compute_requirements(instance_info, instance_samples):
    load_samples_raw = [
        {
            'cpu_threads': sample.metrics['cpu:time'],
            'ram_size': sample.metrics['ram:used'],
            'disk_iops': sample.metrics['disk:operations:read'] + sample.metrics['disk:operations:write'],
            'network_bandwidth': sample.metrics['network:bandwidth:send'] + sample.metrics['network:bandwidth:receive']
        }
        for sample in instance_samples
        ]

    load_samples_filtered = _filter_peaks(load_samples_raw)

    requirements_unnormalized = krico.core.lexicon.Lexicon()

    for metric in load_samples_filtered[0].keys():
        metric_samples = [
            sample[metric] for sample in load_samples_filtered
            ]

        metric_load_percentile = float(
            numpy.percentile(metric_samples, _configuration.analysis.predictor.load.percentile))
        metric_load_overhead = metric_load_percentile * (
        1.0 + float(_configuration.analysis.predictor.load.overhead) / 100.0)

        requirements_unnormalized[metric] = metric_load_overhead

    requirements_normalized = krico.analysis.predictor.normalizer.normalize(requirements_unnormalized,
                                                                            instance_info.availability_zone)

    return requirements_normalized


def _filter_peaks(samples):
    threshold_percentile = 3.0
    threshold_multiplier = 3.0

    metric_names = samples[0].keys()

    samples_by_metric = {
        metric: [
            sample[metric]
            for sample in samples
            ]
        for metric in metric_names
        }

    threshold_low = {
        metric: numpy.percentile(samples_by_metric[metric], int(round(threshold_percentile))) / threshold_multiplier
        for metric in metric_names
        }
    threshold_high = {
        metric: numpy.percentile(samples_by_metric[metric],
                                 int(round(100.0 - threshold_percentile))) * threshold_multiplier
        for metric in metric_names
        }

    samples_filtered = []

    for sample in samples:
        if all([
                                   threshold_low[metric] <= sample[metric] <= threshold_high[metric]
                                   for metric in metric_names
                                   ]):
            samples_filtered.append(sample)

    _logger.debug('Filtered out {} out of {} samples.'.format(
        len(samples) - len(samples_filtered),
        len(samples)
    ))

    return samples_filtered
