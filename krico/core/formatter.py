import re
import yaml


def pretty(dictionary):
    text = yaml.dump(dictionary, default_flow_style=False)

    return re.sub(r'!!python/\w*:?', '', text)
