from os import environ
import importlib


def load_context():
    context_name = environ.get('DS', None)
    context_name = context_name or 'docker_pull'
    module = importlib.import_module(context_name)
    assert hasattr(module, 'Context'), 'Context module should contain a `Context` class'
    return getattr(module, 'Context')
