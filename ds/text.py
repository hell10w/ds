import re


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
