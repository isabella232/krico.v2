import logging
import logging.config

import sys

import krico.core

_configuration = krico.core.configuration['logger']


def get(name):
    return logging.getLogger(name)


def initialize():
    preset = _configuration['preset']
    logger_configuration = _configuration['defaults'].copy()
    preset_configuration = _configuration['presets'][preset].copy()
    logger_configuration.update(preset_configuration)

    try:
        logging.config.dictConfig(logger_configuration.dictionary())

    except AttributeError:
        default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.DEBUG, stream=sys.stdout, format=default_format)

    _logger = get('krico.core.logger')
    _logger.info('Logging initialized.')


initialize()
