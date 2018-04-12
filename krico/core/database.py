import os
import pickle
import pymongo.mongo_client

import krico.core.attribute
import krico.core.lazy
import krico.core.lexicon
import krico.core.logger
import krico.core.configuration

_logger = krico.core.logger.get('krico.core.database')
_configuration = krico.core.configuration.root


class DataObject(object):
    def __init__(self):
        object.__init__(self)
        self._dao = krico.core.lexicon.Lexicon()

    def dump(self):
        dictionary = self._dao.dictionary()
        DataObject._dump_transform(dictionary)

        return dictionary

    def load(self, dictionary):
        if '_id' in dictionary:
            del dictionary['_id']

        DataObject._load_transform(dictionary)
        self._dao = krico.core.lexicon.Lexicon(dictionary)

    @staticmethod
    def _dump_transform(dictionary):
        for (key, value) in dictionary.items():
            if isinstance(value, BinaryObject):
                dictionary[key] = {
                    '_type': BinaryObject.type,
                    'data': pickle.dumps(value)
                }

            elif isinstance(value, dict):
                DataObject._dump_transform(value)

    @staticmethod
    def _load_transform(dictionary):
        for (key, value) in dictionary.items():
            if isinstance(value, dict):
                if '_type' in value and value['_type'] == BinaryObject.type:
                    dictionary[key] = pickle.loads(value['data'])

                else:  # Again, make sure to recurse into sub-docs
                    DataObject._load_transform(value)


class BinaryObject(object):
    type = 'krico-binary'

    def __init__(self):
        object.__init__(self)


class BinaryObjectWrapper(BinaryObject):
    def __init__(self, data):
        object.__init__(self)
        self.__data = data

    @property
    def data(self):
        return self.__data


class _MongoProxy(krico.core.attribute.AttributeWrapper):
    def __init__(self, host, port):
        krico.core.attribute.AttributeWrapper.__init__(self)
        self.__host = host
        self.__port = port
        self.__connection = None
        self.__pid = None

    def get(self, key):
        return _DatabaseProxy(self, key)

    def set(self, key, value):
        raise NotImplementedError()

    def connect(self):
        _logger.info('Establishing connection to MongoDB server at: {}:{} from PID: {}'.format(self.__host, self.__port, os.getpid()))
        mongo_client = pymongo.mongo_client.MongoClient(self.__host, self.__port)

        # Force to download some data from server - if connection is invalid, it will fail and raise exception
        mongo_server_info = mongo_client.server_info()

        _logger.info('Successfully connected to MongoDB version {}'.format(mongo_server_info['version']))
        self.__connection = mongo_client
        self.__pid = os.getpid()

    def disconnect(self):
        if self.connection:
            self.__connection.close()

    @property
    def connection(self):
        if not self.__connection or self.__pid != os.getpid():
            self.connect()

        return self.__connection


class _DatabaseProxy(krico.core.attribute.AttributeWrapper):
    def __init__(self, mongo_proxy, database_name):
        krico.core.attribute.AttributeWrapper.__init__(self)
        self.__mongo_proxy = mongo_proxy
        self.__database_name = database_name

    def get(self, key):
        return _CollectionProxy(self, key)

    def set(self, key, value):
        raise NotImplementedError()

    @property
    def database(self):
        return self.__mongo_proxy.connection[self.__database_name]

    def collections(self):
        return self.database.collection_names(include_system_collections=False)


