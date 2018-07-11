from cassandra.cqlengine import connection
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType

import krico.core.configuration
import krico.core.exception
import krico.core.logger

_logger = krico.core.logger.get(__name__)
_configuration = krico.core.configuration.root


class HostAggregate(UserType):
    disk = columns.Map(columns.Text(), columns.Integer())
    ram = columns.Map(columns.Text(), columns.Integer())
    name = columns.Text()
    configuration_id = columns.Text()
    cpu = columns.Map(columns.Text(), columns.Integer())


class Flavor(UserType):
    vcups = columns.Integer()
    disk = columns.Integer()
    ram = columns.Integer()
    name = columns.Text()


class ClassifierInstances(Model):
    id = columns.UUID(primary_key=True)
    category = columns.Text()
    name = columns.Text()
    parameters = columns.Map(columns.Text(), columns.Integer())
    host_aggregate = HostAggregate()
    image = columns.Text()
    host = columns.Text()
    instances_id = columns.Text()
    load_measured = columns.Map(columns.Text(), columns.Float())
    stop_time = columns.DateTime()
    flavor = Flavor()
    start_time = columns.DateTime()


class PredictorInstances(Model):
    id = columns.UUID(primary_key=True)
    instance_id = columns.Text()
    category = columns.Text()
    image = columns.Text()
    requirements = columns.Map(columns.Text(), columns.Float())
    parameters = columns.Map(columns.Text(), columns.Integer())


def connect():
    try:
        connection.setup([_configuration.core.database.host], _configuration.core.database.keyspace)
        _logger.info('Connected to Cassandra database!')
    except Exception:
        raise krico.core.exception.Error('Cannot connect to Cassandra database!')
