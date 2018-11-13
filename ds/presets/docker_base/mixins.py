import os
from os.path import exists
from os.path import expanduser
from os.path import join

from docker.types import Mount

from .base import BaseDockerContext
from . import commands


class AttachMixin(BaseDockerContext):
    detach_keys = 'ctrl-c'

    def get_commands(self):
        return super(AttachMixin, self).get_commands() + [
            commands.Attach,
        ]


class ManageContainerMixin(BaseDockerContext):
    stop_before_start = True
    remove_before_start = True

    def get_commands(self):
        return super(ManageContainerMixin, self).get_commands() + [
            commands.Start,
            commands.Stop,
            commands.Restart,
            commands.Kill,
            commands.Rm,
            commands.Inspect,
            commands.Exec,
        ]


class CreateContainerMixin(ManageContainerMixin):
    def get_commands(self):
        return super(CreateContainerMixin, self).get_commands() + [
            commands.ShowRunOptions,
            commands.Create,
            commands.Recreate,
        ]

    def get_container_entry(self):
        return []

    def get_container_cmd(self):
        return []

    @property
    def container_entry(self):
        return self.get_container_entry()

    @property
    def container_cmd(self):
        return self.get_container_cmd()


class LogsMixin(BaseDockerContext):
    logs_tail = 100
    logs_follow = True

    def get_commands(self):
        return super(LogsMixin, self).get_commands() + [
            commands.Logs,
        ]


class ContainerUserMixin(BaseDockerContext):
    container_user = None

    def get_run_options(self, **options):
        return super(ContainerUserMixin, self). \
            get_run_options(user=self.container_user, **options)


class NetworkMixin(ContainerUserMixin):
    network = None

    def get_run_options(self, **options):
        return super(NetworkMixin, self). \
            get_run_options(network=self.network, **options)


class UserMixin(ContainerUserMixin):
    @property
    def container_user(self):
        return os.getuid()


class MountsMixin(BaseDockerContext):
    def get_run_options(self, **options):
        return super(MountsMixin, self).\
            get_run_options(mounts=self.get_mounts(), **options)

    def get_mounts(self):
        return []


class EnvironmentMixin(BaseDockerContext):
    container_environment = {}

    def get_run_options(self, **options):
        return super(EnvironmentMixin, self).\
            get_run_options(environment=self.get_environment(), **options)

    def get_environment(self):
        return self.container_environment


class HomeMountsMixin(MountsMixin):
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


class WorkingDirMixin(MountsMixin):
    working_dir = '/app/'

    def get_run_options(self, **options):
        return super(WorkingDirMixin, self). \
            get_run_options(working_dir=self.working_dir, **options)


class ProjectMountMixin(WorkingDirMixin):
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


class ShellMixin(ContainerUserMixin):
    shell_entry = '/bin/bash'

    def get_commands(self):
        return super(ShellMixin, self).get_commands() + [
            commands.Shell,
            commands.RootShell,
        ]
