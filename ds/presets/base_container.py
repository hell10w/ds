import os
from logging import getLogger
from os.path import exists
from os.path import expanduser
from os.path import join

from ds import context
from ds import text
from ds.command import Command

logger = getLogger(__name__)

_DS_SIGN_LABEL = 'ds.opts'


class Naming(object):
    @property
    def image_name(self):
        return text.join_not_empty('/', self.prefix, self.project_name)

    @property
    def container_name(self):
        return text.sanitize_text(self.image_name)


class PrefixedNaming(Naming):
    prefix = None

    @property
    def image_name(self):
        return text.join_not_empty('/', self.prefix, self.project_name)

    @property
    def container_name(self):
        image_name = self.image_name.split(':', 1)[0]
        return text.join_not_empty('--', self.prefix,
                                   text.sanitize_text(image_name))


class ProjectPrefixedNaming(PrefixedNaming):
    @property
    def prefix(self):
        return self.project_name


class DockerContext(Naming, context.Context):
    mount_project_root = True
    working_dir = '/work/'
    home = '/'

    remove_on_stop = True

    detach = False
    detach_keys = 'ctrl-c'

    restart = 'no'

    logs_tail = 100

    shell = '/bin/bash'

    networks = ()

    environment = {}

    def get_all_commands(self):
        return super(DockerContext, self).get_all_commands() + [
            Status,
            Ps,
            Start,
            Up,
            Stop,
            Down,
            Restart,
            Recreate,
            Rm,
            Logs,
            Attach,
            Exec,
            Shell,
            RootShell,
            Inspect,
            ShowNetworks,
        ]

    @property
    def uid(self):
        return os.getuid()

    #  @property
    #  def gid(self):
    #      return None  #  os.getgid()

    def get_mounts(self):
        result = []
        for dest in text.safe_list(self.home):
            if not dest:
                continue
            result.extend([
                HomeMount('.bashrc', dest),
                HomeMount('.inputrc', dest),
                HomeMount('.config/bash', dest),
                HomeMount('.psqlrc', dest),
                HomeMount('.liquidpromptrc', dest),
            ])
        if self.mount_project_root:
            dest = self.working_dir or '/project/'
            result.append(Mount(self.project_root, dest))
        return result

    @property
    def mounts(self):
        result = []
        for mount in self.get_mounts():
            realized = mount(self)
            if not realized:
                continue
            result.append(realized)
        return result

    def on_startup(self):
        self.logs()


class Mount(object):
    def __init__(self, src, dest, mode='rw'):
        self.src = src
        self.dest = dest
        self.mode = mode

    def __call__(self, context):
        return (self.src, self.dest, self.mode)


class HomeMount(Mount):
    def __call__(self, context):
        src = expanduser(join('~', self.src))
        if not exists(src):
            return
        dest = join(self.dest, self.src)
        return (src, dest, self.mode)


class _InspectData(object):
    def __init__(self, data):
        self._raw_data = data
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = text.safe_loads(self._raw_data, 0)
        return self._data

    @property
    def is_running(self):
        return text.safe_dict_path(
            self.data, 'State', 'Running', default=False)

    @property
    def is_present(self):
        return text.safe_dict_path(self.data, 'State')

    @property
    def labels(self):
        return text.safe_dict_path(self.data, 'Config', 'Labels', default={})

    @property
    def signature(self):
        return self.labels.get(_DS_SIGN_LABEL, None)

    @property
    def container_id(self):
        return text.safe_dict_path(self.data, 'id')


class DockerCommand(Command):
    def _format_running_status(self, is_running):
        state = {
            True: 'running',
            False: 'not running',
        }[is_running]
        return 'Container is {}'.format(state)

    def ensure_running_state(self, expected=True):
        is_running = self.inspect_data.is_running
        if is_running != expected:
            logger.error(self._format_running_status(is_running))
            return False
        return True

    def ensure_present(self):
        if not self.inspect_data.is_present:
            return False
        return True

    @property
    def current_signature(self):
        return self.inspect_data.signature

    @property
    def inspect_data(self):
        data = getattr(self.context, '_inspect_data', None)

        if not data or not self.context.executor.is_empty_queue:
            self.context.executor.append([
                ('docker', 'inspect'),
                self.context.container_name,
            ])
            result = self.context.executor.commit()
            data = _InspectData(result.stdout)
            setattr(self.context, '_inspect_data', data)

        return data


