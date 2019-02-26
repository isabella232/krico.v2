"""Database module."""
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine import CQLEngineException
from cassandra.cqlengine.management import create_keyspace_simple
from cassandra.cqlengine.management import drop_keyspace
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType

import collections
import numpy
import datetime
import json
import logging
import uuid

from krico import core

from krico.core.exception import Error, DatabaseConnectionError

log = logging.getLogger(__name__)


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

    vcpus: Number of Virtual CPU's.

    ram: Ram size in GBs.

    disk: Disk size in GBs."""

    name = columns.Text()
    vcpus = columns.Integer()
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

    @staticmethod
    def get_host_aggregates(configuration_id=None):
        """Return host aggregates from database.

        When configuration id is provides, returns host aggregates for specific
        configuration. If not, return all host aggregates.

        Keyword arguments:
        ------------------
        configuration_id : string
            Name of host aggregate.

        Returns:
        --------
        host_aggregates: list of HostAggregate objects."""

        if configuration_id:
            return HostAggregate.objects.filter(
                configuration_id=configuration_id
            ).allow_filtering().all()

        return HostAggregate.objects.all()


class Image(Model):
    """Cassandra Model that represents workload image.

    Variables:
    ------------------
    image: Name of workload image.

    category: Name of workload category."""

    image = columns.Text(primary_key=True)
    category = columns.Text()

    @staticmethod
    def get_images_names(category):
        """Return names of images in specific category.

        Images were running on cluster.

        Keyword arguments:
        ------------------
        category: string
            Name of category.

        Returns:
        --------
        images: list()
            List with image names."""

        images = []

        for row in Image.objects.\
                filter(category=category).allow_filtering():
            images.append(row.image)

        return images


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

    resource_usage: Collected metrics.

    stop_time: Stop collecting time.

    flavor: Information about flavor which instance was run on.

    start_time: Start collecting time."""

    id = columns.UUID(primary_key=True)
    name = columns.Text()
    configuration_id = columns.Text()
    category = columns.Text()
    parameters = columns.Map(columns.Text(), columns.Double())
    host_aggregate = columns.UserDefinedType(Host)
    image = columns.Text()
    host = columns.Text()
    instance_id = columns.Text()
    resource_usage = columns.Map(columns.Text(), columns.Double())
    stop_time = columns.DateTime()
    flavor = columns.UserDefinedType(Flavor)
    start_time = columns.DateTime()

    @staticmethod
    def get_classifier_learning_set(configuration_id):
        """Prepare classifier learning data for specific host aggregate.

        Keyword arguments:
        ------------------
        configuration_id : string
            Name of host aggregate.

        Returns:
        --------
        x, y """

        x = []
        y = []

        instance_query = ClassifierInstance.objects.filter(
            configuration_id=configuration_id
        ).allow_filtering()

        for instance in instance_query:
            requirements = collections.OrderedDict(
                sorted(instance.load_measured.items())
            )
            x.append(requirements.values())
            y.append(core.CATEGORIES.index(instance.category))

        return numpy.array(x), numpy.array(y)


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
    parameters = columns.Map(columns.Text(), columns.Double())
    image = columns.Text()
    instance_id = columns.Text()
    requirements = columns.Map(columns.Text(), columns.Double())

    @staticmethod
    def get_predictor_learning_set(category, image=None):
        """Prepare predictor learning data for category (and image).

        Keyword arguments:
        ------------------
        category : string
            Name of category.

        image : string
            Name of image.

        Returns:
        --------
        x, y """

        x = []
        y = []

        if category:

            if image:
                instances_query = PredictorInstance.objects.filter(
                    category=category,
                    image=image
                ).allow_filtering()
            else:
                instances_query = PredictorInstance.objects.filter(
                    category=category
                ).allow_filtering()

        else:
            raise Error(
                "Category is required for this function!"
            )

        for instance in instances_query:
            parameters = collections.OrderedDict(
                sorted(instance.parameters.items())
            )
            requirements = collections.OrderedDict(
                sorted(instance.requirements.items())
            )

            x.append(parameters.values())
            y.append(requirements.values())

        return numpy.array(x), numpy.array(y)


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
        connection.setup(
            [core.configuration['database']['host']],
            core.configuration['database']['keyspace'])
        log.info('Connected to Cassandra database!')
    except CQLEngineException:
        raise DatabaseConnectionError(
            'Cannot connect to Cassandra database at {}:{}.'.format(
                core.configuration['database']['host'],
                core.configuration['database']['keyspace']))


def delete_database():
    """Delete Cassandra database."""

    if not connection.session:
        connect()
    drop_keyspace(core.configuration['database']['keyspace'])


def fill(classifier_data_path, predictor_data_path):
    """Fill Cassandra database with data from JSON

    Keyword arguments:
    ------------------
    classifier_data_path: string
            Path to JSON with classifier data.

    predictor_data_path: string
            Path to JSON with predictor data."""

    connect()
    drop_keyspace(core.configuration['database']['keyspace'])
    create_keyspace_simple(
        core.configuration['database']['keyspace'],
        core.configuration['database']['replication_factor'])

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
            host_aggregate=Host(
                disk=row['host_aggregate']['disk'],
                ram=row['host_aggregate']['ram'],
                name=row['host_aggregate']['name'],
                configuration_id=row['host_aggregate']['configuration_id'],
                cpu=row['host_aggregate']['cpu']
            ),
            flavor=Flavor(
                vcpus=row['flavor']['vcpus'],
                disk=row['flavor']['disk'],
                ram=row['flavor']['ram'],
                name=row['flavor']['name']
            ),
            image=row['image'],
            host=row['host'],
            instance_id=row['instance_id'],
            resource_usage=row['load_measured'],
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
