import mock
import pytest

from krico import core
from krico.core.exception import NotEnoughMetricsError, NotFoundError
from krico.database import importer

experiment_id = "experiment_id"


class TestImportMetricsFromSwanExperiment(object):

    @mock.patch('krico.database.importer.Metrics')
    def test_if_throw_exception_when_cannot_gather_basic_information(
            self, mock_metrics):
        mock_metrics.get_by_experiment_id.return_value.count.return_value =\
            len(core.METRICS*10)

        mock_metrics.get_by_experiment_id.return_value.\
            first.return_value.tags = {}

        try:
            importer.import_metrics_from_swan_experiment(experiment_id)
        except Exception as e:
            assert isinstance(e, NotFoundError)


class TestGetParameters(object):

    @pytest.mark.parametrize("metric,category", (
            (importer.Metrics(
                tags={'memory': "0.0", 'ratio': "0.0"}), "caching"),
            (importer.Metrics(
                tags={'clients': "0.0", 'ratio': "0.0"}), "caching"),
            (importer.Metrics(
                tags={'clients': "0.0", 'memory': "0.0"}), "caching"),
            (importer.Metrics(
                tags={'memory': "0.0", 'ratio': "0.0"}), "bigdata")
    ))
    def test_if_throw_exception_when_parameters_not_found(
            self, metric, category):
        try:
            importer._get_parameters(metric, category)
        except Exception as e:
            assert isinstance(e, NotFoundError)
            return

        assert False

    @pytest.mark.parametrize("metric,expected,category", (
            (importer.Metrics(
                tags={'memory': "1.0", 'ratio': "0.5", 'clients': "300.0"}
            ), {
                 'memory': 1.0,
                 'ratio': 0.5,
                 'clients': 300.0
             }, "caching"),
    ))
    def test_if_return_parameters(self, metric, expected, category):
        parameters = importer._get_parameters(metric, category)
        for expect in expected:
            assert parameters[expect] == expected[expect]


class TestRemapMetricNames(object):

    @pytest.mark.parametrize('metrics, expected', (
            ({'cputime': 1.0,
              'memory/rss': 2.0,
              'cache-references': 3.0,
              'cache-misses': 4.0,
              'rdbytes': 5.0,
              'wrbytes': 6.0,
              'rdreq': 7.0,
              'wrreq': 8.0,
              'txbytes': 9.0,
              'rxbytes': 10.0,
              'txpackets': 11.0,
              'rxpackets': 12.0},
             {'cpu:time': 1.0,
              'ram:used': 2.0,
              'cpu:cache:references': 3.0,
              'cpu:cache:misses': 4.0,
              'disk:bandwidth:read': 5.0,
              'disk:bandwidth:write': 6.0,
              'disk:operations:read': 7.0,
              'disk:operations:write': 8.0,
              'network:bandwidth:send': 9.0,
              'network:bandwidth:receive': 10.0,
              'network:packets:send': 11.0,
              'network:packets:receive': 12.0}),
    ))
    def test_if_return_expected_mapping(self, metrics, expected):
        importer._remap_metrics_names(metrics)

        for metric in metrics:
            assert metrics[metric] == expected[metric]


class TestGetRequirements(object):

    @pytest.mark.parametrize('metrics, expected', (
     ({'cpu:time': 2.0,
       'ram:used': 4.0,
       'cpu:cache:references': 0.0,
       'cpu:cache:misses': 0.0,
       'disk:bandwidth:read': 0.0,
       'disk:bandwidth:write': 0.0,
       'disk:operations:read': 3.0,
       'disk:operations:write': 3.0,
       'network:bandwidth:send': 4.0,
       'network:bandwidth:receive': 4.0,
       'network:packets:send': 0.0,
       'network:packets:receive': 0.0},
      {'cpu_threads': 2.0,
       'ram_size': 4.0,
       'disk_iops': 6.0,
       'network_bandwidth': 8.0}),))
    def test_if_return_expected_requirements(self, metrics, expected):
        requirements = importer._get_requirements(metrics)

        for expect in expected:
            assert expected[expect] == requirements[expect]


