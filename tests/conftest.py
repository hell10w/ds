import pytest

from ds.environment import get_environment
from ds.executor import Executor


class Shell(object):
    def __init__(self):
        self._executor = Executor()

    def call(self, *args, **options):
        get_environment().invalidate()
        self._executor.append(args, **options)
        return self._executor.commit()

    def call_ds(self, *args, **options):
        return self.call(*(('python', '-m', 'ds') + args), **options)

    def call_docker_ds(self, *args, **options):
        options.setdefault('skip_stdin', True)
        return self.call_ds(*args, **options)


@pytest.fixture(scope='module')
def shell():
    yield Shell()
