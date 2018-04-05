import hashlib


def string128(data):
    return _compute_string(data, hashlib.sha512)


def string40(data):
    return _compute_string(data, hashlib.sha1)


def _compute_string(data, algorithm):
    return algorithm(data).hexdigest()
