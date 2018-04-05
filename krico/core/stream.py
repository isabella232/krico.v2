import contextlib
import logging
import sys


class _StreamWrapper(object):
    def __init__(self, stream):
        object.__init__(self)
        self.__stream = stream

    def reset(self, stream):
        old_stream = self.__stream
        self.__stream = stream
        return old_stream

    def __getattr__(self, item):
        return getattr(self.__stream, item)


class LoggingHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self, stream=_stream)


_stream = _StreamWrapper(sys.stdout)


def reset(stream):
    return _stream.reset(stream)


@contextlib.contextmanager
def output_redirector(stream):
    old_stdout = sys.stdout
    sys.stdout = stream

    old_stderr = sys.stderr
    sys.stderr = stream

    old_stream = reset(stream)

    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        reset(old_stream)
