def is_not_empty(value):
    if value is None:
        return False
    return True


def drop_empty(*args):
    return list(filter(is_not_empty, args))
