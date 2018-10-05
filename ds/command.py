from __future__ import print_function
from __future__ import unicode_literals

import os
from inspect import getmodule
from inspect import getsourcefile
from logging import getLogger
from weakref import ref

from docopt import docopt
from six import with_metaclass

from ds import fs
from ds import text

logger = getLogger(__name__)


class CommandMeta(type):
    def __new__(mcs, name, bases, dct):
        command_name = dct.pop('name', None)
        klass = super(CommandMeta, mcs).__new__(mcs, name, bases, dct)
        klass._name = command_name or text.kebab_to_snake(name)
        return klass


class BaseCommand(with_metaclass(CommandMeta)):
    usage = 'usage: {name}'
    short_help = ''
    hidden = False

    def __init__(self, context):
        self._context = ref(context)

    @property
    def context(self):
        return self._context()


class Command(BaseCommand):
    options_first = True
    consume_all_args = False

    def parse_command_line(self, command_line):
        command_line = command_line or ()
        if self.consume_all_args:
            return command_line
        usage = self.usage.format(name=self._name)
        return docopt(
            usage, argv=command_line, options_first=self.options_first)

    def invoke_with_args(self, args):
        raise NotImplementedError

    def invoke(self, command_line=None, args=None):
        if args:
            assert not command_line
            return self.invoke_with_args(args)
        return self.invoke_with_args(self.parse_command_line(command_line))

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)


class HiddenCommand(Command):
    hidden = True


class ListCommands(HiddenCommand):
    short_help = 'List all commands in context'

    def invoke_with_args(self, args):
        print(' '.join(self.context.commands.keys()))


class ShowContext(HiddenCommand):
    short_help = 'Show a context info'

    def invoke_with_args(self, args):
        context_class = self.context.__class__
        print('Context:', context_class, context_class.__module__)

        existing_additional_import = fs.existing_additional_import()
        additional_import = fs.additional_import()
        print('Existing additional imports:',
              ';'.join(existing_additional_import))
        print('Missing additional imports:', ';'.join([
            path for path in additional_import
            if path not in existing_additional_import
        ]))

        text.pretty_print_object(self.context)


class EditContext(HiddenCommand):
    short_help = 'Edit a context with $EDITOR'

    def invoke_with_args(self, args):
        context_class = self.context.__class__
        filename = getsourcefile(getmodule(self.context))
        editor = os.environ.get('EDITOR')
        if not editor:
            logger.error('$EDITOR is not defined')
            return
        self.context.executor.append((
            editor,
            filename,
        ))
