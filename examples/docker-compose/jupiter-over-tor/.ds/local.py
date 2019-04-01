from __future__ import unicode_literals

from logging import getLogger
from os.path import exists
from os.path import join
from os import makedirs
from os import chmod

from ds.command import Command
from dsjk_docker.presets.compose import Context as _Context


logger = getLogger()


class Context(_Context):
    compose_files = [
        'docker/compose-generic.yml',
        'docker/compose-jupiter.yml',
    ]

    network_subnet = '172.180.0.0/24'
    nginx_ip = '172.180.0.100'

    ensure_paths = (
        'jupiter-datascience',
        'jupiter-tensorflow',
    )

    def get_environment_variables(self, **kwargs):
        kwargs.update(dict(
            network_subnet=self.network_subnet,
            nginx_ip=self.nginx_ip,
        ))
        return super(Context, self).get_environment_variables(**kwargs)

    def get_commands(self):
        return [
            SwitchLocal,
            SwitchRemote,
        ] + super(Context, self).get_commands()

    def check(self):
        for data_path in self.ensure_paths:
            permissions = None
            if isinstance(data_path, tuple):
                data_path, permissions = data_path
            path = join('.data', data_path)
            if not exists(path):
                logger.info('Create path %s', path)
                makedirs(path)
                if permissions:
                    logger.info('Change permissions to %s for %s', permissions, path)
                    chmod(path, permissions)
        super(Context, self).check()


class SwitchCommand(Command):
    switch_to = None

    def invoke_with_args(self, args):
        executor = self.context.executor
        with executor.chain(path='.ds', skip_stdout=True) as chain:
            chain.append('ln', '-sf', self.switch_to, 'default.py')


class SwitchLocal(SwitchCommand):
    switch_to = 'local.py'


class SwitchRemote(SwitchCommand):
    switch_to = 'remote.py'
