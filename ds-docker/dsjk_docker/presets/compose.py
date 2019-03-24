import os
import sys
from logging import getLogger
from os import getcwd
from os.path import join

from ds.command import Command
from ds.context import Context as _Context
from ds.environment import get_environment
from ds.summary import TableSummary
from ds.utils import flatten, drop_empty


logger = getLogger('compose')


class Context(_Context):
    compose_bin = 'docker-compose'
    compose_verbose = False

    logs_default = (
        '--follow',
        '--tail=100',
    )

    default_shell = '/bin/bash'

    def get_commands(self):
        return super(Context, self).get_commands() + [
            Compose,
            Switch,
            Config,
            Build,
            Up,
            Down,
            Start,
            Stop,
            Rm,
            Logs,
            Ps,
            Restart,
            Kill,
            Exec,
            Shell,
            RootShell,
            Recreate,
        ]

    def get_environment_variables(self, **kwargs):
        result = {
            'project_root': self.project_root,
            'project_name': self.project_name,
            'user': os.getuid(),
        }
        result.update(kwargs)
        return result

    @property
    def environment_variables(self):
        return self.get_environment_variables()

    def get_compose_files(self):
        return 'compose.yml',

    @property
    def compose_files(self):
        return self.get_compose_files()

    def get_current_services(self):
        return get_environment().get('current_services', None)

    def set_current_services(self, value):
        logger.debug('Set services: %s', value)
        get_environment().set('current_services', value)

    current_services = property(get_current_services, fset=set_current_services)

    @property
    def all_services(self):
        self.invoke_compose((
            'config',
            '--services',
        ))
        result = self.executor.commit()
        return result.stdout.strip().split()

    def get_compose_options(self):
        return (
            self.compose_bin,
            '--verbose' if self.compose_verbose else (),
            ('--project-directory', self.project_root),
            ('--project-name', self.project_name),
            [
                ('-f', filename)
                for filename in self.compose_files
            ],
        )

    @property
    def env_filename(self):
        return join(self.project_root, '.env')

    def update_env_file(self):
        with open(self.env_filename, 'w') as output:
            output.writelines([
                '{}={}\n'.format(k, v)
                for k, v in self.environment_variables.items()
            ])

    def invoke_compose(self, args):
        self.update_env_file()
        options = drop_empty(flatten((
            self.get_compose_options(),
            args,
        )))
        self.executor.append(options)

    def switch_current_service(self, allow_all=False):
        all_option = '(all)'
        services = self.all_services

        if allow_all:
            services = [all_option] + services

        result = self.executor.fzf(services, multi=allow_all)
        if not result:
            return

        if not allow_all:
            result = (result, )

        if all_option in result:
            result = None

        self.current_services = result

        return result

    def get_additional_summary(self):
        cells = [
            ['Files', repr(self.compose_files)],
            ['Services', repr(self.current_services or '(all)')],
        ]
        return super(Context, self).get_additional_summary() + [
            TableSummary('Compose', cells),
        ]

    def check(self):
        if getcwd() != self.project_root:
            logger.warning('Current directory is not project\'s root')
        super(Context, self).check()


class Switch(Command):
    consume_all_args = True

    def invoke_with_args(self, args):
        if not args:
            self.context.switch_current_service(allow_all=True)
            return

        services = set(self.context.all_services)
        if set(args) != {'.'}:
            services &= set(args)
        self.context.current_services = list(services)


class Recreate(Command):
    consume_all_args = False

    def invoke_with_args(self, args):
        logger.info('Rebuild')
        self.context['build']()

        logger.info('Stop')
        self.context['stop']()

        logger.info('Remove')
        self.context['rm']('-f')

        logger.info('Up and detach')
        self.context['up']('-d')

        logger.info('Logs')
        self.context['logs']()


class ComposeCommand(Command):
    consume_all_args = True
    compose_command = None
    allow_multiple = True
    with_services = True
    prepend_args = False
    with_command_name = True
    forced_service = None

    def get_services(self):
        if self.forced_service:
            return self.forced_service,
        services = self.context.current_services
        if not services and not self.allow_multiple:
            services = self.context.switch_current_service()
            if services is None:
                sys.exit(1)
        return filter(lambda value: value, services or ())

    def get_command_options(self, args):
        return args if self.prepend_args else ()

    def get_command_args(self, args):
        return args if not self.prepend_args else ()

    def invoke_with_args(self, args):
        options = drop_empty(flatten((
            (self.compose_command or self.get_name()) if self.with_command_name else (),
            self.get_command_options(args),
            self.get_services() if self.with_services else (),
            self.get_command_args(args),
        )))
        self.context.invoke_compose(options)


class Compose(ComposeCommand):
    with_services = False
    with_command_name = False


class Config(ComposeCommand):
    with_services = False
    prepend_args = False


class Build(ComposeCommand):
    pass


class Up(ComposeCommand):
    prepend_args = True


class Down(ComposeCommand):
    pass


class Rm(ComposeCommand):
    allow_multiple = False
    prepend_args = True


class Logs(ComposeCommand):
    prepend_args = True

    def get_command_options(self, args):
        return args or self.context.logs_default


class Ps(ComposeCommand):
    with_services = False


class Restart(ComposeCommand):
    pass


class Kill(ComposeCommand):
    pass


class Start(ComposeCommand):
    allow_multiple = False


class Stop(ComposeCommand):
    allow_multiple = False


class Exec(ComposeCommand):
    compose_command = 'exec'
    allow_multiple = False


class Shell(Exec):
    user = None

    def get_command_args(self, args):
        return args or self.context.default_shell,

    def get_command_options(self, args):
        return (
            ('--user={}'.format(self.user)) if self.user is not None else (),
        )


class RootShell(Shell):
    user = 0
