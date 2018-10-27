from os import makedirs
from os.path import exists
from os.path import dirname
from os.path import join
import json
from logging import getLogger

from cachetools import cached

from ds.path import pwd


logger = getLogger(__name__)


class BaseEnvironment(object):
    def __init__(self):
        self._data = None

    @property
    @cached({})
    def environment_filename(self):
        result = self.get_environment_filename()
        return result

    def get_environment_filename(self):
        raise NotImplementedError

    def load(self):
        filename = self.environment_filename
        if not exists(filename):
            self._data = {}
            return
        with open(filename, 'r') as file:
            try:
                self._data = json.load(file)
            except ValueError:
                self._data = {}

    def save(self):
        filename = self.environment_filename
        logger.debug('Save data to %s', filename)
        path = dirname(filename)
        if not exists(path):
            makedirs(path)
        with open(filename, 'w') as file:
            json.dump(self._data, file)

    @property
    def data(self):
        if self._data is None:
            self.load()
        return self._data

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def invalidate(self):
        self._data = None


# class TempEnvironment(BaseEnvironment):
#     def get_environment_filename(self):
#         ppid = os.getppid()
#         return '/tmp/ds/{}.json'.format(ppid)


# class TopEnvironment(BaseEnvironment):
#     env_filename = '.ds-env'
#
#     def get_environment_filename(self):
#         return join(find_for(self.env_filename), self.env_filename)


class PwdEnvironment(BaseEnvironment):
    env_filename = '.ds-env'

    def get_environment_filename(self):
        return join(pwd(), self.env_filename)


@cached({})
def get_environment():
    return PwdEnvironment()
