"""Core modules."""
from krico.core.exception import NotFoundError

from yaml import load

configuration = {}

# Names of workloads categories.
CATEGORIES = []

# Parameter names of workloads.
PARAMETERS = []

# Names of Virtual Machine usage metrics needed in prediction process.
REQUIREMENTS = []

# Names of Virtual Machine usage metrics needed in classification process.
METRICS = []

INTERVAL = 0


def init(config_path):
    """Loads KRICO configuration.

    Keyword arguments:
    ------------------
    config_path : string
        Path to configuration file."""

    try:
        with open(config_path, 'r') as config_file:
            global configuration
            configuration = load(config_file)
    except IOError:
        raise NotFoundError(
            "Missing config file \"{}\"".format(config_path)
        )

    global CATEGORIES
    CATEGORIES = sorted([
        category['name']
        for category in configuration['workloads']['categories']
    ])

    global PARAMETERS
    PARAMETERS = {
        category['name']: category['parameters']
        for category in configuration['workloads']['categories']
    }

    global REQUIREMENTS
    REQUIREMENTS = sorted(configuration['predictor']['requirements'])

    global METRICS
    METRICS = sorted(configuration['classifier']['metrics'])

    global INTERVAL
    INTERVAL = int(configuration['metric']['interval'])

    return configuration
