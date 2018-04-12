import numpy
import sklearn.cluster
import sklearn.preprocessing

import krico.core.configuration
import krico.core.logger

_configuration = krico.core.configuration.root
_logger = krico.core.logger.get(__name__)


class Cluster(object):
    def __init__(self, hosts):
        object.__init__(self)

        self.__hosts = [host_info.host for host_info in hosts]

        self.__cpu_threads = int(round(numpy.mean([host_info.cpu.threads for host_info in hosts])))
        self.__cpu_performance = numpy.mean([host_info.cpu.performance for host_info in hosts])
        self.__ram_size = numpy.mean([host_info.ram.size for host_info in hosts])
        self.__ram_bandwidth = numpy.mean([host_info.ram.bandwidth for host_info in hosts])
        self.__disk_size = numpy.mean([host_info.disk.size for host_info in hosts])
        self.__disk_iops = numpy.mean([host_info.disk.iops for host_info in hosts])

        cpu_threads_rounded = self.__cpu_threads
        cpu_performance_rounded = int(round(self.__cpu_performance, -1))
        ram_size_rounded = int(round(self.__ram_size))
        ram_bandwidth_rounded = int(round(self.__ram_bandwidth, -1))
        disk_size_rounded = int(round(self.__disk_size, -2))
        disk_iops_rounded = int(round(self.__disk_iops, -2))

        self.__configuration_id = 'krico-cpu-{cpu_threads}-{cpu_performance}-ram-{ram_size}-{ram_bandwidth}-disk-{disk_size}-{disk_iops}'.format(
            cpu_threads=cpu_threads_rounded,
            cpu_performance=cpu_performance_rounded,
            ram_size=ram_size_rounded,
            ram_bandwidth=ram_bandwidth_rounded,
            disk_size=disk_size_rounded,
            disk_iops=disk_iops_rounded
        )

    @property
    def hosts(self):
        return self.__hosts

    @property
    def cpu_threads(self):
        return self.__cpu_threads

    @property
    def cpu_performance(self):
        return self.__cpu_performance

    @property
    def ram_size(self):
        return self.__ram_size

    @property
    def ram_bandwidth(self):
        return self.__ram_bandwidth

    @property
    def disk_size(self):
        return self.__disk_size

    @property
    def disk_iops(self):
        return self.__disk_iops

    @property
    def configuration_id(self):
        return self.__configuration_id


def clusterize(hosts):
    _logger.info('Clusterizing {} hosts into groups...'.format(len(hosts)))

    cluster_indexes = _mean_shift(hosts)

    hosts_by_cluster = {}

    for host, cluster_index in zip(hosts, cluster_indexes):
        cluster_id = 'CPU: {} | threads: {} | RAM: {} | disk: {} | cluster: {}'.format(
            host.cpu.model,
            host.cpu.threads,
            int(host.ram.size),
            int(round(host.disk.size, -2)),
            cluster_index
        )

        _logger.debug('Host {}: {}'.format(host.host, cluster_id))

        if cluster_id not in hosts_by_cluster:
            hosts_by_cluster[cluster_id] = []

        hosts_by_cluster[cluster_id].append(host)

    return [
        Cluster(cluster_hosts) for cluster_hosts in hosts_by_cluster.values()
    ]


def _mean_shift(hosts):
    _logger.info('Performing mean shift clustering...')

    statistics = numpy.array([
        [
            host_info.cpu.threads,
            host_info.cpu.performance,
            host_info.ram.size,
            host_info.ram.bandwidth,
            host_info.disk.size,
            host_info.disk.iops
        ]
        for host_info in hosts
    ], dtype=numpy.float64)

    sklearn.preprocessing.scale(statistics, copy=False)

    # bandwidth = 0.1 * max(sklearn.cluster.estimate_bandwidth(statistics), 0.1)
    bandwidth = 4.0 * len(hosts) ** (-0.3)  # magic function determined empirically
    _logger.debug('Using bandwidth: {}'.format(bandwidth))

    # n_jobs=-1 - all CPUs used
    clusterer = sklearn.cluster.MeanShift(n_jobs=-1, bandwidth=bandwidth)
    cluster_indexes = clusterer.fit_predict(statistics)

    n_clusters = len(numpy.unique(cluster_indexes))
    _logger.info('Found {} clusters.'.format(n_clusters))

    return cluster_indexes
