from logging import getLogger
from os import chdir
from os import getcwd


logger = getLogger()


class chain(object):
    def __init__(self, executor, **options):
        self.executor = executor
        self.options = options
        self.path = self.options.get('path', None)
        self.previous = getcwd() if self.path else None

    def append(self, *args, **options):
        opts = self.options.copy()
        opts.update(options)
        self.executor.append(args, **opts)
    add = append

    def __enter__(self):
        if self.path:
            logger.debug('Switch current directory to %s', self.path)
            chdir(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        replace = self.options.get('replace', False)
        self.executor.commit(replace=replace)
        if self.previous:
            logger.debug('Switch current directory to %s', self.previous)
            chdir(self.previous)
