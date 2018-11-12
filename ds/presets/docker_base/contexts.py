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
                    BaseDockerContext):
    """"""

    stop_before_start = True
    remove_before_start = True

    detach_keys = 'ctrl-c'

    logs_tail = 100

    def get_commands(self):
        predicate = lambda command: command.is_appropriate_for_context(self)
        default = [
            commands.ShowRunOptions,
            commands.Create,
            commands.Start,
            commands.Stop,
            commands.Recreate,
            commands.Restart,
            commands.Kill,
            commands.Inspect,
            commands.Rm,
            commands.Logs,
            commands.Attach,
            commands.Exec,
        ]
        return super(DockerContext, self).get_commands() + \
               list(filter(predicate, default))

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
