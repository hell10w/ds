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

from cachetools import cached


HIDDEN_PREFIX = '.ds'


def clean_path(path):
    return abspath(realpath(path))


def relative(*parts):
    return clean_path(join(dirname(__file__), *parts))


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
def get_possible_imports():
    result = OrderedDict()
    for item in walk_top():
        result[join(item, HIDDEN_PREFIX)] = None
    result[home()] = None
    result[relative('presets')] = None
    return list(result.keys())


@cached({})
def get_additional_import():
    return filter(exists, get_possible_imports())