class _CollectionProxy(object):
    # Maximum number of reconnect tries when operation has failed
    MAX_RECONNECT = 5

    def __init__(self, database_proxy, collection_name):
        object.__init__(self)
        self.__database_proxy = database_proxy
        self.__collection_name = collection_name

    def _handle_reconnect(self, func, *args, **kwargs):
        for i in range(self.MAX_RECONNECT):
            try:
                result = func(*args, **kwargs)
                return result
            except pymongo.errors.AutoReconnect:
                _logger.error('Error occured, trying to reconnect ({}/{})...'
                    .format(i + 1, self.MAX_RECONNECT))

    @property
    def collection(self):
        return self.__database_proxy.database[self.__collection_name]

    def load_one(self, document_filter):
        _logger.debug('Loading single document for filter: {}'.format(document_filter))
        document = self._handle_reconnect(self.collection.find_one, document_filter)

        if document:
            return _CollectionProxy._create_data_object(document)
        else:
            return None

    def load_many(self, document_filter, sort_filter=None):
        _logger.debug('Loading multiple documents for filter: {}'.format(document_filter))

        documents = self._handle_reconnect(self.collection.find, document_filter)

        if sort_filter:
            documents = self._handle_reconnect(documents.sort, sort_filter)

        while True:
            try:
                # Handle connection failures while getting next document from database (load_many function is iterable)
                next = self._handle_reconnect(documents.next)
                yield _CollectionProxy._create_data_object(next)
            except StopIteration:
                break

    def save_one(self, document_filter, data_object):
        _logger.debug('Saving single document for filter: {}'.format(document_filter))
        document = _CollectionProxy._create_document(data_object)
        self._handle_reconnect(self.collection.replace_one, document_filter, document, upsert=True)

    def insert_one(self, data_object):
        _logger.debug('Inserting single document...')
        document = _CollectionProxy._create_document(data_object)
        self._handle_reconnect(self.collection.insert_one, document)

    def insert_many(self, documents):
        _logger.debug('Inserting {} documents...'.format(len(documents)))
        toinsert = [_CollectionProxy._create_document(document) for document in documents]
        self._handle_reconnect(self.collection.insert_many, toinsert)

    def delete_one(self, document_filter):
        _logger.debug('Deleting single document for filter: {}'.format(document_filter))
        self._handle_reconnect(self.collection.delete_one, document_filter)

    def delete_many(self, document_filter):
        _logger.debug('Deleting multiple documents for filter: {}'.format(document_filter))
        self._handle_reconnect(self.collection.delete_many, document_filter)

    def drop(self):
        _logger.debug('Dropping collection.')
        self._handle_reconnect(self.collection.drop)

    def create_index(self, keys):
        _logger.debug('Create index with keys: {}.'.format(keys))
        self._handle_reconnect(self.collection.create_index, keys)

    def distinct(self, field):
        _logger.debug('Load unique value for given key: {}'.format(field))
        return self._handle_reconnect(self.collection.distinct, field)

    def aggregate(self, group_filter):
        _logger.debug('Aggregating with group: {}'.format(group_filter))
        return self._handle_reconnect(self.collection.aggregate, group_filter)

    @staticmethod
    def _create_data_object(document):
        if '_id' in document:
            del document['_id']

        _CollectionProxy._load_transform(document)

        return krico.core.lexicon.Lexicon(document)

    @staticmethod
    def _create_document(data_object):
        document = data_object.dictionary()
        _CollectionProxy._dump_transform(document)
        return document

    @staticmethod
    def _load_transform(document):
        for key, value in document.items():
            if isinstance(value, dict):
                if '_type' in value and value['_type'] == BinaryObject.type:
                    document[key] = pickle.loads(value['data'])
                else:
                    _CollectionProxy._load_transform(value)

    @staticmethod
    def _dump_transform(document):
        for key, value in document.items():
            if isinstance(value, BinaryObject):
                document[key] = {
                    '_type': BinaryObject.type,
                    'data': pickle.dumps(value)
                }

            elif isinstance(value, dict):
                _CollectionProxy._dump_transform(value)


# TODO refactor this in case of problems with DB connection
class MongoProxyCache(krico.core.lazy.Cache):
    def __init__(self):
        krico.core.lazy.Cache.__init__(self)

    def _construct(self, item):
        host, port = item
        _logger.info('Creating connection cache to MongoDB for key {}'.format(item))
        mongo_proxy = _MongoProxy(host, port)
        mongo_proxy.connect()
        return mongo_proxy
        

class Analysis(object):
    classifier_networks = None
    classifier_instances = None
    classifier_statistics = None
    predictor_networks = None
    predictor_instances = None
    predictor_statistics = None

    @staticmethod
    def assign(connection):
        try:
            analysis = connection['analysis']

            Analysis.classifier_networks = analysis['classifier-networks']
            Analysis.classifier_instances = analysis['classifier-instances']
            Analysis.classifier_statistics = analysis['classifier-statistics']

            Analysis.predictor_networks = analysis['predictor-networks']
            Analysis.predictor_instances = analysis['predictor-instances']
            Analysis.predictor_statistics = analysis['predictor-statistics']

            _logger.debug('Connected to KRICO analysis database')
        except (AttributeError, TypeError):
            _logger.error('Cannot access KRICO analysis database')


class Monitor(object):
    hosts = None
    samples = None

    @staticmethod
    def assign(connection):
        try:
            monitor = connection['monitor']
            Monitor.hosts = monitor['hosts']
            Monitor.samples = monitor['samples']
            Monitor.samples.create_index('instance_id')

            _logger.debug('Connected to KRICO monitor database')
        except (AttributeError, TypeError):
            _logger.error('Cannot access KRICO monitor database')


class Service(object):
    instances = None
    monitorservice = None
    monitor_hosts = None
    monitor_samples = None
    analysisservice = None
    workloads_list = None

    @staticmethod
    def assign(connection):
        try:
            service = connection['service']
            Service.instances = service['instances']

            Service.monitorservice = connection['monitor']

            Service.monitor_hosts = Service.monitorservice['hosts']
            Service.monitor_samples = Service.monitorservice['samples']

            Service.analysisservice = connection['analysis']
            Service.workloads_list = Service.analysisservice['instances']

            _logger.debug('Connected to KRICO service database')
        except (AttributeError, TypeError):
            _logger.error('Cannot access KRICO service database')


connection_cache = MongoProxyCache()
connection = _MongoProxy(None, None)

def connect():
    global connection

    try:
        connection = connection_cache[(_configuration.core.database.host, _configuration.core.database.port)]

        Analysis.assign(connection)
        Monitor.assign(connection)
        Service.assign(connection)
    except KeyError:
        raise krico.core.exception.Error('Cannot connect to MongoDB!')
