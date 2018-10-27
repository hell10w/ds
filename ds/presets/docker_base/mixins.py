import os
from os.path import exists
from os.path import expanduser
from os.path import join

from docker.types import Mount

from .contexts import DockerContext


class UserMixin(DockerContext):
    @property
    def container_user(self):
        return os.getuid()

    def get_run_options(self, **options):
        return super(UserMixin, self).\
            get_run_options(user=self.container_user, **options)


class HomeMountsMixin(DockerContext):
    container_home = '/',

    home_mounts = [
        '.bashrc',
        '.inputrc',
        '.config/bash',
        '.psqlrc',
        '.liquidpromptrc',
    ]

    def get_mounts(self):
        additional = []
        for src in self.home_mounts:
            full_src = expanduser(join('~', src))
            if not exists(full_src):
                continue
            for container_home in self.container_home:
                full_dest = join(container_home, src)
                mount = Mount(target=full_dest,
                              source=full_src,
                              type='bind',
                              read_only=True)
                additional.append(mount)
        return super(HomeMountsMixin, self).get_mounts() + additional


class ProjectMountMixin(DockerContext):
    working_dir = '/app/'

    @property
    def project_mount_path(self):
        return self.project_root

    @property
    def project_mount_readonly(self):
        return False

    def get_run_options(self, **options):
        return super(ProjectMountMixin, self). \
            get_run_options(working_dir=self.working_dir, **options)

    def get_mounts(self):
        mount = Mount(target=self.working_dir,
                      source=self.project_mount_path,
                      type='bind',
                      read_only=self.project_mount_readonly)
        return super(ProjectMountMixin, self).get_mounts() + [mount]
