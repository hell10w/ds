import imp
import importlib
import os
from collections import OrderedDict
from logging import getLogger
from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import exists
from os.path import expanduser
from os.path import join
from os.path import realpath
from os.path import sep
from os.path import isdir

from ds.decorators import cached_func

HIDDEN_PREFIX = '.ds'


def clean_path(path):
    return abspath(realpath(path))


def relative(*parts):
    return clean_path(join(dirname(__file__), *parts))


@cached_func
def get_pwd():
    return os.getcwd()


@cached_func
def users_home():
    return join(expanduser('~'), HIDDEN_PREFIX)


@cached_func
def walk_top(path=None):
    path = clean_path(path or get_pwd())
    result = []
    while True:
        if path in result:
            continue
        result.append(path)
        path = dirname(path)
        if result[-1] == path:
            break
    return result


@cached_func
def find_project_root():
    for path in walk_top():
        if not exists(join(path, HIDDEN_PREFIX)):
            continue
        if path == expanduser('~'):
            continue
        return path
    return get_pwd()


@cached_func
def get_project_name():
    return basename(find_project_root())


@cached_func
def build_additional_import():
    result = {
        join(item, HIDDEN_PREFIX): None
        for item in walk_top()
    }
    result[users_home()] = None
    result[relative('presets')] = None
    return [
        path
        for path in result.keys()
        if exists(path)
    ]


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
    for path in build_additional_import():
        result += get_modules(path)
    return result
