import imp
import importlib
from logging import getLogger
import os
from os.path import sep, join, exists, abspath, realpath, dirname, expanduser, basename

from ds.decorators import cached_func


HIDDEN_PREFIX = '.ds'


def relative(*parts):
    return join(dirname(__file__), *parts)


def is_fs_path(path):
    return sep in path


def clean_path(path):
    return abspath(realpath(path))


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
    result = [
        join(item, HIDDEN_PREFIX)
        for item in walk_top()
    ]
    result.append(users_home())
    result.append(relative('presets'))
    return filter(exists, result)
