import multiprocessing

import krico.core.logger
import krico.core.configuration

__author__ = 'tziol'

_logger = krico.core.logger.get('krico.core.processor')
_configuration = krico.core.configuration.root


def process(data, functor):
    _logger.info('Executing function in {} workers...'.format(_configuration.core.processor.threads))
    workers = multiprocessing.Pool(processes=_configuration.core.processor.threads)
    results = workers.map(functor, data)
    return results
