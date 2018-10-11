import os

from base_container import DockerContext
from base_container import Exec
from base_container import Mount
from base_pull import Context as PullContext
from ds import text


class ClojureContext(DockerContext):
    cmd = 'lein', 'repl',
    networks = 'host',

    def get_all_commands(self):
        return super(ClojureContext, self).get_all_commands() + [
            CreateNewProject,
            Lein,
            Repl,
        ]

    @property
    def environment(self):
        result = super(ClojureContext, self).environment
        result['HOME'] = '/tmp/'
        return result

    @property
    def home(self):
        result = text.safe_list(super(ClojureContext, self).home)
        result.append('/tmp/')
        return result


class Context(ClojureContext, PullContext):
    default_image = 'clojure'
    default_tag = 'lein'


class Lein(Exec):
    def get_command_args(self):
        return 'lein',


class Repl(Exec):
    def get_command_args(self):
        return 'lein', 'repl',


class CreateNewProject(Exec):
    usage = 'usage: {name} [<template>] [<name>]'
    short_help = 'Generate new project'
    hidden = False
    consume_all_args = False

    def format_args(self, args):
        result = list(self.get_command_args()) + list(args)
        return 'lein', 'new', \
                args.get('<template>', None) or 'app', \
                args.get('<name>', None) or 'app', \
                '--to-dir', self.context.working_dir, \
                '--force',
