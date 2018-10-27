from __future__ import unicode_literals
from logging import getLogger
from pprint import pprint
import sys

from ds.command import Command
from ds.utils.term import get_tty_width


logger = getLogger(__name__)


class DockerCommand(Command):
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


class ShowRunOptions(DockerCommand):
    usage = 'usage: {name} [<args>...]'
    short_help = ''
    consume_all_args = True
    hidden = True

    def invoke_with_args(self, args):
        options = self.context. \
            get_run_options(image=self.context.image_name,
                            name=self.context.container_name,
                            command=args if args else None)
        pprint(options, width=get_tty_width())


class Create(DockerCommand):
    usage = 'usage: {name} [<args>...]'
    short_help = 'Create a container'
    consume_all_args = True

    def invoke_with_args(self, args):
        if self.is_running:
            if self.context.stop_before_start:
                logger.debug('Store a container')
                self.context.stop()
            else:
                logger.error('Container is running already')
                sys.exit(1)

        options = self.context. \
            get_run_options(image=self.context.image_name,
                            name=self.context.container_name,
                            command=args if args else None)

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
    usage = 'usage: {name} [<args>...]'
    short_help = 'Start a container'
    consume_all_args = True

    def invoke_with_args(self, args):
        options, container = self.context.create(args)

        if options.get('detach', False):
            container.start()
            self.context.logs()
        else:
            self.context.attach()


class Stop(DockerCommand):
    short_help = 'Stop a container'

    def invoke_with_args(self, args):
        if not self.is_running:
            logger.error('Container is not working')
            return
        logger.error('Stop a container')
        self.context.container.stop()


class Restart(DockerCommand):
    short_help = 'Restart a container'
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if self.is_running:
            self.context.stop()
        self.context.start(args)


class Recreate(DockerCommand):
    short_help = 'Recreate a container'
    usage = 'usage: {name} [<args>...]'
    consume_all_args = True

    def invoke_with_args(self, args):
        if self.is_running:
            self.context.stop()
        if self.is_exists:
            self.context.rm()
        self.context.start(args)


class Kill(DockerCommand):
    short_help = 'Kill a container'

    def invoke_with_args(self, args):
        if self.context.container:
            self.context.container.kill()


class Rm(DockerCommand):
    short_help = 'Remove a container'

    def invoke_with_args(self, args):
        if self.is_running:
            self.context.stop()
        if self.context.container:
            self.context.container.remove()


class Logs(DockerCommand):
    short_help = 'Fetch the logs of a container'

    def invoke_with_args(self, args):
        if not self.ensure_running():
            return
        self.context.executor.append([
            ('docker', 'logs'),
            '--follow',
            ('--tail', str(self.context.logs_tail)),
            self.context.container_name,
        ])


class Attach(DockerCommand):
    short_help = 'Attach a local stdin/stdout to a container'

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
    pass


class Shell(Exec):
    pass


class RootShell(Exec):
    pass


class Pull(DockerCommand):
    pass


class Build(DockerCommand):
    pass
