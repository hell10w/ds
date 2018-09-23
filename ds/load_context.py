import importlib
from os import environ


def load_context():
    context_name = environ.get('DS', None)
    context_name = context_name or 'default'
    module = importlib.import_module(context_name)
    assert hasattr(
        module, 'Context'), 'Context module should contain a `Context` class'
    return getattr(module, 'Context')
