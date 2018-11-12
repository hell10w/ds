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
from ds.utils import drop_empty
from ds.presets.docker_base import commands
from .base import BaseDockerContext
from . import naming
from . import mixins


class DockerContext(mixins.MountsMixin, mixins.EnvironmentMixin,
                    BaseDockerContext):
    """"""

    stop_before_start = True
    remove_before_start = True

    detach_keys = 'ctrl-c'

    logs_tail = 100

    def get_commands(self):
        return super(DockerContext, self).get_commands() + drop_empty(
            commands.ShowRunOptions if self.has_image_name else None,
            commands.Create if self.has_image_name else None,
            commands.Start if self.has_image_name else None,
            commands.Stop if self.has_container_name else None,
            commands.Recreate if self.has_image_name else None,
            commands.Restart if self.has_image_name else None,
            commands.Kill if self.has_container_name else None,
            commands.Inspect if self.has_container_name else None,
            commands.Rm if self.has_container_name else None,
            commands.Logs if self.has_container_name else None,
            commands.Attach if self.has_container_name else None,
            commands.Exec if self.has_container_name else None,
            commands.Shell if self.has_container_name else None,
            commands.RootShell if self.has_container_name else None,
        )

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

    def get_base_container_command(self):
        return []

    @property
    def base_container_command(self):
        return self.get_base_container_command()

    def get_default_container_command(self):
        return []

    @property
    def default_container_command(self):
        return self.get_default_container_command()


class ExternalContext(DockerContext):
    pass


class BuildContext(naming.ImageNaming, DockerContext):
    def get_commands(self):
        return super(BuildContext, self).get_commands() + [
            commands.Build,
        ]


class PullContext(naming.ImageNaming, DockerContext):
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
