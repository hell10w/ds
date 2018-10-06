from base_container import DockerContext
from base_container import Exec
from base_pull import Context as PullContext


class RedisContext(DockerContext):
    """
    https://hub.docker.com/_/redis/
    """

    def get_all_commands(self):
        return super(RedisContext, self).get_all_commands() + [
            Cli,
            Info,
        ]


class Context(RedisContext, PullContext):
    default_image = 'redis'

    detach = True
    remove_on_stop = False

    mount_project_root = False
    working_dir = None
    uid = None


class Cli(Exec):
    def get_command_args(self):
        return 'redis-cli',


class Info(Exec):
    def get_command_args(self):
        return 'redis-cli', 'info',
