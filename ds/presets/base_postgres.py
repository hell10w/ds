from os.path import join

from ds import text
from base_container import DockerContext
from base_container import Exec
from base_container import Mount
from base_pull import Context as PullContext


class PostgresContext(DockerContext):
    """
    https://hub.docker.com/_/postgres/
    """

    home = '/root/', '/var/lib/postgresql/',

    pg_user = 'postgres'
    pg_password = pg_user
    pgdata = '/var/lib/postgresql/data/'

    def get_all_commands(self):
        return super(PostgresContext, self).get_all_commands() + [
            Psql,
            Pg_dump,
            Pg_restore,
        ]

    @property
    def environment(self):
        result = super(PostgresContext, self).environment
        text.append_value(result, 'PG_USER', self.pg_user)
        text.append_value(result, 'PG_PASSWORD', self.pg_password)
        text.append_value(result, 'PGDATA', self.pgdata)
        return result

    def get_mounts(self):
        result = super(PostgresContext, self).get_mounts()
        if self.data_mount:
            result.append(Mount(self.data_mount, self.pgdata))
        return result

    @property
    def uid(self):
        return self.pg_user or 'postgres'

    @property
    def data_mount(self):
        return join(self.project_root, '.data', 'postgres')


class PostgresExec(Exec):
    user = 'postgres'


class Psql(PostgresExec):
    def get_command_args(self):
        return 'psql',


class Pg_dump(PostgresExec):
    def get_command_args(self):
        return 'pg_dump',


class Pg_restore(PostgresExec):
    def get_command_args(self):
        return 'pg_restore',
