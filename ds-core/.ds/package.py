from __future__ import unicode_literals
from logging import getLogger

from ds import context
from ds.command import Command


logger = getLogger(__name__)


class Context(context.Context):
    def get_commands(self):
        return super(Context, self).get_commands() + [
            Test,
            Publish,
        ]


class Test(Command):
    consume_all_args = True

    def invoke_with_args(self, args):
        self.context.executor.append(('pytest', '--cov=ds', args), skip_all=True)
        self.context.executor.append(('ds', 'switch-context', 'package'))


class Publish(Command):
    consume_all_args = True

    def invoke_with_args(self, args):
        prefix = 'python', 'setup.py', 'sdist',
        self.context.executor.append(prefix)
        self.context.executor.append((prefix, 'upload', '-r', 'pypi'))
