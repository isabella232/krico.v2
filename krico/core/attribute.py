import abc

import krico.core.trait


class AttributeWrapper(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        object.__init__(self)

    @abc.abstractmethod
    def get(self, key):
        raise NotImplementedError()

    @abc.abstractmethod
    def set(self, key, value):
        raise NotImplementedError()

    def __getattr__(self, attribute_name):
        if krico.core.trait.is_private_attribute(attribute_name):
            # this should always raise AttributeError, as __getattr__ only gets called for unknown attribute names
            return self._get_private_attribute(attribute_name)

        else:
            try:
                return self.get(attribute_name)

            except Exception as ex:
                raise AttributeError(ex)

    def __setattr__(self, attribute_name, value):
        if krico.core.trait.is_private_attribute(attribute_name):
            self._set_private_attribute(attribute_name, value)

        else:
            try:
                self.set(attribute_name, value)

            except Exception as ex:
                raise AttributeError(ex)

    def __getitem__(self, key):
        try:
            return self.get(key)

        except Exception as ex:
            raise KeyError(ex)

    def __setitem__(self, key, value):
        try:
            self.set(key, value)

        except Exception as ex:
            raise KeyError(ex)

    def _get_private_attribute(self, attribute_name):
        return object.__getattribute__(self, attribute_name)

    def _set_private_attribute(self, attribute_name, value):
        object.__setattr__(self, attribute_name, value)


class ObjectWrapper(AttributeWrapper):
    def __init__(self, obj):
        AttributeWrapper.__init__(self)
        self._object = obj

    def get(self, key):
        return getattr(self._object, key)

    def set(self, key, value):
        setattr(self._object, key, value)

    def __repr__(self):
        return str(self._object)

    def __contains__(self, key):
        return key in self._object
