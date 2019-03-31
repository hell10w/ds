from __future__ import unicode_literals
from collections import OrderedDict
from os import getcwd
from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import exists
from os.path import expanduser
from os.path import join
from os.path import realpath
import pkgutil
import importlib

from cachetools import cached


HIDDEN_PREFIX = '.ds'
PRESETS_PREFIX = 'dsjk_'


def clean_path(path):
    return abspath(realpath(path))


def relative(*parts, **kwargs):
    return clean_path(join(dirname(kwargs.pop('target', __file__)), *parts))


@cached({})
def pwd():
    return getcwd()


@cached({})
def home():
    return join(expanduser('~'), HIDDEN_PREFIX)


@cached({})
def walk_top(path=None):
    path = clean_path(path or pwd())
    result = []
    while True:
        if path in result:
            continue
        result.append(path)
        path = dirname(path)
        if result[-1] == path:
            break
    return result


@cached({})
def find_for(target):
    for path in walk_top():
        if not exists(join(path, target)):
            continue
        if path == expanduser('~'):
            continue
        return path
    return pwd()


@cached({})
def get_project_name():
    return basename(find_for(HIDDEN_PREFIX))


@cached({})
def get_project_root():
    return find_for(HIDDEN_PREFIX)


@cached({})
def get_preset_extensions():
    result = []
    for _, name, _ in pkgutil.iter_modules():
        if not name.startswith(PRESETS_PREFIX) and name != 'ds':
            continue
        try:
            importlib.import_module(name)
            result.append(name)
        except:
            # it doesn't matter if can't import
            pass
    return result


@cached({})
def get_possible_imports():
    result = OrderedDict()
    for item in walk_top():
        result[join(item, HIDDEN_PREFIX)] = None
    result[home()] = None
    # result[relative('presets')] = None
    return list(result.keys())


@cached({})
def get_additional_import():
    result = filter(exists, get_possible_imports())
    return result
