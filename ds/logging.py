from __future__ import absolute_import

from logging import basicConfig
from logging import DEBUG
from logging import ERROR
from logging import getLogger
from logging import INFO
from logging import WARNING

logger = getLogger()


def setup_logging_level(verbosity):
    level = {
        1: WARNING,
        2: INFO,
        3: DEBUG,
    }.get(verbosity, ERROR)
    basicConfig(level=level)
