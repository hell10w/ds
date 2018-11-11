#!/usr/bin/env ds
from os import environ

from base_container import DockerCommand
from base_container import DockerContext
from base_container import ProjectPrefixedNaming


class Context(DockerContext, ProjectPrefixedNaming):
    default_image = 'debian'
    default_tag = 'latest'

    def get_image_name(self):
        image = environ.get('DS_IMAGE') or self.default_image
        tag = environ.get('DS_TAG') or self.default_tag
        return ':'.join([image, tag])

    @property
    def image_name(self):
        return self.get_image_name()

    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Pull,
        ]


class Pull(DockerCommand):
    short_help = 'Pull an image'

    def invoke_with_args(self, args):
        self.context.executor.append([
            ('docker', 'pull'),
            self.context.image_name,
        ])
