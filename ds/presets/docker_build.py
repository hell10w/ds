from docker_generic import DockerContext, Build


class Context(DockerContext):
    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Build,
        ]
