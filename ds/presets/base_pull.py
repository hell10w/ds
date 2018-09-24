from os import environ

from base_container import DockerContext
from base_container import Pull


class Context(DockerContext):
    default_image = 'debian:latest'

    def get_image_name(self):
        return environ.get('DS_IMAGE') or self.default_image

    @property
    def image_name(self):
        return self.get_image_name()

    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Pull,
        ]
