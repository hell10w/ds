def format_columns(*items, **opts):
    if not items:
        return

    width = [
        max(map(len, [(items[row][column] or '').strip()
                      for row in range(len(items))]))
        for column in range(len(items[0]))
    ]

    line_delim = opts.get('line_delim', '\n')
    column_delim = opts.get('column_delim', '  ')
    line_prefix = opts.get('line_prefix', ' ')

    return line_delim.join([
        ''.join([
            line_prefix,
            column_delim.join([
                value.ljust(width[column])
                for column, value in enumerate(row)
            ])
        ])
        for row in items
    ])
