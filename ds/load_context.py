import imp


def load_context(name):
    context_filename = name
    module = imp.load_source('context', context_filename)
    Context = getattr(module, 'Context', None)
    if Context is None:
        logger.error('Context is not loaded')
    return Context
