import krico.core.logger

_logger = krico.core.logger.get(__name__)


class Error(RuntimeError):
    def __init__(self, message):
        RuntimeError.__init__(self, message)
        _logger.error(message)


class NotFoundError(Error):
    def __init__(self, message):
        Error.__init__(self, 'Object {} not found.'.format(message))
