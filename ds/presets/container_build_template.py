from __future__ import unicode_literals

from ds.presets.docker_base import BuildContext
from ds.presets.docker_base import DefaultNaming
from ds.presets.docker_base import UserMixin
from ds.presets.docker_base import HomeMountsMixin
from ds.presets.docker_base import ProjectMountMixin


class ContainerBuildContext(ProjectMountMixin, UserMixin, HomeMountsMixin,
                            DefaultNaming, BuildContext):
    pass
