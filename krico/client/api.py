import requests

import krico.core.configuration
import krico.core.hash
import krico.core.lexicon
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


class AllocationMode:
    shared = 'shared'
    exclusive = 'exclusive'

    def __init__(self):
        raise NotImplementedError()


class _Client(object):
    def __init__(self, endpoint, user, password, project):
        object.__init__(self)
        _logger.info('Creating KRICO API client for URL: {}'.format(endpoint))
        self.__endpoint = endpoint
        self.__user = user
        self.__password = password
        self.__project = project

    def __form_url(self, suffix):
        return self.__endpoint + suffix

    def __post(self, suffix, data):
        url = self.__form_url(suffix)
        _logger.debug('Posting to URL: {} | Data: {}'.format(url, data))

        response = requests.post(url, json=data)
        response.raise_for_status()

        return krico.core.lexicon.Lexicon(response.json())

    def classify(self, instance_id):
        _logger.info('Getting load prediction: instance_id={}'.format(instance_id))

        return self.__post(
            '/classify',
            {'instance_id': instance_id}
        )

    def predict_load(self, image, category, parameters, availability_zone=None, allocation=None):
        _logger.info(
            'Getting load prediction: image={}, category={}, parameters={}, zone={}'.format(image, category, parameters,
                                                                                            availability_zone))

        request_data = {
            'image': image,
            'category': category,
            'parameters': parameters,
        }

        _set_if_not_none(request_data, 'availability_zone', availability_zone)
        _set_if_not_none(request_data, 'allocation', allocation)

        return self.__post('/predict-load', request_data)


def _set_if_not_none(mapping, key, value):
    if value:
        mapping[key] = value


def connect(user, password, project):
    _logger.info('Connecting to KRICO API: {}@{}...'.format(user, project))

    cache_key = (
        user,
        krico.core.hash.string128(password),
        project
    )

    if cache_key not in _connections_cache:
        _connections_cache[cache_key] = _Client(
            endpoint=_configuration.client.endpoint,
            user=user,
            password=password,
            project=project
        )

    return _connections_cache[cache_key]


_connections_cache = {}

default = connect(
    user=_configuration.core.cloud.user,
    password=_configuration.core.cloud.password,
    project=_configuration.core.cloud.project
)
