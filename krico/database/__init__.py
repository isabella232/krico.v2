"""Database module."""
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine import CQLEngineException
from cassandra.cqlengine.management import create_keyspace_simple
from cassandra.cqlengine.management import drop_keyspace
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType

import datetime

import json

import uuid

import krico.core
import krico.core.exception
import krico.core.logger

_logger = krico.core.logger.get(__name__)
_configuration = krico.core.configuration['database']


class Host(UserType):
    """Cassandra user-defined type that represents host aggregate.

    Variables:
    ------------------
    name: Name of host aggregate.

    configuration_id: ID of host aggregate.

    cpu: Basic CPU parameters like threads and performance.

    ram: Basic RAM parameters like bandwidth and size.

    disk: Basic Disk parameters like iops and size."""

    name = columns.Text()
    configuration_id = columns.Text()
    cpu = columns.Map(columns.Text(), columns.Integer())
    ram = columns.Map(columns.Text(), columns.Integer())
    disk = columns.Map(columns.Text(), columns.Integer())


class Flavor(UserType):
    """Cassandra user-defined type that represents OpenStack flavor.

    Variables:
    ------------------
    name: Name of OpenStack flavor.

    vcups: Number of Virtual CPU's.

    ram: Ram size in GBs.

    disk: Disk size in GBs."""

    name = columns.Text()
    vcups = columns.Integer()
    ram = columns.Integer()
    disk = columns.Integer()


class HostAggregate(Model):
    """Cassandra Model that represents host aggregate.

    Variables:
    ------------------
    name: Name of host aggregate.

    configuration_id: ID of host aggregate.

    cpu: Basic CPU parameters like threads and performance.

    ram: Basic RAM parameters like bandwidth and size.

    disk: Basic Disk parameters like iops and size."""

    name = columns.Text()
    configuration_id = columns.Text(primary_key=True)
    cpu = columns.Map(columns.Text(), columns.Integer())
    ram = columns.Map(columns.Text(), columns.Integer())
    disk = columns.Map(columns.Text(), columns.Integer())


class Image(Model):
    """Cassandra Model that represents workload image.

    Variables:
    ------------------
    image: Name of workload image.

    category: Name of workload category."""

    image = columns.Text(primary_key=True)
    category = columns.Text()


class ClassifierInstance(Model):
    """Cassandra Model that represents single collected metrics record.

    Variables:
    ------------------
    id: UUID.

    name: Name of OpenStack instance.

    configuration_id: Id of host aggregate.

    category: Name of workload category.

    parameters: Parameters of workload.

    host_aggregate: Information about host aggregate which instance was run on.

    image: Name of workload image.

    host: Name of hypervisor host.

    instance_id: Id of instance.

    load_measured: Collected metrics.

    stop_time: Stop collecting time.

    flavor: Information about flavor which instance was run on.

    start_time: Start collecting time."""

    id = columns.UUID(primary_key=True)
    name = columns.Text()
    configuration_id = columns.Text()
    category = columns.Text()
    parameters = columns.Map(columns.Text(), columns.Integer())
    host_aggregate = columns.UserDefinedType(Host)
    image = columns.Text()
    host = columns.Text()
    instance_id = columns.Text()
    load_measured = columns.Map(columns.Text(), columns.Double())
    stop_time = columns.DateTime()
    flavor = columns.UserDefinedType(Flavor)
    start_time = columns.DateTime()


class ClassifierNetwork(Model):
    """Cassandra Model that represents classifier neural network.

    Variables:
    ------------------
    id: UUID.

    configuration_id: Id of host aggregate.

    network: Neural network model in bytes."""

    id = columns.UUID(primary_key=True)
    configuration_id = columns.Text()
    network = columns.Blob()


class PredictorInstance(Model):
    """Cassandra Model that represents single collected metrics record.

    Variables:
    ------------------
    id: UUID.

    category: Name of workload category.

    parameters: Parameters of workload.

    image: Name of workload image.

    instance_id: Id of instance.

    requirements: Required resources to run workload."""

    id = columns.UUID(primary_key=True)
    category = columns.Text()
    parameters = columns.Map(columns.Text(), columns.Integer())
    image = columns.Text()
    instance_id = columns.Text()
    requirements = columns.Map(columns.Text(), columns.Double())


