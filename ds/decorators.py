from functools import wraps


# `functools.lru_cache` starts with 3.2
def cached_func(func):
    values = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str([args, kwargs])
        if key not in values:
            values[key] = func(*args, **kwargs)
        return values[key]
    return wrapper
