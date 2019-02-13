"""Core modules."""

import yaml

with open("/etc/krico/config.yml", 'r') as __config_file:
    configuration = yaml.load(__config_file)
