from __future__ import unicode_literals
import sys
import importlib
import logging
from logging import basicConfig
from logging import getLogger
from logging import DEBUG
from logging import ERROR
from logging import INFO
from logging import WARNING

from docopt import docopt

from ds import __version__ as version
from ds.environment import get_environment
from ds.path import get_additional_import
from ds.utils import format_columns
from ds import errors


logger = getLogger(__name__)

PRE_USAGE = """usage: ds [-v|-vv|-vvv] [--version] [<args>...]

Options:
 -v|-vv|-vvv   Verbosity level
"""

USAGE = """usage: ds [-v|-vv|-vvv] [--version] <command> [<args>...]

Options:
 -v|-vv|-vvv   Verbosity level 

{additional}

Commands:
{commands}
"""


def format_usage(context, show_hidden=False):
    commands = format_columns(*[
        [name, command.short_help]
        for name, command in context.commands.items()
        if not command.hidden or show_hidden
    ])

    additional = '\n\n'.join([
        '{title}:\n{content}'.format(
            title=item.title,
            content=item.render(),
        )
        for item in context.get_additional_summary()
    ])

    return USAGE.format(commands=commands or '', additional=additional)


def invoke_context(context_class):
    pre_usage_args = [arg for arg in sys.argv[1:]
                      if arg not in ('-h', '--help')]
    pre_usage_options = docopt(PRE_USAGE, version=version, options_first=True,
                               argv=pre_usage_args)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    verbose_level = pre_usage_options.get('-v')
    level = {
        1: WARNING,
        2: INFO,
        3: DEBUG,
    }.get(verbose_level, ERROR)
    basicConfig(level=level)

    context = context_class()

    usage_options = docopt(format_usage(context, verbose_level >= 2),
                           version=version, options_first=True)

    name = usage_options.get('<command>')
    options = usage_options.get('<args>')

    if name not in context.commands:
        logger.error(errors.COMMAND_NOT_FOUND_MESSAGE)
        sys.exit(errors.COMMAND_NOT_FOUND)

    context.check()

    context[name].invoke(command_line=options)
    context.executor.commit(replace=True)


def context_fallback(context_name):
    logger.info('Fallback to default context. It was %s', context_name)
    get_environment().set('context', None)


def main():
    basicConfig(level=INFO)
    context_name = get_environment().get('context', None)

    no_context = context_name is None
    if no_context:
        context_name = 'default'

    sys.path = get_additional_import() + sys.path

    try:
        context_module = importlib.import_module(context_name)
    except ImportError as error:
        if not no_context:
            logger.exception(error)
            context_fallback(context_name)
            sys.exit(errors.NO_CONTEXT_MODULE)
        from ds.presets import dsjk as context_module

    if not hasattr(context_module, 'Context'):
        logger.error(errors.NO_CONTEXT_CLASS_MESSAGE)
        context_fallback(context_name)
        sys.exit(errors.NO_CONTEXT_CLASS)

    context_class = getattr(context_module, 'Context')
    invoke_context(context_class)


if __name__ == '__main__':
    main()
