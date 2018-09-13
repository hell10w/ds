import os
from os.path import exists, join, expanduser

from ds import context
from ds import fs


class DockerContext(context.Context):
    @property
    def container_name(self):
        return self.project_name

    prefix = 'ds'

    container_working_dir = '/app/'
    container_home = '/'

    rm = True
    detach = True

    @property
    def container_name(self):
        return self.project_name

    @property
    def image_name(self):
        return '/'.join([self.prefix, self.project_name])

    @property
    def container_name(self):
        return '--'.join([self.prefix, self.project_name])

    @property
    def container_uid(self):
        return os.getuid()

    @property
    def container_gid(self):
        return os.getgid()

    def get_mounts(self):
        result = []

        if self.container_home:
            result.extend([
                self._make_home_mount('.bashrc'),
                self._make_home_mount('.inputrc'),
                self._make_home_mount('.config/bash'),
                self._make_home_mount('.psqlrc'),
                self._make_home_mount('.liquidpromptrc'),
            ])

        if self.container_working_dir:
            result.append((self.project_root, self.container_working_dir, 'rw'))

        return [
            self._make_mount(item)
            for item in result
        ]

    @property
    def mounts(self):
        return [
            (src, dest, mode)
            for src, dest, mode in self.get_mounts()
            if exist(src)
        ])

    def _make_home_mount(self, src):
        return expanduser(join('~', src)), join(self.container_home, src)

    def _make_mount(self, src, dest, mode='ro'):
        return (src, dest, mode)


class DockerBuildContext(DockerContext):
    pass


class DockerPullContext(DockerContext):
    image_name = 'debian:latest'
