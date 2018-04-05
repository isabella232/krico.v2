import signal

import krico.core.logger
import krico.core.exception

_logger = krico.core.logger.get('krico.core.executable.interrupt')


class TerminateInterrupt(BaseException):
    def __init__(self):
        BaseException.__init__(self)


class _SignalHandler(object):
    __interrupt_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)

    def __init__(self):
        object.__init__(self)
        self.__attached = False
        self.__default_handlers = {}

    def attach(self):
        if self.__attached:
            _logger.warn('Signal handler already attached.')

        else:
            for signal_number in _SignalHandler.__interrupt_signals:
                self.__default_handlers[signal_number] = signal.getsignal(signal_number)
                signal.signal(signal_number, _handle_signal)

            self.__attached = True

    def detach(self):
        if not self.__attached:
            _logger.warn('Signal handler not attached.')

        else:
            for signal_number in _SignalHandler.__interrupt_signals:
                signal.signal(signal_number, self.__default_handlers[signal_number])
                del self.__default_handlers[signal_number]

            self.__attached = False


def _handle_signal(signal_number, _):
    _logger.info('Handling signal: {}'.format(signal_number))
    raise TerminateInterrupt()


def attach():
    _handler.attach()


def detach():
    _handler.detach()


_handler = _SignalHandler()
