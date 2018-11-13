from __future__ import unicode_literals
from logging import getLogger

import docker
import docker.errors

from ds import context
from . import naming


logger = getLogger()


class BaseDockerContext(naming.ContainerNaming, context.Context):
    def __init__(self):
        super(BaseDockerContext, self).__init__()
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = docker.from_env()
        return self._client

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
        )
        result.update(options)
        return result

    def filter_commands(self, commands):
        result = []
        for command in commands:
            if command.container_name_required and not self.has_container_name:
                logger.debug('Filter command %s', command)
                continue
            if command.image_name_required and not self.has_image_name:
                logger.debug('Filter command %s', command)
                continue
            result.append(command)
        return super(BaseDockerContext, self).filter_commands(result)
