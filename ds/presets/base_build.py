from base_container import Build
from base_container import DockerContext


class Context(DockerContext):
    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Build,
        ]
