def is_instance(obj, cls):
    return issubclass(type(obj), cls)


def is_private_attribute(attribute_name):
    return attribute_name.startswith('_')
