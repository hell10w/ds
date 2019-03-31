from __future__ import unicode_literals
from collections import OrderedDict
from logging import getLogger

from ds import executor
from ds import command
from ds import path
from ds.summary import TableSummary as _TableSummary


logger = getLogger(__name__)


class BaseContext(object):
    def __init__(self, **options):
        self._commands = OrderedDict()

        for command_class in self.get_commands():
            if not command_class:
                continue
            name = None
            if isinstance(command_class, (tuple, list)):
                name, command_class = command_class
            command = command_class(self)
            if name is None:
                name = command.get_name()
            self._commands[name] = command

        # self._commands = OrderedDict([])
        # self._sort_commands(self._filter_commands(self._commands.items()))
        # commands = self._filter_commands(commands)
        # commands = self._sort_commands(commands)

    @property
    def commands(self):
        return self._commands

    def _filter_commands(self, commands):
        return commands

    def _sort_commands(self, commands):
        key = lambda command: (command.weight, command.__name__)
        return sorted(commands, key=key)

    def get_commands(self):
        return []

    def get_command(self, name):
        if self.commands is None:
            return
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

    def check(self):
        pass


class IntrospectionMixin(BaseContext):
    @property
    def source_file(self):
        from inspect import getmodule
        from inspect import getsourcefile
        return getsourcefile(getmodule(self))

    def get_commands(self):
        return super(IntrospectionMixin, self).get_commands() + [
            command.ShowContext,
            command.EditContext,
        ]


class ExecutorMixin(BaseContext):
    executor_class = executor.Executor

    def __init__(self, **options):
        self._executor = self.executor_class()
        super(ExecutorMixin, self).__init__(**options)

    @property
    def executor(self):
        return self._executor


class TestExecutorMixin(ExecutorMixin):
    executor_class = executor.TestExecutor


# class ReplMixin(BaseContext):
#     @property
#     def repl_class(self):
#         from ds.repl import Repl
#         return Repl
#
#     def get_commands(self):
#         return super(ReplMixin, self).get_commands() + [
#             command.DsRepl,
#         ]


class ProjectMixin(BaseContext):
    def get_project_root(self):
        return path.get_project_root()

    @property
    def project_root(self):
        return self.get_project_root()

    def get_project_name(self):
        return path.get_project_name()

    @property
    def project_name(self):
        return self.get_project_name()


class Context(ProjectMixin, IntrospectionMixin, ExecutorMixin, BaseContext):
    def get_commands(self):
        return super(Context, self).get_commands() + [
            command.ListCommands,
            command.SwitchContext,
        ]

    def get_additional_summary(self):
        name = '{} ({})'.format(self.__class__.__module__, self.source_file)
        project = '{} ({})'.format(self.project_name, self.project_root)
        return [
            _TableSummary('Context', [['Name', name], ['Project', project]]),
        ]
