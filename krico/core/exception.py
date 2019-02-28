import logging

log = logging.getLogger(__name__)


class Error(RuntimeError):
    def __init__(self, message):
        pass


class NotFoundError(Error):
    def __init__(self, message):
        Error.__init__(self, '{}: {}'.format(self.__repr__(), message))


class NotEnoughResourcesError(Error):
    def __init__(self, message):
        Error.__init__(self, '{}: {}'.format(self.__repr__(), message))


class DatabaseConnectionError(Error):
    def __init__(self, message):
        Error.__init__(self, '{}: {}'.format(self.__repr__(), message))


class NotEnoughMetricsError(Error):
    def __init__(self, message):
        Error.__init__(self, '{}: {}'.format(self.__repr__(), message))
