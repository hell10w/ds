from collections import namedtuple
from logging import getLogger
from os import execvp
from subprocess import call
from subprocess import CalledProcessError
from subprocess import check_output
from subprocess import PIPE
from subprocess import Popen

from ds import text

logger = getLogger(__name__)

ExecResult = namedtuple('ExecResult', ('code', 'stdout', 'stderr'))


class Executor(object):
    def __init__(self, simulate=False):
        self._simulate = simulate
        self._queue = []

    def append(self, args, **opts):
        args = text.flatten(args)
        if not args:
            return
        self._queue.append((args, opts))

    def _call(self, args, **opts):
        logger.debug('Call with %s', args)
        if self._simulate:
            return ExecResult(0, '', '')

        process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(b'')
        return ExecResult(process.returncode, stdout, stderr)

    def _replace(self, args, **opts):
        logger.debug('Replace with %s', args)
        if self._simulate:
            return
        execvp(args[0], args[:])

    def commit(self, replace=False):
        queue = self._queue
        self._queue = []
        for is_last, (item, opts) in text.iter_with_last(queue):
            if is_last and replace:
                self._replace(item, **opts)
                return
            value = self._call(item, **opts)
            if is_last:
                return value
