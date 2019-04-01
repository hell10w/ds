from ds.command import Command
from ds.context import BaseContext
from dsjk_docker.presets.base.commands import Exec


class IPythonMixin(BaseContext):
    def get_commands(self):
        return super(IPythonMixin, self).get_commands() + [
            Ipython,
        ]


class PythonMixin(BaseContext):
    def get_commands(self):
        return super(PythonMixin, self).get_commands() + [
            Python,
        ]


class Python(Exec):
    def get_command(self):
        return 'python',


class Ipython(Exec):
    def get_command(self):
        return 'ipython',


class CleanPyc(Command):
    patterns = '*.py[co]', '__pycache__'

    def invoke_with_args(self, args):
        executor = self.context.executor
        with executor.chain(skip_stdout=True) as chain:
            for pattern in self.patterns:
                chain.append('find', '.', '-iname', pattern, '-delete')
