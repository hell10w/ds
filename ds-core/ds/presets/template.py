from __future__ import unicode_literals
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
