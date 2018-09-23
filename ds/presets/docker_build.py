from docker_generic import Build
from docker_generic import DockerContext


class Context(DockerContext):
    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Build,
        ]
