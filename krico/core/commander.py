__author__ = 'tziol'

import krico.core.logger
import krico.core.configuration

_logger = krico.core.logger.get('krico.core.commander')
_configuration = krico.core.configuration.root


class CommandDispatcher(object):
    @staticmethod
    def is_dispatcher(cls):
        return isinstance(cls, type) and issubclass(cls, CommandDispatcher)

    @classmethod
    def commands(cls):
        class_attributes = dir(cls)
        base_attributes = dir(CommandDispatcher)

        attributes = {
            attribute.replace('_', '-'): getattr(cls, attribute)
            for attribute in class_attributes
            if not attribute.startswith('_')
            and attribute not in base_attributes
            }

        return [
            attribute_name
            for attribute_name, attribute in attributes.items()
            if (CommandDispatcher.is_dispatcher(attribute) or callable(attribute))
            ]

    @classmethod
    def dispatch(cls, options):
        if options:
            option = options.pop(0).replace('-', '_')
            _logger.debug('Handling command: {}'.format(option))

            if hasattr(cls, option):
                attribute = getattr(cls, option)

                if CommandDispatcher.is_dispatcher(attribute):
                    attribute.dispatch(options)
                    return

                elif callable(attribute):
                    attribute(*options)
                    return
                # method_to_call = getattr('krico.launcher.main', 'test')
                # result = method_to_call()

            print '[ERROR] Unkown command: {}'.format(option)

        print 'Need one of the following commands:'

        for command in cls.commands():
            print '\t', command

    @classmethod
    def dispatch_commandline(cls):
        options = list(_configuration.commandline.options.positional)
        cls.dispatch(options)

    @classmethod
    def complete(cls, *options):
        if options:
            options_list = list(options)
            option = options_list.pop(0)

            if len(options_list) == 0:
                if option == 'ALL':
                    cls.__complete_commands()
                else:
                    cls.__complete_commands(option)

            elif hasattr(cls, option):
                attribute = getattr(cls, option)

                if CommandDispatcher.is_dispatcher(attribute):
                    attribute.complete(*options_list)

    @classmethod
    def __complete_commands(cls, prefix=None):
        commands = cls.commands()
        if prefix:
            commands = [command for command in commands if command.startswith(prefix)]

        for command in commands:
            print command
