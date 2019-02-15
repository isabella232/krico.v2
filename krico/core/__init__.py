"""Core modules."""

import yaml

configuration = dict()

# Names of workloads categories.
CATEGORIES = []

# Parameter names of workloads.
PARAMETERS = []

# Names of Virtual Machine usage metrics needed in prediction process.
REQUIREMENTS = []

# Names of Virtual Machine usage metrics needed in classification process.
METRICS = []


def init():
    with open("/etc/krico/config.yml", 'r') as __config_file:
        configuration = yaml.load(__config_file)

    CATEGORIES = sorted([
        category['name']
        for category in configuration['workloads']['categories']
    ])

    PARAMETERS = {
        category['name']: category['parameters']
        for category in configuration['workloads']['categories']
    }

    REQUIREMENTS = sorted(configuration['predictor']['requirements'])

    METRICS = sorted(configuration['classifier']['metrics'])