class _Start(DockerCommand):
    usage = 'usage: {name} [<args>...]'
    short_help = 'Start a container'
    consume_all_args = True

    def _collect_opts(self):
        return (
            '-it',
            '-d' if self.context.detach else (),
            '--rm' if self.context.remove_on_stop else (),
            [('--network', network) for network in self.context.networks],
            ('-u', '{}'.format(self.context.uid))
            if self.context.uid is not None else (),
            [('-e', '='.join([key, value]))
             for key, value in self.context.environment.items()],
            [('-v', ':'.join(mountpoint))
             for mountpoint in self.context.mounts],
            ('-w', self.context.working_dir)
            if self.context.working_dir else (),
            ('--restart', self.context.restart)
            if self.context.restart else (),
        )

    def invoke_with_args(self, args):
        if args and self.context.detach:
            logger.error(
                '`detach` is enabled. Arguments for `start` is not allowed in this case.'
            )
            return

        opts = self._collect_opts()
        signature = text.signature(list(opts) + list(args))

        logger.debug('Previous signature is %s, current is %s',
                     self.current_signature, signature)

        changed = self.inspect_data.is_present and \
            self.current_signature != signature
        if changed:
            logger.warning('Recreate with updated context')
            self.context.recreate(args)
            return

        if self.inspect_data.is_running:
            logger.warning('Container is working')

        else:
            if self.inspect_data.is_present:
                if self.context.detach:
                    self.context.executor.append([
                        ('docker', 'start'),
                        self.context.container_name,
                    ])
                else:
                    logger.warning(
                        'Recreate because the container presents and is not working'
                    )
                    self.context.recreate(args)
                    return

            else:
                self.context.executor.append([
                    ('docker', 'run'),
                    opts,
                    ('-l', '='.join([_DS_SIGN_LABEL, signature])),
                    ('--name', self.context.container_name),
                    self.context.image_name,
                    args,
                ])

        if self.context.detach:
            self.context.on_startup()


class Start(_Start):
    hidden = True


class Up(_Start):
    pass


class _Stop(DockerCommand):
    short_help = 'Stop a container'

    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        self.context.executor.append([
            ('docker', 'stop'),
            self.context.container_name,
        ])


class Stop(_Stop):
    hidden = True


class Down(_Stop):
    pass


class Recreate(DockerCommand):
    short_help = 'Recreate a container'
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if self.inspect_data.is_running:
            self.context.stop()
        if self.inspect_data.is_present:
            self.context.rm()
        self.context.start(args)


class Restart(DockerCommand):
    short_help = 'Restart a container'
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if self.inspect_data.is_running:
            self.context.stop()
        self.context.start(args)


class Rm(DockerCommand):
    short_help = 'Remove a container'

    def invoke_with_args(self, args):
        if self.inspect_data.is_running:
            self.context.stop()
        self.context.executor.append([
            ('docker', 'rm'),
            self.context.container_name,
        ])


class Attach(DockerCommand):
    short_help = 'Attach a local stdin/stdout to a container'

    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        print('Note: Press {} to dettach'.format(self.context.detach_keys))
        self.context.executor.append([
            ('docker', 'attach'),
            ('--detach-keys', self.context.detach_keys),
            self.context.container_name,
        ])


class Inspect(DockerCommand):
    short_help = 'Return low-level information on Docker objects'
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if not self.ensure_present():
            return
        self.context.executor.append([
            ('docker', 'inspect'),
            args,
            self.context.container_name,
        ])


class ShowNetworks(DockerCommand):
    short_help = 'Show a networks info of a container'
    usage = 'usage: {name}'
    consume_all_args = True

    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        self.context.executor.append([
            ('docker', 'inspect'),
            ('-f', '{{json .NetworkSettings.Networks }}'),
            self.context.container_name,
        ])


class Status(DockerCommand):
    short_help = 'Show a short summary of container\'s status'

    def invoke_with_args(self, args):
        is_running = self.inspect_data.is_running
        print(self._format_running_status(is_running))


class Ps(Status):
    short_help = 'same as `status`'
    hidden = True


class Logs(DockerCommand):
    short_help = 'Fetch the logs of a container'

    def invoke_with_args(self, args):
        if not self.ensure_running_state():
            return
        self.context.executor.append([
            ('docker', 'logs'),
            '--follow',
            ('--tail', str(self.context.logs_tail)),
            self.context.container_name,
        ])


class Exec(DockerCommand):
    usage = 'usage: {name} <args>...'
    consume_all_args = True

    user = None

    @property
    def short_help(self):
        args = self.get_command_args()
        if args:
            return '`{}`'.format(' '.join(args))
        return 'Run a command in a container'

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
    @property
    def short_help(self):
        shell = self.context.shell
        uid = self.context.uid
        if self.user is not None:
            uid = self.user
        return 'Run {} in a container with uid {}'.format(shell, uid)

    def get_command_args(self):
        return self.context.shell,


class RootShell(Shell):
    user = 0

    def get_command_args(self):
        return self.context.shell,
