import abc
import datetime
import time

import krico.core.debug
import krico.core.exception
import krico.core.timestamp
import krico.core.configuration
import krico.core.logger

import krico.core.executable.interrupt

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


class Loop(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, interval):
        object.__init__(self)
        self.__interval = interval

    def run(self):
        deadline = krico.core.timestamp.now()
        delta = datetime.timedelta(seconds=self.__interval)

        try:
            while True:
                _logger.debug('Beginning iteration...')

                now = krico.core.timestamp.now()
                while deadline <= now:
                    deadline += delta

                self._loop()

                now = krico.core.timestamp.now()
                if now < deadline:
                    time.sleep((deadline - now).total_seconds())

        except krico.core.executable.interrupt.TerminateInterrupt:
            _logger.info('Termination requested.')
            raise

        except:
            krico.core.debug.log_exception(_logger)
            raise

        finally:
            _logger.info('Teardown...')
            self._teardown()

    @abc.abstractmethod
    def _loop(self):
        raise NotImplementedError()

    def _teardown(self):
        pass
