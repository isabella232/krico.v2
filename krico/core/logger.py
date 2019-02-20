import logging
import logging.config
import sys

from krico import core


def init():
    preset = core.configuration['logger']['preset']
    logger_configuration = core.configuration['logger']['defaults'].copy()
    preset_configuration = \
        core.configuration['logger']['presets'][preset].copy()
    logger_configuration.update(preset_configuration)

    try:
        logging.config.dictConfig(logger_configuration.dictionary())

    except AttributeError:
        default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.DEBUG, stream=sys.stdout, format=default_format)

    _logger = logging.getLogger(__name__)
    _logger.info('Logging initialized.')
