from __future__ import unicode_literals
from __future__ import absolute_import
from logging import getLogger

from ds import context
from ds.command import Command


logger = getLogger(__name__)


class Context(context.Context):
    def get_commands(self):
        return super(Context, self).get_commands() + [
            Simple,
            WithOpts,
            Consume,
            Shell,
            OtherPath,
            CallOtherCommand,
        ]


class Simple(Command):
    def invoke_with_args(self, args):
        logger.info('Invoked')


class WithOpts(Command):
    usage = '[--up|--down] [--value=<count>] [<tail>...]'

    def invoke_with_args(self, args):
        logger.info('Called with %s', args)


class Consume(Command):
    consume_all_args = True

    def invoke_with_args(self, args):
        logger.info('Called with %s', args)


class Shell(Command):
    def invoke_with_args(self, args):
        executor = self.context.executor
        with executor.chain(skip_stdout=True, shell=True) as chain:
            chain.append('ls *')


class OtherPath(Command):
    def invoke_with_args(self, args):
        executor = self.context.executor
        with executor.chain(path='/tmp/', skip_stdout=True) as chain:
            chain.append('ls', '-l')


class CallOtherCommand(Command):
    def invoke_with_args(self, args):
        self.context.with_opts()
        self.context.with_opts('--up')
        self.context['with-opts']('--up')
