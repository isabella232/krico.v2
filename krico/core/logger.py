import logging
import logging.config
import sys

from krico.core import configuration

config = configuration['logger']


def initialize():
    preset = config['preset']
    logger_configuration = config['defaults'].copy()
    preset_configuration = config['presets'][preset].copy()
    logger_configuration.update(preset_configuration)

    try:
        logging.config.dictConfig(logger_configuration.dictionary())

    except AttributeError:
        default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.DEBUG, stream=sys.stdout, format=default_format)

    _logger = logging.getLogger(__name__)
    _logger.info('Logging initialized.')
