from os.path import exists
from logging import getLogger

from base_container import DockerCommand
from base_container import DockerContext

logger = getLogger(__name__)


class Context(DockerContext):
    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            Build,
            CreateDockerfile,
        ]


class Build(DockerCommand):
    short_help = 'Build an image'

    def invoke_with_args(self, args):
        self.context.executor.append([
            ('docker', 'build'),
            self.context.image_name,
        ])


class CreateDockerfile(DockerCommand):
    hidden = True
    short_help = 'Create Dockerfile and .dockerignore'

    templates = {
        'Dockerfile': 'FROM debian:stretch\n\n\n',
        '.dockerignore': '*',
    }

    def invoke_with_args(self, args):
        for filename, content in self.templates.items():
            if exists(filename):
                logger.error('File "%s" already exists', filename)
                continue
            with open(filename, 'w') as output:
                output.write(content)
