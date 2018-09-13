import os
import sys
from logging import INFO
from logging import WARNING
from logging import DEBUG
from logging import ERROR
from logging import basicConfig
from logging import getLogger
from pprint import pprint

from docopt import docopt

from ds import __version__ as version
from ds import text
from ds import fs
from ds.import_tools import try_to_import, get_module_path
from ds.command import CommandMeta


logger = getLogger(__name__)

BASE_USAGE = 'usage: ds [-v|-vv|-vvv] [--version] [--help] ' \
             '[--simulate] [--flow=<path>] [--context=<path>] '
BASE_OPTIONS = """
 --flow=<path>      Import path of a flow class. If this option is empty then `DS_FLOW` environment variable will be checked
 --context=<path>   Import path of a context class. If this option is empty then `DS_CONTEXT` environment variable will be checked
 --simulate         Do nothing
 -v|-vv|-vvv        Verbosity level
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


class Flow(object):
    def __init__(self):
        self.pre_usage_options = None
        self.usage_options = None
        self.context = None

    def run(self):
        self.pre_usage_options = self.pre_usage()

        self.setup_logging_level()
        self.extend_import_path()

        path, Flow = self.load_flow()
        if Flow is not self.__class__:
            logger.debug('Loaded flow class %s', Flow)
            return Flow
        logger.info('Flow is "%s"', path)

        logger.debug('Pre-usage options:\n%s', self.pre_usage_options)

        path, Context = self.load_context()
        logger.info('Context is "%s"', path)
        self.context = Context(self)

        self.usage_options = self.usage()
        logger.debug('Usage options:\n%s', self.usage_options)

        self.invoke_command(self.usage_options.get('<command>'),
                            self.usage_options.get('<args>'))

    def invoke_command(self, command_name, command_line=None):
        command = self.commands.get(command_name)
        if not command:
            logger.error('Command "%s" not found', command_name)
            return
        return command.invoke_with_command_line(command_line)

    def load_flow(self):
        candidates = [
            self.pre_usage_options.get('--flow') or os.environ.get('DS_FLOW'),
            'flow::Flow',
            'ds.flow::Flow',
        ]
        for index, path in enumerate(candidates):
            if not path:
                continue
            try:
                module, klass = self.load_class(path)
            except Exception as e:
                logger.debug('Flow load error. Path: "%s". Error: %s / %s', path, e.__class__.__name__, e)
                if index == len(candidates) - 1:
                    raise
                continue
            if not klass:
                continue
            is_self = get_module_path(module) == fs.clean_path(__file__) and \
                      klass.__name__ == self.__class__.__name__
            if is_self:
                return path, self.__class__
            return path, klass

    def load_context(self):
        candidates = [
            self.pre_usage_options.get('--context') or os.environ.get('DS_CONTEXT'),
            'context::Context',
            'ds.presets.context.ds_setup::Context',
        ]
        for index, path in enumerate(candidates):
            if not path:
                continue
            try:
                _, klass = self.load_class(path)
            except Exception as e:
                logger.debug('Context load error. Path: "%s". Error: %s / %s', path, e.__class__.__name__, e)
                if index == len(candidates) - 1:
                    raise
                continue
            return path, klass

    def load_class(self, path):
        rest, attr = (path.rsplit('::', 1) + [None])[:2]
        if attr is None:
            logger.error('Bad an import path "%s". Import path should be in format `<fs path or python module>::<module attribute name>`. E.g. `ds.flow::Flow` or `ds/flow.py:Flow`', path)
            return None, None
        module = try_to_import(rest)
        return module, getattr(module, attr)

    def pre_usage(self):
        argv = [item for item in sys.argv[1:] if item not in ('--help', '-h')]
        return docopt(PRE_USAGE, version=version, options_first=True, argv=argv)

    def usage(self):
        columns = [[command.meta.name, command.meta.short_help]
                   for command in self.commands.values()
                   if not command.meta.hidden or self.pre_usage_options.get('-v') >= 2]
        commands = text.format_columns(*columns)
        usage = USAGE.format(commands=commands)
        return docopt(usage, version=version, options_first=True)

    def setup_logging_level(self):
        verbosity = self.pre_usage_options.get('-v')
        level = {
            1: WARNING,
            2: INFO,
            3: DEBUG,
        }.get(verbosity, ERROR)
        basicConfig(level=level)

    def extend_import_path(self):
        sys.path = fs.build_additional_import() + sys.path

    def get_commands(self):
        return CommandMeta.commands

    @property
    def commands(self):
        return self.get_commands()
