from ds import text
from base_container import DockerContext
from base_container import Exec
from base_container import ForeignContext
from base_container import PersistentContext
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


class Context(PostgresContext, ForeignContext, PersistentContext, PullContext):
    default_image = 'postgres'


class Psql(Exec):
    def get_command_args(self):
        return 'psql',
