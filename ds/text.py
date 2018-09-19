import re
from json import loads
from pprint import pformat
from collections import OrderedDict


def format_columns(*items, **opts):
    if not items:
        return

    width = [
        max(map(len, [items[row][column] for row in range(len(items))]))
        for column in range(len(items[0]))
    ]

    line_delim = opts.get('line_delim', '\n')
    column_delim = opts.get('column_delim', '  ')
    line_prefix = opts.get('line_prefix', ' ')

    return line_delim.join([
        column_delim.join([
            ''.join([line_prefix, value.ljust(width[column])])
            for column, value in enumerate(row)
        ]) for row in items
    ])


def kebab_to_snake(name):
    value = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', value).lower()


def flatten(args):
    result = []
    for item in args:
        if isinstance(item, (set, tuple, list)):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def pretty_print_object(instance):
    for key in dir(instance):
        if key.startswith('_'):
            continue
        value = getattr(instance, key)
        if callable(value):
            return
        if isinstance(value, OrderedDict):
            value = dict(value)
        formatted_value = pformat(value, indent=1)
        sep = {
            False: ' ',
            True: '\n',
        }['\n' in formatted_value]
        print((':' + sep).join([key, formatted_value]))


def safe_dict_path(d, *path, **opts):
    default = opts.pop('default', None)
    value = d
    for key in path:
        value = (value or {}).get(key, None)
    return value or default


def safe_loads(raw_data):
    try:
        data = loads(raw_data)
    except ValueError:
        data = []
    if data and isinstance(data, list):
        data = data[0]
    if not data or not isinstance(data, dict):
        data = None
    return data or {}