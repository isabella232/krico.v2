import abc

import krico.core.attribute


class LazyObject(krico.core.attribute.AttributeWrapper):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        krico.core.attribute.AttributeWrapper.__init__(self)
        self.__object = None

    def get(self, key):
        return getattr(self.__get_object(), key)

    def set(self, key, value):
        setattr(self.__get_object(), key, value)

    def __get_object(self):
        if not self.__object:
            self.__object = self._construct()

        return self.__object

    def __len__(self):
        return len(self.__get_object())

    def __nonzero__(self):
        if self.__get_object():
            return True
        else:
            return False

    @abc.abstractmethod
    def _construct(self):
        raise NotImplementedError()


class LazyWrapper(LazyObject):
    def __init__(self, constructor):
        LazyObject.__init__(self)
        self.__constructor = constructor

    def _construct(self):
        return self.__constructor()


class Cache(krico.core.attribute.AttributeWrapper):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        krico.core.attribute.AttributeWrapper.__init__(self)
        self.__cache = {}

    def get(self, key):
        if key not in self.__cache:
            self.__cache[key] = self._construct(key)

        return self.__cache[key]

    def set(self, key, value):
        raise NotImplementedError()

    @abc.abstractmethod
    def _construct(self, item):
        raise NotImplementedError()
