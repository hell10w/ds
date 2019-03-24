def flatten(args):
    result = []
    for item in args:
        if isinstance(item, (set, tuple, list)):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
