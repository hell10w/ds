import os
from os.path import exists
from os.path import isdir
from os.path import join
import pkgutil

from ds.path import get_additional_import
from ds.path import get_preset_extensions


class BaseVariant(object):
    def file_path(self):
        raise NotImplementedError

    def import_path(self):
        raise NotImplementedError

    def display_name(self):
        raise NotImplementedError


class UserVariant(BaseVariant):
    def __init__(self, directory, module_name):
        self.directory = directory
        self.module_name = module_name

    def file_path(self):
        return join(self.directory, self.module_name + '.py')

    def import_path(self):
        return self.module_name

    def display_name(self):
        return ' '.join([self.module_name, self.module_name, self.file_path()])


class SystemVariant(BaseVariant):
    def __init__(self, extension, module_name):
        self.extension = extension
        self.module_name = module_name

    def file_path(self):
        extension = __import__(self.extension)
        return join(
            extension.__path__[0],
            'presets',
            self.module_name + '.py',
        )

    def import_path(self):
        return '.'.join([self.extension, 'presets', self.module_name])

    def display_name(self):
        return ' '.join([
            '/'.join([self.extension, self.module_name]),
            self.import_path(),
            '(builtin)',
        ])


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
            UserVariant(path, name)
            for name in get_modules(path)
        ]

    for extension in get_preset_extensions():
        try:
            module = __import__(extension)
            path = module.__path__[0] + '/presets'
            for _, name, ispkg in pkgutil.walk_packages([path]):
                if ispkg:
                    continue
                result.append(SystemVariant(extension, name))
        except:
            pass

    return result
