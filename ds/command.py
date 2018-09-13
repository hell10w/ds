from weakref import ref
from collections import OrderedDict

from six import with_metaclass
from docopt import docopt

from ds import meta


class CommandMeta(meta.CollectMeta):
    meta_defaults = dict(
        abstract=False,
        hidden=False,
        name=meta.AUTOFILL,
        usage='usage: {name}',
        short_help='',
        options_first=True,
        consume_all_args=False,
    )

    commands = OrderedDict()

    def __new__(mcs, name, bases, dct):
        klass = super(CommandMeta, mcs).__new__(mcs, name, bases, dct)
        if not klass.meta.abstract:
            mcs.commands[klass.meta.name] = klass
        return klass


class Command(with_metaclass(CommandMeta)):
    class Meta:
        abstract = True

    def __init__(self, context):
        self._context = ref(context)

    @property
    def context(self):
        return self._context()

    @property
    def flow(self):
        return self.context.flow

    def parse_command_line(self, command_line):
        command_line = command_line or ''
        if self.meta.consume_all_args:
            return command_line
        usage = self.meta.usage.format(name=self.meta.name)
        return docopt(usage, argv=command_line,
                      options_first=self.meta.options_first)

    def invoke_with_command_line(self, command_line=None):
        return self.invoke(self.parse_argv(command_line))

    def invoke_with_args(self, args):
        from pprint import pprint
        pprint(args)
        raise NotImplementedError


class __complete(Command):
    class Meta:
        hidden = True
        short_help = 'Autocomplete helper'
