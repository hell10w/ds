from __future__ import unicode_literals
from logging import getLogger
from pprint import pprint
import sys

from ds.command import Command
from ds.command import preset_base_command
from ds.utils.term import get_tty_width


logger = getLogger(__name__)


class DockerCommand(Command):
    container_name_required = False
    image_name_required = False

    weight = preset_base_command()

    @property
    def is_exists(self):
        return self.context.container is not None

    @property
    def is_running(self):
        return self.is_exists and \
               self.context.container.status == 'running'

    def ensure_running(self):
        if not self.is_running:
            logger.error('Container is not running')
            return
        return True


class Pull(DockerCommand):
    image_name_required = True

    short_help = 'Pull an image from a registry'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        self.context.executor.append([
            ('docker', 'pull'),
            self.context.image_name,
        ])


class Build(DockerCommand):
    image_name_required = True

    short_help = 'Build an image'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        self.context.executor.append([
            ('docker', 'build'),
            ('-t', self.context.image_name),
            ('-f', self.context.docker_file) if self.context.docker_file else (),
            self.context.build_path if self.context.build_path else (),
        ])


class ShowRunOptions(DockerCommand):
    container_name_required = True
    image_name_required = True

    usage = '[<args>...]'
    short_help = ''
    consume_all_args = True

    hidden = True

    weight = preset_base_command()

    def invoke_with_args(self, args):
        options = self.context. \
            get_run_options(image=self.context.image_name,
                            name=self.context.container_name,
                            command=args if args else None)
        pprint(options, width=get_tty_width())


class Create(DockerCommand):
    container_name_required = True
    image_name_required = True

    usage = '[<args>...]'
    short_help = 'Create a container'
    consume_all_args = True

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if self.is_exists:
            logger.error('Container exists already')
            sys.exit(1)

        command = list(self.context.container_entry) + \
                  list(args or self.context.container_cmd)

        options = self.context. \
            get_run_options(image=self.context.image_name,
                            name=self.context.container_name,
                            command=command if command else None)

        if self.is_exists:
            if self.context.remove_before_start:
                logger.debug('Remove a container')
                self.context.rm()
            else:
                logger.error('Container exists')
                return options, self.context.container

        logger.debug('Create a container with %s', options)

        container = self.context.client.containers.create(**options)
        logger.debug('%s created', container.id)

        return options, container


class Start(DockerCommand):
    container_name_required = True
    image_name_required = True

    usage = '[<args>...]'
    short_help = 'Start a container'
    consume_all_args = True

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if self.is_running:
            if self.context.stop_before_start:
                logger.debug('Store a container')
                self.context.stop()
            else:
                logger.error('Container is running already')
                sys.exit(1)

        options, container = self.context.create(args)

        if options.get('detach', False):
            container.start()
            self.context.logs()
        else:
            self.context.attach()


class Stop(DockerCommand):
    container_name_required = True

    short_help = 'Stop a container'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if not self.is_running:
            logger.error('Container is not working')
            return
        logger.error('Stop a container')
        self.context.container.stop()


class Restart(DockerCommand):
    container_name_required = True
    image_name_required = True

    short_help = 'Restart a container'
    usage = '[<args>...]'
    consume_all_args = True

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if self.is_running:
            self.context.stop()
        self.context.start(args)


class Recreate(DockerCommand):
    container_name_required = True
    image_name_required = True

    short_help = 'Recreate a container'
    usage = '[<args>...]'
    consume_all_args = True

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if self.is_running:
            self.context.stop()
        if self.is_exists:
            self.context.rm()
        self.context.start(args)


class Kill(DockerCommand):
    container_name_required = True

    short_help = 'Kill a container'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if self.context.container:
            self.context.container.kill()


class Rm(DockerCommand):
    container_name_required = True

    short_help = 'Remove a container'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if self.is_running:
            self.context.stop()
        if self.context.container:
            self.context.container.remove()


class Logs(DockerCommand):
    container_name_required = True

    short_help = 'Fetch the logs of a container'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if not self.ensure_running():
            return
        self.context.executor.append([
            ('docker', 'logs'),
            '--follow' if self.context.logs_follow else (),
            ('--tail', str(self.context.logs_tail)),
            self.context.container_name,
        ])


class Inspect(DockerCommand):
    container_name_required = True

    short_help = 'Return low-level information about a container'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if not self.ensure_running():
            return
        self.context.executor.append([
            ('docker', 'inspect'),
            self.context.container_name,
        ])


class Attach(DockerCommand):
    container_name_required = True

    short_help = 'Attach a local stdin/stdout to a container'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        if not self.is_exists:
            logger.error('Container doesn\'t exist')
            return

        print('Note: Press {} to detach'.format(self.context.detach_keys))

        if self.is_running:
            command = 'attach'
        else:
            command = ('start', '--attach', '--interactive')

        self.context.executor.append([
            'docker',
            command,
            ('--detach-keys', self.context.detach_keys),
            self.context.container_name,
        ])


class Exec(DockerCommand):
    container_name_required = True

    usage = 'usage: {name} <args>...'
    consume_all_args = True

    interactive = True
    tty = True

    weight = preset_base_command()

    @property
    def user(self):
        from .mixins import UserMixin
        user = None
        if isinstance(self.context, UserMixin):
            user = self.context.container_user
        return user

    @property
    def short_help(self):
        args = self.get_command()
        if args:
            return '`{}`'.format(' '.join(args))
        return 'Run a command in a container'

    def invoke_with_args(self, invoke_args):
        if not self.is_running:
            logger.error('Container isn\'t running')
            return

        args = self.format_args(invoke_args)

        self.context.executor.append([
            ('docker', 'exec'),
            '-i' if self.interactive else (),
            '-t' if self.tty else (),
            ('-u', str(self.user)) if self.user is not None else (),
            self.context.container_name,
            args,
        ])

    def format_args(self, invoke_args):
        result = list(self.get_command()) + list(invoke_args)
        assert result, 'No arguments for exec'
        return result

    def get_command(self):
        return ()


class Shell(Exec):
    container_name_required = True

    weight = preset_base_command()

    user = None

    @property
    def short_help(self):
        shell = self.context.shell_entry
        user = self.user
        if user is None:
            user = self.context.container_user
        return 'Run {} in a container with uid={}'.\
            format(shell, user if user is not None else '*unfilled*')

    def get_command(self):
        return self.context.shell_entry,


class RootShell(Shell):
    container_name_required = True

    weight = preset_base_command()

    user = 0
