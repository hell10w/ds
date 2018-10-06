from os.path import join

from base_container import DockerContext
from base_container import Exec
from base_container import Mount
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

    restart = 'always'

    data_mount = None

    def get_mounts(self):
        result = super(RedisContext, self).get_mounts()
        if self.data_mount:
            result.append(Mount(self.data_mount, '/data/'))
        return result

    @property
    def data_mount(self):
        return join(self.project_root, '.data', 'redis')


class Cli(Exec):
    def get_command_args(self):
        return 'redis-cli',


class Info(Exec):
    def get_command_args(self):
        return 'redis-cli', 'info',
