from collections import OrderedDict
from logging import getLogger

from ds import command
from ds import executor
from ds import flow
from ds import fs
from ds import text


BASE_USAGE = 'usage: ds [-v|-vv|-vvv] [--version] [--help] ' \
             '[-c <context>] ' \
             '[--simulate] '
BASE_OPTIONS = """
 --simulate      Do nothing
 -v|-vv|-vvv     Verbosity level
 -c <context>    Context module name
""".strip('\n')

PRE_USAGE = BASE_USAGE + """[<args>...]

Options:
""" + BASE_OPTIONS

USAGE = BASE_USAGE + """<command> [<args>...]

Options:
""" + BASE_OPTIONS + """
 <command>

Commands:
{commands}
"""

logger = getLogger(__name__)


class BaseContext(object):
    executor_class = executor.Executor

    def __init__(self):
        self._commands = OrderedDict(
            [(command_class._name, command_class(self))
             for command_class in self.get_all_commands()])
        self._executor = None

    def get_all_commands(self):
        return []

    @property
    def commands(self):
        return self._commands

    @property
    def executor(self):
        return self._executor

    def run(self):
        pass

    def get_command(self, name):
        for candidate in (name, name.replace('_', '-')):
            if candidate in self.commands:
                return self.commands[candidate]

    def __getitem__(self, key):
        command = self.get_command(key)
        if command:
            return command
        raise KeyError

    def __getattribute__(self, name):
        try:
            return super(BaseContext, self).__getattribute__(name)
        except AttributeError:
            command = self.get_command(name)
            if command:
                return command
            raise


class Context(BaseContext):
    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            command.ListCommands,
            command.ShowContext,
        ]

    def get_project_root(self):
        return fs.find_project_root()

    @property
    def project_root(self):
        return self.get_project_root()

    def get_project_name(self):
        return fs.get_project_name()

    @property
    def project_name(self):
        return self.get_project_name()

    def run(self):
        pre_usage_options = flow.pre_usage(PRE_USAGE)

        self._executor = self.executor_class(
            simulate=pre_usage_options.get('--simulate'))

        verbose_level = pre_usage_options.get('-v')
        flow.setup_logging_level(verbose_level)

        columns = [[name, command.short_help]
                   for name, command in self.commands.items()
                   if not command.hidden or verbose_level >= 2]
        commands = text.format_columns(*columns)

        usage_options = flow.usage(USAGE.format(commands=commands or ''))

        name = usage_options.get('<command>')
        options = usage_options.get('<args>')

        if name not in self.commands:
            logger.error('Command not found')
            return

        self[name].invoke(command_line=options)
        self.executor.commit(replace=True)
