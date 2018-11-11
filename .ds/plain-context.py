from __future__ import unicode_literals
from logging import getLogger

from ds import context
from ds.command import Command
from ds.summary import TableSummary


logger = getLogger(__name__)


class Context(context.Context):
    def get_additional_summary(self):
        test_summary = TableSummary('Test', [['a', '1'], ['b', '2']])
        return super(Context, self).get_additional_summary() + [test_summary]

    def get_commands(self):
        return super(Context, self).get_commands() + [
            EchoTest,
        ]


class EchoTest(Command):
    usage = '[<text>]'

    def invoke_with_args(self, args):
        text = args.get('<text>') or ''
        self.context.executor.append(('echo', text))
