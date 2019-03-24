from __future__ import unicode_literals

from ds.summary import TableSummary
from .base import BaseDockerContext
from . import commands
from . import naming
from . import mixins


UNDEFINED = '(undefined)'


class DockerContext(mixins.MountsMixin, mixins.EnvironmentMixin,
                    mixins.NetworkMixin, mixins.ShellMixin,
                    mixins.LogsMixin, mixins.AttachMixin,
                    mixins.ManageContainerMixin,
                    BaseDockerContext):
    def get_additional_summary(self):
        container = self.container

        container_name = '-'
        if self.has_container_name:
            container_name = self.container_name
        image_name = '-'
        if self.has_image_name:
            image_name = self.image_name

        cells = [
            ['Name', container_name or UNDEFINED],
            ['Image', image_name or UNDEFINED],
            ['Status', container.status if container else '-'],
            ['ID', container.short_id if container else '-'],
        ]

        return super(DockerContext, self).get_additional_summary() + [
            TableSummary('Container', cells),
        ]


class ExternalContext(DockerContext):
    pass


class BuildContext(naming.BuildNaming, mixins.CreateContainerMixin,
                   DockerContext):
    def get_commands(self):
        return super(BuildContext, self).get_commands() + [
            commands.Build,
        ]

    def get_build_path(self):
        return self.project_root

    @property
    def build_path(self):
        return self.get_build_path()

    def get_docker_file(self):
        return 'Dockerfile'

    @property
    def docker_file(self):
        return self.get_docker_file()


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
