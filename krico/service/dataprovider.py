import flask

import krico.core.configuration
import krico.core.database
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get('krico.service.dataprovider')


def get_instances_alive():
    
    _logger.debug("Processing GET /instances request")
    response = {}
    
    try:
        for instance in krico.core.database.Service.instances.load_many({}):
            if instance['state'] == "running":
                instance_details = instance.dictionary()
                del instance_details['instance_id']
                metrics_from_db = list(krico.core.database.Service.monitor_samples.load_many({'instance_id': instance['instance_id']}))
                metrics = {}
                if len(metrics_from_db) > 0:
                    metrics = metrics_from_db[-1].dictionary()['metrics']
                response[instance.instance_id] = instance_details
                response[instance.instance_id]['metrics'] = metrics
        
        _logger.debug("Reply on GET request: " + str(response))
        
    except Exception as ex:
        _logger.error('Exception raised while parsing response from database (instances):')
        return flask.jsonify({
            'error': 'Processing error: {}'.format(ex)
        }), 500
        
    _logger.debug('Sending response to the client...')
    return flask.jsonify(response), 201


def get_all_workloads():
    _logger.debug("Processing GET /workloads request")
    try:
        return flask.jsonify(_configuration.dictionary()['analysis']['workloads']), 201
    except KeyError as ex:
        return flask.jsonify({'error': 'Cannot find configuration key: {}'.format(ex.message)}), 500
    


def get_workloads_with_parameters():
    response = {}
    for instance in krico.core.database.Service.workloads_list.load_many({}):
        workload_desc = instance.dictionary()
        category = workload_desc['category']
        if not category in response:
            response[category] = {}
            response[category]['parameters'] = workload_desc['parameters']
    return response
