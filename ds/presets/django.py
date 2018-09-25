from base_container import Exec


class Manage(Exec):
    def get_command_args(self):
        return './manage.py',


class ShellPlus(Exec):
    def get_command_args(self):
        return './manage.py', 'shell_plus',


class Migrate(Exec):
    def get_command_args(self):
        return './manage.py', 'migrate',


class Makemigrations(Exec):
    def get_command_args(self):
        return './manage.py', 'makemigrations',
