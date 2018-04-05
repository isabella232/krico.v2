import krico.analysis.predictor.networks
import krico.analysis.predictor.statistics

import krico.core.configuration
import krico.core.lexicon
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


def run():
    _logger.info('Refreshing all predictor models...')
    krico.analysis.predictor.statistics.refresh()
    krico.analysis.predictor.networks.refresh()
