import os
from os.path import exists
from os.path import isdir
from os.path import join
import pkgutil

from ds.path import get_additional_import
from ds.path import get_preset_extensions


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
        result += [
            (name, name, path)
            for name in get_modules(path)
        ]

    for extension in get_preset_extensions():
        try:
            module = __import__(extension)
            path = module.__path__[0] + '/presets'
            for _, name, ispkg in pkgutil.walk_packages([path]):
                if ispkg:
                    continue
                context = '.'.join([extension, 'presets', name])
                display = '/'.join([extension, name])
                result.append((display, context, '(system)'))
        except:
            pass

    return result
