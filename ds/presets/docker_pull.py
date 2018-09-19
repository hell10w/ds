from os import environ

from docker_generic import DockerContext, Pull


class Context(DockerContext):
    image_name = environ.get('DS_IMAGE') or 'debian:latest'

    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Pull,
        ]
