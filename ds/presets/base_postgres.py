from ds import text
from base_container import DockerContext
from base_container import Exec
from base_pull import Context as PullContext


class PostgresContext(DockerContext):
    """
    https://hub.docker.com/_/postgres/
    """

    home = '/var/lib/postgresql/'

    pg_user = None  # default is `postgres`
    pg_password = None  # default same as $pg_user

    def get_all_commands(self):
        return super(PostgresContext, self).get_all_commands() + [
            Psql,
            Pg_dump,
            Pg_restore,
        ]

    @property
    def environment(self):
        environment = super(PostgresContext, self).environment
        text.append_value(environment, 'PG_USER', self.pg_user)
        text.append_value(environment, 'PG_PASSWORD', self.pg_password)
        return environment

    @property
    def uid(self):
        return self.pg_user or 'postgres'


class Context(PostgresContext, PullContext):
    default_image = 'postgres'

    detach = True
    remove_on_stop = False

    mount_project_root = False
    working_dir = None


class Psql(Exec):
    def get_command_args(self):
        return 'psql',


class Pg_dump(Exec):
    def get_command_args(self):
        return 'pg_dump',


class Pg_restore(Exec):
    def get_command_args(self):
        return 'pg_restore',
