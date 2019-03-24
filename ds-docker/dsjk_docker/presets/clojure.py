from dsjk_docker.presets.base import mixins
from dsjk_docker.presets.base import naming
from dsjk_docker.presets.base import DockerContext
from dsjk_docker.presets.base import PullContext
from dsjk_docker.presets.base.commands import Exec
from ds.command import preset_command


class ClojureContext(DockerContext):
    def get_commands(self):
        return super(ClojureContext, self).get_commands() + [
            NewProject,
            Lein,
            Repl,
        ]


class Context(ClojureContext, naming.DefaultNaming, mixins.UserMixin,
              mixins.HomeMountsMixin, mixins.ProjectMountMixin,
              PullContext):
    default_image = 'clojure'
    default_tag = 'lein'
    container_home = '/tmp',

    def get_environment(self):
        environment = super(Context, self).get_environment()
        environment.setdefault('HOME', self.container_home[0])
        return environment

    def get_container_default(self):
        return 'lein', 'repl'


class Lein(Exec):
    weight = preset_command()

    def get_command(self):
        return 'lein',


class Repl(Exec):
    weight = preset_command()

    def get_command(self):
        return 'lein', 'repl',


class NewProject(Exec):
    usage = '[<template>] [<name>]'
    short_help = 'Generate new project'
    consume_all_args = False

    weight = preset_command()

    def format_args(self, args):
        to_dir = ()
        if self.context.working_dir:
            to_dir = '--to-dir', self.context.working_dir
        return 'lein', 'new', \
                args.get('<template>', None) or 'app', \
                args.get('<name>', None) or 'app', \
                to_dir, '--force',
