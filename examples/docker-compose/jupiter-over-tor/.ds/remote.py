from __future__ import unicode_literals

from getpass import getpass

from ds.command import Command
from dsjk_docker.presets.compose import Shell
from local import Context as _Context
try:
    input = raw_input
except NameError:
    pass


class Context(_Context):
    compose_files = _Context.compose_files + [
        'docker/compose-production.yml',
    ]
    ensure_paths = _Context.ensure_paths + (
        ('tor', 0o700),
    )

    def get_commands(self):
        return super(Context, self).get_commands() + [
            TorHostname,
            PasswdRecreate,
        ]


class TorHostname(Shell):
    user = None
    forced_service = 'tor'

    def get_command_args(self, args):
        return 'cat', '/var/lib/tor/hidden_service/hostname'


class PasswdRecreate(Command):
    def invoke_with_args(self, args):
        username = input('Username: ')
        password = getpass('Password: ')

        executor = self.context.executor
        with executor.chain(path='docker/nginx/') as chain:
            chain.append('htpasswd', '-cb', './nginx.htpasswd', username, password)
