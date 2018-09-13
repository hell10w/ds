import imp
import importlib
from logging import getLogger

from ds import fs

logger = getLogger(__name__)

_cache = {}


def try_to_import(path):
    if fs.is_fs_path(path):
        module = import_by_path(path)
    else:
        module = import_module(path)
    return module


def import_by_path(path):
    if path not in _cache:
        _cache[path] = imp.load_source('tmp', path)
    return _cache[path]


def import_module(path):
    return importlib.import_module(path)


def get_module_path(module):
    return fs.clean_path(module.__file__)
