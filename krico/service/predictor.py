import flask
import math

import krico.core.configuration
import krico.core.exception
import krico.core.lexicon
import krico.core.logger

import krico.analysis.predictor.requirements

import krico.service.aggregates
import krico.service.response

_logger = krico.core.logger.get(__name__)
_configuration = krico.core.configuration.root


class _AllocationMode:
    shared = 'shared'
    exclusive = 'exclusive'

    def __init__(self):
        raise NotImplementedError()


class PredictLoadRequest(object):
    def __init__(self, json):
        object.__init__(self)

        try:
            self.image = json['image']
            self.availability_zone = json.get('availability_zone', None)
            self.category = json['category']
            self.parameters = krico.core.lexicon.Lexicon(json['parameters'])
            self.allocation = json.get('allocation', _AllocationMode.shared)
        except KeyError as ex:
            raise KeyError("request is not valid, missing argument: ", ex.message)
        except:
            raise Exception("unknown error")


class NotEnoughResources(krico.core.exception.Error):
    def __init__(self, aggregate_name):
        krico.core.exception.Error.__init__(self, 'Cannot execute the workload on host aggregate {}.'.format(aggregate_name))


@krico.service.response.request_handler
def predict_load_request():
    request = PredictLoadRequest(flask.request.json)
    predictions = predict_load(request)

    response_predictions = []

    for prediction in predictions:
        prediction_dictionary = {
            'name': prediction.host_aggregate.name,
            'configuration_id': prediction.host_aggregate.configuration_id,
            'availability_zone': prediction.host_aggregate.availability_zone,
            'flavor': prediction.flavor.dictionary()
        }
        if 'requirements' in prediction:
            prediction_dictionary['requirements'] = prediction.requirements.dictionary()

        response_predictions.append(prediction_dictionary)

    return {
        'predictions': response_predictions
    }


def predict_load(predict_request):
    aggregates = _find_host_aggregates(predict_request)

    _logger.debug('Prediciting load for {} host aggregate(s)...'.format(len(aggregates)))

    predictions = []

    for aggregate_info in aggregates:
        try:
            prediction_for_aggregate = _predict_load_for_aggregate(predict_request, aggregate_info)
            predictions.append(prediction_for_aggregate)

        except NotEnoughResources:
            _logger.debug('Not enough resources to predict load for host aggregate {}'.format(aggregate_info.configuration_id))
    
    if not aggregates:
        raise krico.core.exception.Error('No host aggregates predicted for selected availability zone!')

    return predictions


def _find_host_aggregates(predict_request):
    if predict_request.availability_zone:
        return krico.service.aggregates.find(predict_request.availability_zone)
    else:
        return krico.service.aggregates.find()


def _predict_load_for_aggregate(predict_request, aggregate_info):
    if predict_request.category != 'unknown':
        requirements = krico.analysis.predictor.requirements.predict(predict_request, aggregate_info)

    flavor_vcpus_max = _floor(aggregate_info.cpu.threads * (1.0 - _configuration.service.predictor.reserved.vcpus))
    flavor_ram_max = _floor(aggregate_info.ram.size * (1.0 - _configuration.service.predictor.reserved.ram)) * 1024
    flavor_disk_max = _floor(aggregate_info.disk.size * (1.0 - _configuration.service.predictor.reserved.disk))

    if predict_request.allocation == _AllocationMode.shared:
        if predict_request.category == 'unknown':
            flavor_vcpus = predict_request.parameters.vcpus
            flavor_ram = predict_request.parameters.ram

        else:
            flavor_vcpus = _ceil(requirements.cpu_threads)
            flavor_ram = _ceil(requirements.ram_size) * 1024

        flavor_disk = _ceil(predict_request.parameters.disk)

        if flavor_vcpus > flavor_vcpus_max or flavor_ram > flavor_ram_max or flavor_disk > flavor_disk_max:
            _logger.debug('FLAVOR_DISK: {} / {}'.format(flavor_disk, flavor_disk_max))
            _logger.debug('FLAVOR_RAM: {} / {}'.format(flavor_ram, flavor_ram_max))
            _logger.debug('FLAVOR_VCPUS: {} / {}'.format(flavor_vcpus, flavor_vcpus_max))
            raise NotEnoughResources(aggregate_info.configuration_id)

    elif predict_request.allocation == _AllocationMode.exclusive:
        flavor_vcpus = flavor_vcpus_max
        flavor_ram = flavor_ram_max
        flavor_disk = flavor_disk_max

    else:
        raise NotImplementedError()

    flavor_name = 'krico-{}c-{}m-{}d'.format(
        flavor_vcpus,
        flavor_ram / 1024,
        flavor_disk
    )

    prediction_for_zone = krico.core.lexicon.Lexicon({
        'host_aggregate': aggregate_info,
        'flavor': {
            'name': flavor_name,
            'vcpus': flavor_vcpus,
            'ram': flavor_ram,
            'disk': flavor_disk
        }
    })

    if predict_request.category != 'unknown':
        prediction_for_zone.requirements = requirements

    return prediction_for_zone


def _floor(number):
    return int(math.floor(number))


def _ceil(number):
    return int(math.ceil(number))
