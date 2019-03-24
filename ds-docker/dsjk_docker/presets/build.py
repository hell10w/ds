from __future__ import unicode_literals

from dsjk_docker.presets.base import BuildContext
from dsjk_docker.presets.base import DefaultNaming
from dsjk_docker.presets.base import UserMixin
from dsjk_docker.presets.base import HomeMountsMixin
from dsjk_docker.presets.base import ProjectMountMixin


class Context(ProjectMountMixin, UserMixin, HomeMountsMixin,
              DefaultNaming, BuildContext):
    pass
