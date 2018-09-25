from base_container import DockerContext
from base_container import Exec
from base_pull import Context as PullContext


class PythonContext(DockerContext):
    def get_all_commands(self):
        return super(PythonContext, self).get_all_commands() + [
            Pip,
            PipFreeze,
        ]


class Context(PythonContext, PullContext):
    default_image = 'python'
    default_tag = '3.5'


class Pip(Exec):
    short_help = '`pip`'
    user = 0

    def get_command_args(self):
        return 'pip',


class PipFreeze(Exec):
    short_help = '`pip freeze`'

    def get_command_args(self):
        return 'pip', 'freeze',
