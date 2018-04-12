import os
import re
import sys
import yaml

import krico.core.lexicon
import krico.core.trait
import krico.core.attribute


class ConfigurationError(RuntimeError):
    def __init__(self, message=None):
        RuntimeError.__init__(self, message)


def _load_configuration():
    # default configuration
    configuration_root = krico.core.lexicon.Lexicon(
        {'core.environment.configuration': '/etc/krico'},
        name='krico'
    )

    # commandline configuration overrides everything everywhere always
    _commandline_configuration = _parse_commandline()
    configuration_root.update(_commandline_configuration)

    configuration_path = configuration_root.core.environment.configuration

    configuration_root.update(load(configuration_path))

    # override once again
    configuration_root.update(_commandline_configuration)

    return configuration_root


def _parse_commandline():
    options = {}
    positional = []

    for option in sys.argv[1:]:
        if option.startswith('--'):
            option_tokens = option[2:].split('=')
            key = option_tokens[0]
            value = _parse_value(option_tokens[1]) if len(option_tokens) > 1 else True

            options[key] = value
        else:
            positional.append(_parse_value(option))

    options['commandline.options.positional'] = positional

    return krico.core.lexicon.Lexicon(options, 'commandline')


def _parse_value(string):
    if string in ['True', 'true']:
        return True
    elif string in ['False', 'false']:
        return False
    else:
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return string


def load(path):
    """
    Loads a lexicon hierarchy from a directory of yaml files.
    :param path: path to a directory of yaml files
    :return: a lexicon representation of the yaml directory
    """
    yaml_lexicon = _load_directory(path)
    _resolve(yaml_lexicon)

    return yaml_lexicon


def _load_directory(path):
    yaml_lexicon = krico.core.lexicon.Lexicon()

    for file_name in os.listdir(path):
        if not file_name.startswith('.'):  # skipping hidden files
            file_path = os.path.join(path, file_name)

            if os.path.isdir(file_path):
                subsection_name = file_name
                subsection_data = _load_directory(file_path)

            elif os.path.isfile(file_path) and file_name.endswith('.yml'):
                subsection_name = os.path.splitext(os.path.basename(file_name))[0]
                subsection_data = _load_file(file_path)

            else:
                raise ConfigurationError('Unsupported file in the configuration tree: {}'.format(file_path))

            yaml_lexicon[subsection_name] = subsection_data

    return yaml_lexicon


def _load_file(path):
    with open(path, 'r') as yaml_file:
        yaml_text = yaml_file.read()
        items = yaml.load(yaml_text)

        return krico.core.lexicon.Lexicon(items)


def _resolve(yaml_lexicon):
    """
    We support reference value tags in the form of: <some.field>
    Modifies the current lexicon (i.e. does not make a copy).
    :param yaml_lexicon: a lexicon to resolve references
    :return: nothing at all
    """
    for key, value in yaml_lexicon.items():
        yaml_lexicon[key] = _resolve_value(yaml_lexicon, value)


def _resolve_value(yaml_lexicon, value):
    if krico.core.trait.is_instance(value, krico.core.lexicon.Lexicon):
        # recurse into the inner lexicon
        _resolve(value)
        return value

    elif krico.core.trait.is_instance(value, list):
        # resolve every item of the list
        return [_resolve_value(yaml_lexicon, v) for v in value]

    else:
        tmp_value = value

        while krico.core.trait.is_instance(tmp_value, str):
            # resolve all tags in the string

            if _resolve_whole_pattern.match(tmp_value):
                # whole value is a reference tag
                resolved_value = _resolve_tag(yaml_lexicon, tmp_value)

            else:
                # look for reference tags in the value
                resolved_value = _resolve_pattern.sub(
                    lambda match: str(_resolve_tag(yaml_lexicon, match.group(0))),
                    tmp_value
                )

            if resolved_value != tmp_value:
                tmp_value = resolved_value

            else:
                # everything resolved
                break

        return tmp_value


def _resolve_tag(yaml_lexicon, tag):
    key = tag[1:-1].strip()
    return yaml_lexicon[key]


_resolve_pattern = re.compile(r'<[^>]+>')
_resolve_whole_pattern = re.compile(r'^<[^>]+>$')

root = _load_configuration()
