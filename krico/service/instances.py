import krico.core.logger
import krico.core.timestamp

import krico.analysis.instance

_logger = krico.core.logger.get(__name__)

# TODO: This file needs to be reworked after updating old neural network with Keras and removing OS deps from model

def refresh():
    _logger.info('Refreshing instance data...')

    stop_time = krico.core.timestamp.now()
    # TODO: Refresh should probably happen for all instances
    terminated_instances = _get_terminated_instances()

    for instance in terminated_instances:
        instance.state = _InstanceState.terminated
        instance.stop_time = stop_time
        krico.core.database.Service.instances.save_one(
            {'instance_id': instance.instance_id},
            instance
        )

        if instance.category != 'unknown':
            _logger.debug(
                'Loading monitor samples for terminated instance: {} ({})'.format(instance.name, instance.instance_id))

            monitor_samples = list(
                krico.core.database.Service.monitor_samples.load_many({'instance_id': instance.instance_id}))

            if not monitor_samples:
                _logger.warn(
                    'No samples found for terminated instance: {} ({})'.format(instance.name, instance.instance_id))
            else:
                _logger.info(
                    'Found {} samples for terminated instance: {} ({})'.format(len(monitor_samples), instance.name,
                                                                               instance.instance_id))
                krico.analysis.instance.process(instance, monitor_samples)