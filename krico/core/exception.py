import logging

log = logging.getLogger(__name__)


class Error(RuntimeError):
    def __init__(self, message):
        RuntimeError.__init__(self, message)
        log.error(message)


class NotFoundError(Error):
    def __init__(self, message):
        Error.__init__(self, '{}: {}'.format(self.__repr__(), message))


class NotEnoughResourcesError(Error):
    def __init__(self, message):
        Error.__init__(self, '{}: {}'.format(self.__repr__(), message))


class DatabaseConnectionError(Error):
    def __init__(self, message):
        Error.__init__(self, '{}: {}'.format(self.__repr__(), message))
