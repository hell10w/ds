import importlib

from ds.flow import find_pre_usage_option


def load_context():
    context_name = find_pre_usage_option('-c')
    module = importlib.import_module(context_name or 'default')
    assert hasattr(
        module, 'Context'), 'Context module should contain a `Context` class'
    return getattr(module, 'Context')
