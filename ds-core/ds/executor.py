from __future__ import unicode_literals
import os
from collections import namedtuple
from logging import getLogger
from os import execvp
from subprocess import PIPE
from subprocess import Popen

from ds.utils import flatten
from ds.utils import drop_empty
from ds.chain import chain


logger = getLogger(__name__)

ExecResult = namedtuple('ExecResult', ('code', 'stdout', 'stderr'))


class BaseExecutor(object):
    def append(self, args, **opts):
        raise NotImplementedError

    def commit(self, replace=False):
        raise NotImplementedError


class ExecutorShortcuts(BaseExecutor):
    def fzf(self, choices, multi=False, prompt=None, no_sort=False):
        input_ = '\n'.join(choices)
        args = ['fzf']
        if multi:
            args.append('--multi')
        if prompt:
            args.append('--prompt=' + prompt.rstrip() + ' ')
        if no_sort:
            args.append('--no-sort')
        self.append(args, input=input_, skip_stderr=True)
        result = self.commit().stdout.strip().split('\n')
        if not multi:
            return result[0]
        return result

    def yesno(self, prompt):
        return self.fzf(['no', 'yes'], prompt=prompt) == 'yes'

    def edit_file(self, filename):
        editor = os.environ.get('EDITOR')
        if not editor:
            logger.error('$EDITOR is not defined')
            return
        self.append([editor, filename])
        self.commit(replace=True)


class ChainMixin(BaseExecutor):
    def chain(self, **options):
        return chain(self, **options)


class Executor(ExecutorShortcuts, ChainMixin, BaseExecutor):
    def __init__(self):
        super(Executor, self).__init__()
        self._queue = []

    @property
    def is_empty_queue(self):
        return len(self._queue) == 0

    def append(self, args, **opts):
        args = drop_empty(*flatten(args))
        if not args:
            return
        self._queue.append((args, opts))

    def _call(self, args, **opts):
        logger.debug('Call with %s', args)

        skip_all = opts.get('skip_all', False)
        skip_stdout = opts.get('skip_stdout', skip_all)
        skip_stdin = opts.get('skip_stdin', skip_all)
        skip_stderr = opts.get('skip_stderr', skip_all)
        shell = opts.get('shell', False)
        input_ = opts.get('input', None)

        popen_kwargs = dict(
            stdin=None if skip_stdin else PIPE,
            stdout=None if skip_stdout else PIPE,
            stderr=None if skip_stderr else PIPE,
            shell=shell,
        )
        process = Popen(args, **popen_kwargs)
        stdout, stderr = process.communicate(input_)
        code = process.poll()
        if code:
            logger.info('Code: %s, stdout: %s, stderr: %s',
                        code, repr(stdout), repr(stderr))
        return ExecResult(code, stdout, stderr)

    def _replace(self, args, **opts):
        logger.debug('Replace with %s', args)
        execvp(args[0], args[:])

    def commit(self, replace=False):
        queue = self._queue
        self._queue = []
        for is_last, (item, opts) in iter_with_last(queue):
            if is_last and replace and not opts:  # TODO: opts
                self._replace(item, **opts)
                return
            value = self._call(item, **opts)
            if is_last:
                return value


class TestExecutor(Executor):
    CALL = 'call'
    REPLACE = 'replace'

    def __init__(self):
        super(TestExecutor, self).__init__()
        self._log = []

    @property
    def execute_log(self):
        return self._log

    def _call(self, args, **opts):
        self._log.append((self.CALL, args, opts))

    def _replace(self, args, **opts):
        self._log.append((self.REPLACE, args, opts))


def iter_with_last(items):
    for item in items[:-1]:
        yield False, item
    for item in items[-1:]:
        yield True, item
