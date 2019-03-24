from os import urandom

from string import printable


def _normalize_hex(value, base):
    return int(round(value * base / 256))


def _byte_to_int(value):
    return int(value.encode('hex'), 16)


def generate_random_string(length=32, alphabet=None):
    alphabet = alphabet or printable
    return ''.join([
        alphabet[_normalize_hex(_byte_to_int(item), len(alphabet))]
        for item in urandom(length)
    ])
