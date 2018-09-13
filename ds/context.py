from weakref import ref

from ds import fs
from ds.command import __complete


class BaseContext(object):
    def __init__(self, flow):
        self._flow = ref(flow)

    @property
    def flow(self):
        return self._flow()

    #  def get_commands(self):
    #      return [
    #          __complete,
    #      ]


class Context(BaseContext):
    def get_project_root(self):
        return fs.get_project_root()

    @property
    def project_root(self):
        return self.get_project_root()

    def get_project_name(self):
        return fs.get_project_name()

    @property
    def project_name(self):
        return self.get_project_name()
