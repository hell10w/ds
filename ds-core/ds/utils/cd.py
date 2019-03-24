from os import chdir
from os import getcwd
from contextlib import contextmanager


@contextmanager
def cd(path, **opts):
    previous = getcwd()
    try:
        chdir(path)
        yield
    finally:
        chdir(previous)
        finalizers = opts.get('finalizers', None) or []
        for finalizer in finalizers:
            finalizer()
