from os.path import join

from dsjk_docker.presets.base import BaseDockerContext
from dsjk_docker.presets.base.commands import Exec, Shell


class PipMixin(BaseDockerContext):
    requirements_filename = 'requirements.txt'

    def get_pip_requirements_path(self):
        return join(
            self.project_root,
            self.requirements_filename,
        )

    def get_commands(self):
        return super(PipMixin, self).get_commands() + [
            Pip,
            PipFreeze,
        ]


class Pip(Exec):
    user = 0

    def get_command(self):
        return 'pip',


class PipFreeze(Shell):
    tty = False

    def get_command(self):
        return 'pip', 'freeze',

    def invoke_with_args(self, args):
        super(PipFreeze, self).invoke_with_args(args)
        result = self.context.executor.commit()
        path = self.context.get_pip_requirements_path()
        with open(path, 'w') as output:
            output.write(result.stdout)
        self.context.executor.append(('git', 'diff', path))
