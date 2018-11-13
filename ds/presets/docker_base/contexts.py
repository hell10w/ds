from __future__ import unicode_literals
import sys

try:
    import docker
    import docker.errors
    from docker.types import Mount
except ImportError:
    print('Install docker-py with `pip install docker`')
    sys.exit(1)

from ds.summary import TableSummary
from .base import BaseDockerContext
from . import commands
from . import naming
from . import mixins


class DockerContext(mixins.MountsMixin, mixins.EnvironmentMixin,
                    mixins.NetworkMixin, mixins.ShellMixin,
                    mixins.LogsMixin, mixins.AttachMixin,
                    mixins.ManageContainerMixin,
                    BaseDockerContext):
    def get_additional_summary(self):
        container = self.container
        cells = [
            ['Name', self.container_name or '-'],
            ['Image', self.image_name or '-'],
            ['Status', container.status if container else '-'],
            ['ID', container.short_id if container else '-'],
        ]
        return super(DockerContext, self).get_additional_summary() + [
            TableSummary('Container', cells),
        ]


class ExternalContext(DockerContext):
    pass


class BuildContext(naming.ImageNaming, mixins.CreateContainerMixin,
                   DockerContext):
    def get_commands(self):
        return super(BuildContext, self).get_commands() + [
            commands.Build,
        ]


class PullContext(naming.ImageNaming, mixins.CreateContainerMixin,
                  DockerContext):
    default_image = None
    default_tag = 'latest'

    def check(self):
        assert self.default_image, 'Default image is not set'
        super(PullContext, self).check()

    @property
    def image_name(self):
        if not self.default_image:
            return
        return ':'.join(filter(lambda value: value,
                               [self.default_image, self.default_tag]))

    def get_commands(self):
        return super(PullContext, self).get_commands() + [
            commands.Pull,
        ]
