import os
from os.path import exists, join, expanduser
from logging import getLogger

from ds.command import Command
from ds import context
from ds import fs
from ds import text


logger = getLogger(__name__)


class DockerContext(context.Context):
    @property
    def container_name(self):
        return self.project_name

    prefix = 'ds'

    container_working_dir = '/app/'
    container_home = '/'

    container_rm = True

    container_detach = True
    container_detach_keys = 'ctrl-c'

    container_logs_tail = 100

    container_shell = '/bin/bash'

    def get_all_commands(self):
        return super(DockerContext, self).get_all_commands() + [
            Start,
            Stop,
            Restart,
            Rm,
            Logs,
            Attach,
            Exec,
            Shell,
            RootShell,
            Inspect,
            InspectNetworks,
        ]

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

    def get_container_mounts(self):
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
            self._make_mount(*item)
            for item in result
        ]

    @property
    def container_mounts(self):
        return [
            (src, dest, mode)
            for src, dest, mode in self.get_container_mounts()
            if exists(src)
        ]

    def _make_home_mount(self, src):
        return expanduser(join('~', src)), join(self.container_home, src)

    def _make_mount(self, src, dest, mode='ro'):
        return (src, dest, mode)


class _InspectData(object):
    def __init__(self, data):
        self._raw_data = data
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = text.safe_loads(self._raw_data)
        return self._data

    @property
    def is_running(self):
        return text.safe_dict_path(self.data, 'State', 'Running', default=False)


class _DockerCommand(Command):
    def ensure_running_state(self, expected=True):
        is_running = self.inspect_data.is_running
        if is_running != expected:
            state = {
                True: 'running',
                False: 'not running',
            }[is_running]
            logger.error('Container is %s', state)
            return False
        return True

    @property
    def inspect_data(self):
        self.context.executor.append([
            ('docker', 'inspect'),
            self.context.container_name,
        ])
        result = self.context.executor.commit()
        return _InspectData(result.stdout)


class Start(_DockerCommand):
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if not self.ensure_running_state(expected=False):
            return
        self.context.executor.append([
            ('docker', 'run'),
            '-it',
            '-d' if self.context.container_detach else (),
            '--rm' if self.context.container_rm else (),
            ('-u', '{}:{}'.format(self.context.container_uid, self.context.container_gid)) if self.context.container_uid is not None else (),
            [
                ('-v', ':'.join(mountpoint))
                for mountpoint in self.context.container_mounts
            ],
            ('-w', self.context.container_working_dir) if self.context.container_working_dir else (),
            ('--name', self.context.container_name),
            self.context.image_name,
            args,
        ])


class Stop(_DockerCommand):
    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        self.context.executor.append([
            ('docker', 'stop'),
            self.context.container_name,
        ])


class Restart(_DockerCommand):
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if self.inspect_data.is_running:
            self.context.stop()
        self.context.start(args)


class Rm(_DockerCommand):
    def invoke_with_args(self, args):
        if self.inspect_data.is_running:
            self.context.stop()
        self.context.executor.append([
            ('docker', 'rm'),
            self.context.container_name,
        ])


class Attach(_DockerCommand):
    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        print('Note: Press {} to dettach'.format(self.context.container_detach_keys))
        self.context.executor.append([
            ('docker', 'attach'),
            ('--detach-keys', self.context.container_detach_keys),
            self.context.container_name,
        ])


class Inspect(_DockerCommand):
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        self.context.executor.append([
            ('docker', 'inspect'),
            args,
            self.context.container_name,
        ])


class InspectNetworks(_DockerCommand):
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        self.context.executor.append([
            ('docker', 'inspect'),
            ('-f', '{{json .NetworkSettings.Networks }}'),
            self.context.container_name,
        ])


class Logs(_DockerCommand):
    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        self.context.executor.append([
            ('docker', 'logs'),
            '--follow',
            ('--tail', str(self.context.container_logs_tail)),
            self.context.container_name,
        ])


class Exec(_DockerCommand):
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    user = None

    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        args = list(self.get_command_args()) + list(args)
        assert args, 'No arguments for exec'
        self.context.executor.append([
            ('docker', 'exec'),
            '-it',
            ('-u', str(self.user)) if self.user is not None else (),
            self.context.container_name,
            args,
        ])

    def get_command_args(self):
        return ()


class Shell(Exec):
    def get_command_args(self):
        return self.context.container_shell,


class RootShell(Shell):
    user = 0

    def get_command_args(self):
        return self.context.container_shell,


class Build(_DockerCommand):
    def invoke_with_args(self, args):
        self.context.executor.append([
            ('docker', 'build'),
            self.context.image_name,
        ])


class Pull(_DockerCommand):
    def invoke_with_args(self, args):
        self.context.executor.append([
            ('docker', 'pull'),
            self.context.image_name,
        ])
