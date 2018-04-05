import flask
import traceback

import krico.core.configuration
import krico.core.logger

_logger = krico.core.logger.get(__name__)
_configuration = krico.core.configuration.root


def success(response_data):
    _logger.debug('Request successfully handled, sending response:\n{}'.format(response_data))
    return flask.jsonify(response_data), 201


def error(message):
    _logger.error(message)
    return flask.jsonify({'error': message}), 400


def request_handler(function):
    def wrapper(*args, **kwargs):
        try:
            response_data = function(*args, **kwargs)
            return success(response_data)

        except Exception as ex:
            _logger.debug('Stack trace:\n{}'.format(traceback.format_exc()))
            message = 'Exception while processing request: {}({})'.format(type(ex).__name__, ex)
            return error(message)

    return wrapper