class PredictorNetwork(Model):
    """Cassandra Model that represents predictor neural network.

    Variables:
    ------------------
    id: UUID.

    configuration_id: Id of host aggregate.

    image: Name of workload image.

    category: Name of workload category.

    network: Neural network model in bytes."""

    id = columns.UUID(primary_key=True)
    configuration_id = columns.Text()
    image = columns.Text()
    category = columns.Text()
    network = columns.Blob()


class MonitorSample(Model):
    """Cassandra Model that represents collected samples for classification.

    Variables:
    ------------------
    id: UUID.

    instance_id: Id of instance.

    configuration_id: Id of host aggregate.

    image: Name of workload image.

    metrics: Collected metrics."""

    id = columns.UUID(primary_key=True)
    instance_id = columns.Text()
    configuration_id = columns.Text()
    metrics = columns.Map(columns.Text(), columns.Double())


def connect():
    """Connect to Cassandra database."""

    try:
        connection.setup([_configuration['host']], _configuration['keyspace'])
        _logger.info('Connected to Cassandra database!')
    except CQLEngineException:
        raise krico.core.exception.DatabaseConnectionError(
            'Cannot connect to Cassandra database at {}:{}.'.format(
                _configuration['host'], _configuration['keyspace']))


def delete_database():
    """Delete Cassandra database."""

    if not connection.session:
        connect()
    drop_keyspace(_configuration['keyspace'])


def fill(classifier_data_path, predictor_data_path):
    """Fill Cassandra database with data from JSON

    Keyword arguments:
    ------------------
    classifier_data_path: string
            Path to JSON with classifier data.

    predictor_data_path: string
            Path to JSON with predictor data."""

    connect()
    drop_keyspace(_configuration['keyspace'])
    create_keyspace_simple(_configuration['keyspace'],
                           _configuration['replication_factor'])
    sync_table(Image)
    sync_table(HostAggregate)
    sync_table(ClassifierInstance)
    sync_table(ClassifierNetwork)
    sync_table(PredictorInstance)
    sync_table(PredictorNetwork)

    with open(classifier_data_path) as f:
        data = json.load(f)

    for row in data:
        ClassifierInstance.create(
            id=uuid.UUID(row['id']),
            category=row['category'],
            name=row['name'],
            configuration_id=row['host_aggregate']['configuration_id'],
            parameters=row['parameters'],
            host_aggregate=krico.database.Host(
                disk=row['host_aggregate']['disk'],
                ram=row['host_aggregate']['ram'],
                name=row['host_aggregate']['name'],
                configuration_id=row['host_aggregate']['configuration_id'],
                cpu=row['host_aggregate']['cpu']
            ),
            flavor=krico.database.Flavor(
                vcups=row['flavor']['vcpus'],
                disk=row['flavor']['disk'],
                ram=row['flavor']['ram'],
                name=row['flavor']['name']
            ),
            image=row['image'],
            host=row['host'],
            instance_id=row['instance_id'],
            load_measured=row['load_measured'],
            stop_time=datetime.datetime.strptime(row['start_time'],
                                                 "%Y-%m-%dT%H:%M:%S.%fZ"),
            start_time=datetime.datetime.strptime(row['start_time'],
                                                  "%Y-%m-%dT%H:%M:%S.%fZ")
        )

        HostAggregate.create(
            disk=row['host_aggregate']['disk'],
            ram=row['host_aggregate']['ram'],
            name=row['host_aggregate']['name'],
            configuration_id=row['host_aggregate']['configuration_id'],
            cpu=row['host_aggregate']['cpu']
        )

    with open(predictor_data_path) as f:
        data = json.load(f)

    for row in data:
        PredictorInstance.create(
            id=uuid.UUID(row['id']),
            instance_id=row['instance_id'],
            image=row['image'],
            category=row['category'],
            requirements=row['requirements'],
            parameters=row['parameters']
        )

        Image.create(
            image=row['image'],
            category=row['category']
        )


if __name__ == '__main__':
    fill('./models/classifier-instances.json',
         './models/predictor-instances.json')
