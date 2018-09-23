from os import environ

from docker_generic import DockerContext
from docker_generic import Pull


class Context(DockerContext):
    def get_image_name(self):
        return environ.get('DS_IMAGE') or 'debian:latest'

    @property
    def image_name(self):
        return self.get_image_name()

    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Pull,
        ]
