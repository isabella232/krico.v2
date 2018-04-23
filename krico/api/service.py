from concurrent import futures
from threading import Thread
import time
import grpc
import signal
import sys

from krico.api.proto import api_pb2 as api_messages, api_pb2_grpc as api_service

import krico.core.configuration
import krico.core.logger

import krico.core.database
import krico.analysis.classifier
import krico.analysis.predictor.refresh

_configuration = krico.core.configuration.root

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_LOGGER_NAME = 'gRPC API'


class Api(api_service.ApiServicer):
    # TODO: Implementation
    def Classify(self, request, context):
        classified_as = None
        return api_messages.ClassifyResponse(classified_as=classified_as)

    # TODO: Implementation
    def Predict(self, request, context):
        requirements = None
        return api_messages.PredictResponse(requirements=requirements)

    # TODO: Implementation
    def RefreshClassifier(self, request, context):
        return api_messages.RefreshClassifierResponse()

    # TODO: Implementation
    def RefreshPredictor(self, request, context):
        return api_messages.RefreshPredictorResponse()

    # TODO: Implementation
    def RefreshInstances(self, request, context):
        return api_messages.RefreshInstancesResponse()

    def WorkloadsCategories(self, request, context):
        workloads_categories = _configuration.dictionary()['analysis']['workloads']['categories']
        return api_messages.WorkloadsCategoriesResponse(workloads_categories=workloads_categories)


class ApiWorker(Thread):
    def __init__(self):
        super(ApiWorker, self).__init__()
        self._logger = krico.core.logger.get(_LOGGER_NAME)
        self._logger.info('Initializing ApiWorker')
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        api_service.add_ApiServicer_to_server(Api(), self.server)
        self.server.add_insecure_port('{0}:{1}'.format(
            _configuration.service.api.host, _configuration.service.api.port))
        self.daemon = True
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signal, frame):
        self.server.stop(0)
        self._logger.info('ApiWorker is stopped')
        sys.exit(0)

    def run(self):
        try:
            self.server.start()
            self._logger.info('Listening on {0}:{1}'.format(
                _configuration.service.api.host, _configuration.service.api.port))
            signal.pause()

        except Exception as e:
            self._logger.error(e)
            self.server.stop(0)
            self._logger.info('ApiWorker is stopped')

    def terminate(self):
        self._logger.info('ApiWorker is stopped')
        self.server.stop(0)
