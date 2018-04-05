import sys
import traceback


class LogFunctionCall(object):
    def __init__(self, logger):
        object.__init__(self)
        self.__logger = logger

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            call_arguments = []

            call_arguments.extend([
                str(argument) for argument in args
            ])

            call_arguments.extend([
                '{}={}'.format(argument_name, argument_value)
                for argument_name, argument_value in kwargs
            ])

            self.__logger.debug('{name}({arguments})'.format(
                name=function.__name__,
                arguments=', '.join(call_arguments)
            ))

            return_value = function(*args, **kwargs)

            self.__logger.debug('{name}() return'.format(name=function.__name__))

            return return_value

        return wrapper


def log_exception(logger):
    try:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        stack_trace = ''.join(traceback.format_tb(exception_traceback))

        logger.warn('Exception: {}({})'.format(exception_type.__name__, exception_value))
        logger.debug('Stack trace:\n{}'.format(stack_trace))

    finally:
        # circular references possible with sys.exc_info()
        exception_type = exception_value = exception_traceback = None
