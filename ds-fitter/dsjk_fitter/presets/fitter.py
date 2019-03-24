from datetime import datetime
from logging import getLogger
from os import makedirs
from os.path import join
from os.path import exists
from os.path import dirname

from ds import context
from ds.command import Command


logger = getLogger()


class Context(context.Context):
    def get_commands(self):
        return super(Context, self).get_commands() + [
            ('n', New),
            New,
            ('v', View),
            View,
            ('l', View),
        ]

    @property
    def base_path(self):
        return join(self.project_root, 'notes')

    @property
    def new_filename(self):
        now = datetime.now()
        filename = '{}.txt'.format(now.strftime('%H-%M-%S-%f'))
        return join(self.base_path, now.strftime('%Y%m%d'), filename)


class New(Command):
    def invoke_with_args(self, args):
        filename = self.context.new_filename
        path = dirname(filename)
        if not exists(path):
            makedirs(path)
        logger.info('Edit %s', filename)
        self.context.executor.edit_file(filename)


class View(Command):
    def invoke_with_args(self, args):
        self.context.executor.append((
            'ranger',
            '--cmd=flat 1',
            self.context.base_path,
        ))
