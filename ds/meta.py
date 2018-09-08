from ds import text


AUTOFILL = object()


def collect_meta_options(meta, defaults, **additional):
    result = defaults.copy()
    if meta:
        result.update(filter_public(meta, defaults))
    result.update(additional)
    return result


def filter_public(meta, defaults):
    result = {}
    for key in dir(meta):
        if key.startswith('_'):
            continue
        if key not in defaults:
            raise RuntimeError(
                'Attribute `{}` is not allowed for meta'.format(key))
        value = getattr(meta, key)
        if value and defaults[key] is AUTOFILL:
            raise RuntimeError(
                'Attribute `{}` will be filled automatically'.format(key))
        result[key] = value
    return result


class CollectMeta(type):
    meta_defaults = dict()

    def __new__(mcs, name, bases, dct):
        Meta = dct.pop('Meta', None)
        klass = super(CollectMeta, mcs).__new__(mcs, name, bases, dct)
        klass._meta = collect_meta_options(
            Meta, mcs.meta_defaults, name=text.kebab_to_snake(name))
        return klass
