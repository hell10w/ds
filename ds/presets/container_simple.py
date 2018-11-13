from __future__ import unicode_literals
import os

from ds.presets.docker_base import PullContext
from ds.presets.docker_base import DefaultNaming
from ds.presets.docker_base import UserMixin
from ds.presets.docker_base import HomeMountsMixin
from ds.presets.docker_base import ProjectMountMixin


class Context(ProjectMountMixin, UserMixin, HomeMountsMixin,
              DefaultNaming, PullContext):
    @property
    def default_image(self):
        return os.environ.get('IMAGE', 'debian')
