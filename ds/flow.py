import sys
from logging import WARNING, INFO, DEBUG, ERROR, basicConfig

from docopt import docopt

from ds import __version__ as version


def pre_usage(doc):
    argv = [item for item in sys.argv[1:] if item not in ('--help', '-h')]
    return docopt(doc, version=version, options_first=True, argv=argv)


def usage(doc):
    return docopt(doc, version=version, options_first=True)


def setup_logging_level(verbose_level):
    level = {
        1: WARNING,
        2: INFO,
        3: DEBUG,
    }.get(verbose_level, ERROR)
    basicConfig(level=level)
