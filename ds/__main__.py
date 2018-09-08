import logging
import sys
from collections import namedtuple

from docopt import docopt

import ds.command
from ds import __version__ as version
from ds import logging
from ds import text

BASE_USAGE = 'usage: ds [-v|-vv|-vvv] [--version] [--help] '
PRE_USAGE = BASE_USAGE + '[<args>...]'
USAGE = BASE_USAGE + """<command> [<args>...]

Options:
 <command>

Commands:
{commands}
"""


def pre_usage():
    argv = [item for item in sys.argv[1:] if item not in ('--help', '-h')]
    return docopt(PRE_USAGE, version=version, options_first=True, argv=argv)


def usage(columns):
    commands = text.format_columns(*columns)
    return docopt(
        USAGE.format(commands=commands), version=version, options_first=True)


Command = namedtuple('Command', ('name', 'short_help'))


def get_commands():
    return [
        Command('a', 'aaa'),
        Command('bbbb', 'bbb'),
        Command('cbbbbbbbbb', 'ccc'),
    ]


def main():
    options = pre_usage()

    from pprint import pprint
    pprint(options)

    logging.setup_logging_level(options.get('-v'))

    options = usage(
        [[command.name, command.short_help] for command in get_commands()])

    from pprint import pprint
    pprint(options)
    #  context = get_context()
    #  commands = get_commands(context)


if __name__ == '__main__':
    main()
