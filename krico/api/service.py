"""Service API module."""

import signal

import time

from concurrent import futures

from threading import Thread

import grpc

import logging

from krico.analysis import classifier
from krico.analysis import predictor

from krico.api.proto import api_pb2 as api_messages
from krico.api.proto import api_pb2_grpc as api_service

from krico.database import connect as connect_to_db

from krico import core
from krico.core.exception import Error

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

log = logging.getLogger(__name__)


class Api(api_service.ApiServicer):
    def Classify(self, request, context):
        classified_as = classifier.classify(request.instance_id)
        return api_messages.ClassifyResponse(classified_as=classified_as)

    def Predict(self, request, context):
        requirements = predictor.predict(
            category=request.category,
            image=request.image,
            parameters=request.parameters,
            configuration_id=request.configuration_id,
            allocation_mode=request.allocation
        )
        return api_messages.PredictResponse(requirements=requirements)

    def RefreshClassifier(self, request, context):
        classifier.refresh()
        return api_messages.RefreshClassifierResponse()

    def RefreshPredictor(self, request, context):
        predictor.refresh()
        return api_messages.RefreshPredictorResponse()

    # TODO: Implementation
    def RefreshInstances(self, request, context):
        return api_messages.RefreshInstancesResponse()

    def WorkloadsCategories(self, request, context):
        return api_messages.WorkloadsCategoriesResponse(
            workloads_categories=core.configuration['workloads']['categories'])


class ApiWorker(Thread):
    def __init__(self):
        super(ApiWorker, self).__init__()
        log.info('Initializing ApiWorker')
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        api_service.add_ApiServicer_to_server(Api(), self.server)
        self.server.add_insecure_port('{0}:{1}'.format(
            core.configuration['api']['host'],
            core.configuration['api']['port']))
        self.daemon = True
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signal, frame):
        self.server.stop(0)
        log.info('ApiWorker is stopped')
        exit(0)

    def run(self):
        try:
            self.server.start()
            log.info('Listening on {0}:{1}'.format(
                core.configuration['api']['host'],
                core.configuration['api']['port']))
            signal.pause()

        except Exception as e:
            log.error(e)
            self.server.stop(0)
            log.info('ApiWorker is stopped')


def run():
    try:
        connect_to_db()
    except Error:
        log.error(Error.message)
        exit(1)

    api = ApiWorker()
    api.start()

    while True:
        time.sleep(_ONE_DAY_IN_SECONDS)
