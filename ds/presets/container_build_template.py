from __future__ import unicode_literals

from docker_base import BuildContext
from docker_base import DefaultNaming
from docker_base import UserMixin
from docker_base import HomeMountsMixin
from docker_base import ProjectMountMixin


class ContainerBuildContext(ProjectMountMixin, UserMixin, HomeMountsMixin,
                            DefaultNaming, BuildContext):
    pass
