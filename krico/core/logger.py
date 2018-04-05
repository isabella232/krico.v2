import sys
import logging
import logging.config

import krico.core.configuration

_configuration = krico.core.configuration.root


def get(name):
    return logging.getLogger(name)


def initialize():
    preset = _configuration.core.logger.preset
    logger_configuration = _configuration.core.logger.defaults.copy()
    preset_configuration = _configuration.core.logger.presets[preset].copy()
    logger_configuration.update(preset_configuration)

    try:
        logging.config.dictConfig(logger_configuration.dictionary())

    except AttributeError:
        default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format=default_format)

    _logger = get('krico.core.logger')
    _logger.info('Logging initialized.')


initialize()
