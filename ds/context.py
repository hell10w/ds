from __future__ import unicode_literals
from collections import OrderedDict
from logging import getLogger

from ds import executor
from ds import command
from ds import path
from ds.summary import TableSummary as _TableSummary
from ds.utils import cd


logger = getLogger(__name__)


class BaseContext(object):
    def __init__(self, **options):
        self._commands = OrderedDict([(command_class.name, command_class(self))
                                      for command_class in self.get_commands()])

    @property
    def commands(self):
        return self._commands

    def get_commands(self):
        return []

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


class ChangeDirMixin(BaseContext):
    def cd(self, path):
        return cd(path, finalizers=(self.executor.commit, ))


class ExecutorMixin(BaseContext):
    executor_class = executor.Executor

    def __init__(self, **options):
        simulate = options.pop('simulate', False)
        self._executor = self.executor_class(simulate=simulate)
        super(ExecutorMixin, self).__init__(**options)

    @property
    def executor(self):
        return self._executor


class ReplMixin(BaseContext):
    @property
    def repl_class(self):
        from ds.repl import Repl
        return Repl

    def get_commands(self):
        return super(ReplMixin, self).get_commands() + [
            command.DsRepl,
        ]


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


class Context(ProjectMixin, IntrospectionMixin, ReplMixin, ExecutorMixin,
              ChangeDirMixin, BaseContext):
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
