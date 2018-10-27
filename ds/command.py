from __future__ import print_function
from __future__ import unicode_literals
import re
from logging import getLogger
from weakref import ref

from docopt import docopt
from six import with_metaclass

from ds import path
from ds.environment import get_environment
from ds.utils import pretty_print_object
from ds.utils import is_interactive
from ds.discover import find_contexts


logger = getLogger(__name__)


def kebab_to_snake(name):
    value = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', value).lower()


class CommandMeta(type):
    def __new__(mcs, name, bases, dct):
        command_name = dct.pop('name', None)
        klass = super(CommandMeta, mcs).__new__(mcs, name, bases, dct)
        klass.name = command_name or kebab_to_snake(name)
        return klass


class BaseCommand(with_metaclass(CommandMeta)):
    name = None
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
        usage = self.usage.format(name=self.name)
        return docopt(usage, argv=command_line, options_first=self.options_first)

    def invoke_with_args(self, args):
        raise NotImplementedError

    def invoke(self, command_line=None, args=None):
        assert (bool(command_line) != bool(args)) or not command_line
        if args:
            return self.invoke_with_args(args)
        return self.invoke_with_args(self.parse_command_line(command_line))

    __call__ = invoke


class SwitchContext(Command):
    options_first = True
    usage = 'usage: {name} [<context>]'
    short_help = 'Switch context'
    hidden = True

    def invoke_with_args(self, args):
        name = self.get_context_name(args)
        if name:
            get_environment().set('context', name)

    def get_context_name(self, args):
        src = args.get('<context>', None)
        if src:
            return src

        if not is_interactive():
            logger.error('Context name is required for non-interactive shell')
            return

        return self.ask_for_context()

    def ask_for_context(self):
        variants = [' '.join(item) for item in find_contexts()]
        preset = self.context.executor. \
            fzf(variants, prompt='Context')
        if not preset:
            return
        return preset.split(' ', 1)[0]


class ListCommands(Command):
    short_help = 'List all commands in context (autocomplete helper)'
    hidden = True

    def invoke_with_args(self, args):
        print(' '.join(self.context.commands.keys()))


class ShowContext(Command):
    short_help = 'Show a context info (autocomplete helper)'
    hidden = True

    def invoke_with_args(self, args):
        context_class = self.context.__class__
        print('Context:', context_class, context_class.__module__)
        print('Additional imports:', ';'.join(path.get_additional_import()))
        pretty_print_object(self.context)


class EditContext(Command):
    short_help = 'Edit a context with $EDITOR'
    hidden = True

    def invoke_with_args(self, args):
        if not is_interactive():
            return
        self.context.executor.edit_file(self.context.source_file)


class DsRepl(Command):
    short_help = 'Read-eval-print-loop'
    hidden = True

    def invoke_with_args(self, args):
        self.context.repl_class(self.context)(args)
