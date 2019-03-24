from dsjk_docker.presets.base import DockerContext, PullContext, DefaultNaming
from dsjk_docker.presets.base.commands import Exec


class RedisContext(DockerContext):
    """
    https://hub.docker.com/_/redis/
    """

    def get_commands(self):
        return super(RedisContext, self).get_commands() + [
            Cli,
            Info,
        ]


class Context(DefaultNaming, RedisContext, PullContext):
    default_image = 'redis'


class Cli(Exec):
    def get_command(self):
        return 'redis-cli',


class Info(Cli):
    def get_command(self):
        return super(Info, self).get_command() + ('info', )
