import os

from ds import context
from ds import fs


class Context(context.Context):
    @property
    def home(self):
        return fs.users_home()

    def get_project_root(self):
        return fs.find_project_root()

    @property
    def project_root(self):
        return self.get_project_root()

    @property
    def pwd(self):
        return fs.get_pwd()

    def get_uid(self):
        return os.getuid()

    @property
    def uid(self):
        return self.get_uid()
