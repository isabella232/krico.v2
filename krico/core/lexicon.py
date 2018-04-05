import copy

import krico.core.attribute
import krico.core.trait
import krico.core.formatter


class LexiconKeyError(KeyError):
    def __init__(self, section, key):
        KeyError.__init__(self)

        self.key = key
        self.section = section

    def __repr__(self):
        return 'Key <{}> not found in lexicon section <{}>'.format(self.key, self.section)


class Lexicon(krico.core.attribute.AttributeWrapper):
    @staticmethod
    def __split_key(key):
        tokens = str(key).split('.', 1)
        head = tokens[0]
        tail = tokens[1] if len(tokens) > 1 else None

        return head, tail

    @classmethod
    def __construct(cls, name, value, parent):
        if krico.core.trait.is_instance(value, Lexicon):
            value.__parent = parent  # that, or deepcopy (would be neat, but less efficient)
            return value

        elif krico.core.trait.is_instance(value, dict):
            return cls(value, name, parent)

        elif krico.core.trait.is_instance(value, list):
            return [cls.__construct(name, v, parent) for v in value]

        else:
            return value

    @classmethod
    def __to_dictionary(cls, item):
        if issubclass(type(item), Lexicon):
            return {
                key: cls.__to_dictionary(value)
                for key, value in item.items()
                }

        elif krico.core.trait.is_instance(item, list):
            return [cls.__to_dictionary(value) for value in item]

        else:
            return item

    def __init__(self, document=None, name=None, parent=None):
        krico.core.attribute.AttributeWrapper.__init__(self)

        self.__items = {}
        if document:
            for key, value in document.items():
                self.set(key, value)

        if name:
            self.__name = name
        elif document and 'name' in document:
            self.__name = document['name']
        else:
            self.__name = 'lexicon'

        self.__parent = parent

    def get(self, key):
        # we split the key by dots, so that the lexicons can be nested
        key_head, key_tail = Lexicon.__split_key(key)

        # head
        if key_head in self.__items:
            # we have the proper key
            head_value = self.__items[key_head]

        # TODO: remove completely
        # elif key_head == self.__name:
        #	head_value = self

        elif self.__parent is not None:
            # key not found, look in parent
            try:
                head_value = self.__parent.get(key_head)

            except LexiconKeyError as ex:
                # key not found in parent, let's chain exceptions!
                raise LexiconKeyError(
                    section='{}.{}'.format(ex.section, self.__name),
                    key=key
                )

        else:
            # we have nowhere else to run, key not found
            raise LexiconKeyError(
                section=self.__name,
                key=key
            )

        # tail
        value = None

        if not key_tail:
            value = head_value

        elif krico.core.trait.is_instance(head_value, Lexicon):
            value = head_value.get(key_tail)

        # return
        if value is not None:
            return value
        else:
            raise LexiconKeyError(
                section=self.__name,
                key=key
            )

    def set(self, key, value):
        if value is not None:
            key_head, key_tail = Lexicon.__split_key(key)

            if key_tail:
                value = {key_tail: value}

            value = Lexicon.__construct(key_head, value, self)

            if key_head in self.__items \
                    and krico.core.trait.is_instance(value, Lexicon) \
                    and krico.core.trait.is_instance(self.__items[key_head], Lexicon):

                # update existing lexicon
                self.__items[key_head].update(value)

            else:
                self.__items[key_head] = value

    def clear(self):
        self.__items.clear()

    def remove(self, key):
        del self.__items[key]

    def __delitem__(self, key):
        self.remove(key)

    def __contains__(self, key):
        return key in self.__items

    def __eq__(self, other):
        return self.__items == other.__items

    def update(self, other):
        for key, value in other.items():
            self.set(key, value)

    def empty(self):
        for value in self.values():
            if krico.core.trait.is_instance(value, Lexicon):
                if not value.empty():
                    return False

            elif value is not None:
                return False

        return True

    def items(self):
        return self.__items.items()

    def keys(self):
        return self.__items.keys()

    def values(self):
        return self.__items.values()

    def dictionary(self):
        return Lexicon.__to_dictionary(self)

    def copy(self):
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        items_copy = {key: copy.deepcopy(value, memo) for key, value in self.items()}
        return Lexicon(items_copy, self.__name, self.__parent)

    def __repr__(self):
        items_text = krico.core.formatter.pretty(self.dictionary())
        return '<{module_name}.{type_name}>\n{content}'.format(
            module_name=__name__,
            type_name=type(self).__name__,
            content=items_text
        )
