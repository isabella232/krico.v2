# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import api_pb2 as api__pb2


class ApiStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Classify = channel.unary_unary(
        '/Api/Classify',
        request_serializer=api__pb2.ClassifyRequest.SerializeToString,
        response_deserializer=api__pb2.ClassifyResponse.FromString,
        )
    self.Predict = channel.unary_unary(
        '/Api/Predict',
        request_serializer=api__pb2.PredictRequest.SerializeToString,
        response_deserializer=api__pb2.PredictResponse.FromString,
        )
    self.RefreshClassifier = channel.unary_unary(
        '/Api/RefreshClassifier',
        request_serializer=api__pb2.RefreshClassifierRequest.SerializeToString,
        response_deserializer=api__pb2.RefreshClassifierResponse.FromString,
        )
    self.RefreshPredictor = channel.unary_unary(
        '/Api/RefreshPredictor',
        request_serializer=api__pb2.RefreshPredictorRequest.SerializeToString,
        response_deserializer=api__pb2.RefreshPredictorResponse.FromString,
        )
    self.RefreshInstances = channel.unary_unary(
        '/Api/RefreshInstances',
        request_serializer=api__pb2.RefreshInstancesRequest.SerializeToString,
        response_deserializer=api__pb2.RefreshInstancesResponse.FromString,
        )
    self.WorkloadsCategories = channel.unary_unary(
        '/Api/WorkloadsCategories',
        request_serializer=api__pb2.WorkloadsCategoriesRequest.SerializeToString,
        response_deserializer=api__pb2.WorkloadsCategoriesResponse.FromString,
        )
    self.ImportMetricsFromSwanExperiment = channel.unary_unary(
        '/Api/ImportMetricsFromSwanExperiment',
        request_serializer=api__pb2.ImportMetricsFromSwanExperimentRequest.SerializeToString,
        response_deserializer=api__pb2.ImportMetricsFromSwanExperimentResponse.FromString,
        )
    self.ImportSamplesFromSwanExperiment = channel.unary_unary(
        '/Api/ImportSamplesFromSwanExperiment',
        request_serializer=api__pb2.ImportSamplesFromSwanExperimentRequest.SerializeToString,
        response_deserializer=api__pb2.ImportSamplesFromSwanExperimentResponse.FromString,
        )


class ApiServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Classify(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Predict(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RefreshClassifier(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RefreshPredictor(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RefreshInstances(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def WorkloadsCategories(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ImportMetricsFromSwanExperiment(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ImportSamplesFromSwanExperiment(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ApiServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Classify': grpc.unary_unary_rpc_method_handler(
          servicer.Classify,
          request_deserializer=api__pb2.ClassifyRequest.FromString,
          response_serializer=api__pb2.ClassifyResponse.SerializeToString,
      ),
      'Predict': grpc.unary_unary_rpc_method_handler(
          servicer.Predict,
          request_deserializer=api__pb2.PredictRequest.FromString,
          response_serializer=api__pb2.PredictResponse.SerializeToString,
      ),
      'RefreshClassifier': grpc.unary_unary_rpc_method_handler(
          servicer.RefreshClassifier,
          request_deserializer=api__pb2.RefreshClassifierRequest.FromString,
          response_serializer=api__pb2.RefreshClassifierResponse.SerializeToString,
      ),
      'RefreshPredictor': grpc.unary_unary_rpc_method_handler(
          servicer.RefreshPredictor,
          request_deserializer=api__pb2.RefreshPredictorRequest.FromString,
          response_serializer=api__pb2.RefreshPredictorResponse.SerializeToString,
      ),
      'RefreshInstances': grpc.unary_unary_rpc_method_handler(
          servicer.RefreshInstances,
          request_deserializer=api__pb2.RefreshInstancesRequest.FromString,
          response_serializer=api__pb2.RefreshInstancesResponse.SerializeToString,
      ),
      'WorkloadsCategories': grpc.unary_unary_rpc_method_handler(
          servicer.WorkloadsCategories,
          request_deserializer=api__pb2.WorkloadsCategoriesRequest.FromString,
          response_serializer=api__pb2.WorkloadsCategoriesResponse.SerializeToString,
      ),
      'ImportMetricsFromSwanExperiment': grpc.unary_unary_rpc_method_handler(
          servicer.ImportMetricsFromSwanExperiment,
          request_deserializer=api__pb2.ImportMetricsFromSwanExperimentRequest.FromString,
          response_serializer=api__pb2.ImportMetricsFromSwanExperimentResponse.SerializeToString,
      ),
      'ImportSamplesFromSwanExperiment': grpc.unary_unary_rpc_method_handler(
          servicer.ImportSamplesFromSwanExperiment,
          request_deserializer=api__pb2.ImportSamplesFromSwanExperimentRequest.FromString,
          response_serializer=api__pb2.ImportSamplesFromSwanExperimentResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Api', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
