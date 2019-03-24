from logging import getLogger
from os import listdir
from os.path import join
from os.path import exists

from ds import context
from ds.path import relative
from ds.command import Command


logger = getLogger()


class Context(context.Context):
    files = 'incoming', 'backlog', 'doing', 'done'
    commit_with_empty_message = False

    def get_commands(self):
        return super(Context, self).get_commands() + [
            ('i', Init),
            ('e', Edit),
            ('s', Status),
            ('d', Diff),
            ('c', Commit),
        ]

    @property
    def templates_path(self):
        return self.get_templates_path()

    def get_templates_path(self):
        return relative('presets/todo/templates')

    @property
    def templates(self):
        return listdir(self.templates_path)

    @property
    def commit_message(self):
        return '' if self.commit_with_empty_message else '.'


class Init(Command):
    short_help = 'Init files and git'

    def invoke_with_args(self, args):
        src_path = self.context.templates_path
        files = self.context.templates

        some_exists = False
        for name in ['.git'] + files:
            if not exists(name):
                continue
            logger.error('%s already exists!', name)
            some_exists = True

        if some_exists:
            return

        self.context.executor.append(('git', 'init'))

        for filename in files:
            self.context.executor.append(('cp', join(src_path, filename), filename))
            self.context.executor.append(('git', 'add', filename))

        self.context.executor.append(('git', 'commit', '-m', 'init'))


class Edit(Command):
    short_help = 'Open vim with session'

    def invoke_with_args(self, args):
        self.context.executor.append(('vim', '-c', 'source .session.vim'),
                                     skip_all=True)
        self.context.c()


class Commit(Command):
    short_help = 'Commit all'

    def invoke_with_args(self, args):
        files = self.context.templates

        for filename in files:
            self.context.executor.append(('git', 'add', filename))
        self.context.executor.append(('git', 'commit',
                                      '--allow-empty-message',
                                      '-m', self.context.commit_message))


class Status(Command):
    short_help = 'git status'

    def invoke_with_args(self, args):
        self.context.executor.append(('git', 'status'))


class Diff(Command):
    short_help = 'git diff'

    def invoke_with_args(self, args):
        self.context.executor.append(('git', 'diff'))
