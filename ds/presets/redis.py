from base_container import DockerContext
from base_container import Exec
from base_container import ForeignContext
from base_container import PersistentContext
from base_pull import Context as PullContext


class RedisContext(DockerContext):
    def get_all_commands(self):
        return super(RedisContext, self).get_all_commands() + [
            Cli,
            Info,
        ]


class Context(ForeignContext, PersistentContext, RedisContext, PullContext):
    default_image = 'redis'


class Cli(Exec):
    short_help = '`redis-cli`'

    def get_command_args(self):
        return 'redis-cli',


class Info(Exec):
    short_help = '`redis-cli info`'

    def get_command_args(self):
        return 'redis-cli', 'info',
