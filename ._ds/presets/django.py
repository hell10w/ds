from base_container import DockerContext
from base_container import Exec
from python import PythonContext


class DjangoContext(DockerContext):
    def get_all_commands(self):
        return super(DjangoContext, self).get_all_commands() + [
            Manage,
            ShellPlus,
            Migrate,
            MakeMigrations,
        ]


class Manage(Exec):
    def get_command_args(self):
        return './manage.py',


class ShellPlus(Exec):
    def get_command_args(self):
        return './manage.py', 'shell_plus',


class Migrate(Exec):
    def get_command_args(self):
        return './manage.py', 'migrate',


class MakeMigrations(Exec):
    def get_command_args(self):
        return './manage.py', 'makemigrations',
