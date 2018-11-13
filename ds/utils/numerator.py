def numerator(start):
    def inner():
        inner.counter += 1
        return inner.counter
    inner.counter = start
    return inner
