class _Network(object):
    name = None

    def __init__(self, name=None):
        self.name = name


class NoneNetwork(_Network):
    name = 'none'
    driver = None


class HostNetwork(_Network):
    name = 'host'
    driver = 'host'


class BridgeNetwork(_Network):
    name = None
    driver = 'bridge'