class TestPrepareResourceUsage(object):

    @pytest.mark.parametrize(
        "metric_batch_size,batch_count,metrics,expected",
        ((3, 3, [
            importer.Metrics(ns="cputime", doubleval=1.0),
            importer.Metrics(ns="cputime", doubleval=2.0),
            importer.Metrics(ns="cputime", doubleval=3.0),
            importer.Metrics(ns="memory/rss", doubleval=4.0),
            importer.Metrics(ns="memory/rss", doubleval=5.0),
            importer.Metrics(ns="memory/rss", doubleval=6.0),
            importer.Metrics(ns="cache-references", doubleval=7.0),
            importer.Metrics(ns="cache-references", doubleval=8.0),
            importer.Metrics(ns="cache-references", doubleval=9.0)],
          {'cputime': [1.0, 2.0, 3.0],
           'memory/rss': [4.0, 5.0, 6.0],
           'cache-references': [7.0, 8.0, 9.0]}),))
    def test_if_return_expected_resource_usage(
            self, metric_batch_size, batch_count, metrics, expected):

        resource_usage = importer._prepare_resource_usage(
            metric_batch_size, batch_count, metrics)

        for expect in expected:
            assert resource_usage[expect] == expected[expect]


class TestImportMonitorSamplesFromSwanExperiment(object):

    @mock.patch('krico.database.importer.Metrics')
    def test_if_throw_exception_when_cannot_gather_basic_information(
            self, mock_metrics):
        mock_metrics.get_by_experiment_id.return_value.count.return_value =\
            len(core.METRICS*10)

        mock_metrics.get_by_experiment_id.return_value.\
            first.return_value.tags = {}

        try:
            importer.import_samples_from_swan_experiment(experiment_id)
        except Exception as e:
            assert isinstance(e, NotFoundError)


class TestCheckMetrics(object):

    def test_if_throw_exception_when_no_metric(self):
        try:
            importer._check_metrics(0, 12)
        except Exception as e:
            assert isinstance(e, NotEnoughMetricsError)
            return
        assert False

    def test_if_throw_exception_when_not_all_batches_with_metric_are_available(
            self):
        try:
            importer._check_metrics(13, 12)
        except Exception as e:
            assert isinstance(e, NotEnoughMetricsError)
            return
        assert False


class TestTransformResourceUsage(object):

    @pytest.mark.parametrize(
        'usage,length,expected', [
            (({'cpu:time': [-2.0, -1.0],
               'ram:used': [-2.0, -1.0],
               'cpu:cache:references': [-2.0, -1.0],
               'cpu:cache:misses': [-2.0, -1.0],
               'disk:bandwidth:read': [-2.0, -1.0],
               'disk:bandwidth:write': [-2.0, -1.0],
               'disk:operations:read': [-2.0, -1.0],
               'disk:operations:write': [-2.0, -1.0],
               'network:bandwidth:send': [-2.0, -1.0],
               'network:bandwidth:receive': [-2.0, -1.0],
               'network:packets:send': [-2.0, -1.0],
               'network:packets:receive': [-2.0, -1.0]}), 2,
             {'cpu:time': [0.0],
              'ram:used': [0.0],
              'cpu:cache:references': [0.0],
              'cpu:cache:misses': [0.0],
              'disk:bandwidth:read': [0.0],
              'disk:bandwidth:write': [0.0],
              'disk:operations:read': [0.0],
              'disk:operations:write': [0.0],
              'network:bandwidth:send': [0.0],
              'network:bandwidth:receive': [0.0],
              'network:packets:send': [0.0],
              'network:packets:receive': [0.0]})])
    def test_if_return_not_negative_results(self, usage, length, expected):
        test_resource_usage = importer._transform_resource_usage(usage, length)
        assert test_resource_usage == expected

    @pytest.mark.parametrize(
        'usage,length,expected', [
            (({'cpu:time': [-2.0, -1.0],
               'ram:used': [-2.0, -1.0],
               'cpu:cache:references': [-2.0, -1.0],
               'cpu:cache:misses': [-2.0, -1.0],
               'disk:bandwidth:read': [-2.0, -1.0],
               'disk:bandwidth:write': [-2.0, -1.0],
               'disk:operations:read': [-2.0, -1.0],
               'disk:operations:write': [-2.0, -1.0],
               'network:bandwidth:send': [-2.0, -1.0],
               'network:bandwidth:receive': [-2.0, -1.0],
               'network:packets:send': [-2.0, -1.0],
               'network:packets:receive': [-2.0, -1.0]}), 2,
             {'cpu:time': [0.0],
              'ram:used': [0.0],
              'cpu:cache:references': [0.0],
              'cpu:cache:misses': [0.0],
              'disk:bandwidth:read': [0.0],
              'disk:bandwidth:write': [0.0],
              'disk:operations:read': [0.0],
              'disk:operations:write': [0.0],
              'network:bandwidth:send': [0.0],
              'network:bandwidth:receive': [0.0],
              'network:packets:send': [0.0],
              'network:packets:receive': [0.0]})])
    def test_if_expected_results(self, usage, length, expected):
        test_resource_usage = importer._transform_resource_usage(usage, length)
        assert test_resource_usage == expected