from __future__ import unicode_literals
import sys

try:
    import docker
    import docker.errors
    from docker.types import Mount
except ImportError:
    print('Install docker-py with `pip install docker`')
    sys.exit(1)

from ds import context
from ds.summary import TableSummary
from ds.utils import drop_empty
from ds.presets.docker_base import commands
from ds.presets.docker_base import naming


class DockerContextMixin(context.Context):
    def __init__(self):
        super(DockerContextMixin, self).__init__()
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = docker.from_env()
        return self._client


class DockerContext(naming.ContainerNaming, DockerContextMixin,
                    context.Context):
    """"""

    stop_before_start = True
    remove_before_start = True

    detach_keys = 'ctrl-c'

    logs_tail = 100

    def __init__(self):
        super(DockerContext, self).__init__()
        self._container = None

    def get_commands(self):
        return super(DockerContext, self).get_commands() + drop_empty(
            commands.ShowRunOptions if self.has_image_name else None,
            commands.Create if self.has_image_name else None,
            commands.Start if self.has_image_name else None,
            commands.Stop,
            commands.Recreate if self.has_image_name else None,
            commands.Restart if self.has_image_name else None,
            commands.Kill,
            commands.Rm,
            commands.Logs,
            commands.Attach,
            commands.Exec,
            commands.Shell,
            commands.RootShell,
        )

    @property
    def container(self):
        if not self.container_name:
            return
        try:
            return self.client.containers.get(self.container_name)
        except docker.errors.NotFound:
            pass

    def get_run_options(self, **options):
        """
        https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
        """
        result = dict(
            detach=False,
            auto_remove=True,
            stdin_open=True,
            tty=True,
            mounts=self.get_mounts(),
        )
        result.update(options)
        return result

    def get_mounts(self):
        return []

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
        return ':'.join([self.default_image, self.default_tag])

    def get_commands(self):
        return super(PullContext, self).get_commands() + [
            commands.Pull,
        ]
