from __future__ import unicode_literals
from logging import getLogger
import os

from ds import context
from ds.command import Command as _Command


logger = getLogger(__name__)


class Context(context.Context):
    def get_commands(self):
        return super(Context, self).get_commands() + [
            Install,
            CleanPyc,
            CleanDist,
            Publish,
            Test,
        ]


class Command(_Command):
    def get_packages(self):
        result = os.listdir(self.context.project_root)
        result = filter(lambda item: item.startswith('ds-'), result)
        result = sorted(result)
        return result

    @property
    def packages(self):
        return self.get_packages()


class CleanPyc(Command):
    patterns = '*.py[co]', '__pycache__'

    def invoke_with_args(self, args):
        executor = self.context.executor
        with executor.chain(skip_stdout=True) as chain:
            for pattern in self.patterns:
                chain.append('find', '.', '-iname', pattern, '-delete')


class CleanDist(Command):
    consume_all_args = True
    patterns = 'build', 'dist', '*.egg-info'

    def invoke_with_args(self, args):
        if not args:
            args = self.packages
        executor = self.context.executor
        for path in args:
            with executor.chain(path=path, skip_stdout=True, shell=True) as chain:
                for pattern in self.patterns:
                    chain.append('sudo rm -rf {}'.format(pattern))


class Install(Command):
    consume_all_args = True

    def invoke_with_args(self, args):
        if not args:
            args = self.packages
        executor = self.context.executor
        for package in args:
            with executor.chain(path=package, skip_stdout=True) as chain:
                chain.append('sudo', 'python', 'setup.py', 'install', '--force')
            self.context.clean_dist((package, ))
        self.context.clean_pyc()


class Publish(Command):
    def invoke_with_args(self, args):
        executor = self.context.executor
        for package in self.get_packages():
            with executor.chain(path=package, skip_stdout=True) as chain:
                chain.append('python', 'setup.py', 'sdist', 'upload', '-r', 'pypi')
            self.context.clean_dist((package, ))
        self.context.clean_pyc()


class Test(Command):
    consume_all_args = True

    def invoke_with_args(self, args):
        if not args:
            args = self.packages
        executor = self.context.executor
        for path in args:
            with executor.chain(path=path, skip_stdout=True) as chain:
                chain.append('pytest', '-s')
        self.context.clean_pyc()
