import flask

import krico.analysis.classifier

import krico.core.configuration
import krico.core.database
import krico.core.exception
import krico.core.logger

_logger = krico.core.logger.get('krico.service.classifier')
_configuration = krico.core.configuration.root


def classify():
    if not flask.request.json or 'instance_id' not in flask.request.json:
        _logger.info('Bad request format - instance_id missing.')
        flask.abort(400)

    try:
        instance_id = flask.request.json['instance_id']

        _logger.debug('Classifying instance with id: {}'.format(instance_id))

        instance = krico.core.database.Service.instances.load_one({'instance_id': instance_id})
        monitor_samples = list(krico.core.database.Service.monitor_samples.load_many({'instance_id': instance_id}))

        category = krico.analysis.classifier.classify(instance, monitor_samples)
        predicted_category = krico.analysis.categories.names[category]

        # Save classified_as information in database
        instance.classified_as = predicted_category
        krico.core.database.Service.instances.save_one({'instance_id': instance_id}, instance)

        _logger.info('Instance classified as: {}'.format(predicted_category))

    except Exception as ex:
        return flask.jsonify({
            'error': 'Processing classify error: {}'.format(ex)
        }), 500

    return flask.jsonify({'predicted_category': predicted_category}), 201
