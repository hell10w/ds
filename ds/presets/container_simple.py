from __future__ import unicode_literals
import os

from docker_base import PullContext
from docker_base import DefaultNaming
from docker_base import UserMixin
from docker_base import HomeMountsMixin
from docker_base import ProjectMountMixin


class Context(ProjectMountMixin, UserMixin, HomeMountsMixin,
              DefaultNaming, PullContext):
    @property
    def default_image(self):
        return os.environ.get('IMAGE', 'debian')
