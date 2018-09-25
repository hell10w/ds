from base_container import DockerContext
from base_container import DockerCommand


class Context(DockerContext):
    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Build,
        ]


class Build(DockerCommand):
    short_help = 'Build an image'

    def invoke_with_args(self, args):
        self.context.executor.append([
            ('docker', 'build'),
            self.context.image_name,
        ])
