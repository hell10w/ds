import os
from os.path import exists
from os.path import isdir
from os.path import join

from ds.path import get_additional_import


def get_modules(path):
    result = []
    for name in os.listdir(path):
        filename = join(path, name)
        if isdir(filename) and exists(join(filename, '__init__.py')):
            result.append(name)
            continue
        if not filename.endswith('.py') or name.startswith('__'):
            continue
        result.append(name.rsplit('.py', 1)[0])
    return sorted(set(result))


def find_contexts():
    result = []
    for path in get_additional_import():
        result += [(name, path) for name in get_modules(path)]
    return result
