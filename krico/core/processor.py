import multiprocessing

import logger
import configuration

__author__ = 'tziol'

_logger = logger.get('krico.core.processor')
_configuration = configuration.root


def process(data, functor):
    _logger.info('Executing function in {} workers...'.format(_configuration.core.processor.threads))
    workers = multiprocessing.Pool(processes=_configuration.core.processor.threads)
    results = workers.map(functor, data)
    return results
