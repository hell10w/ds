from ds.presets.docker_base import mixins
from ds.presets.docker_base import naming
from ds.presets.docker_base import DockerContext
from ds.presets.docker_base import PullContext
from ds.presets.docker_base.commands import Exec
from ds.command import preset_command


class ClojureContext(DockerContext):
    def get_commands(self):
        return super(ClojureContext, self).get_commands() + [
            CreateNewProject,
            Lein,
            Repl,
        ]


class Context(ClojureContext, naming.DefaultNaming,
              mixins.HomeMountsMixin, mixins.ProjectMountMixin,
              PullContext):
    default_image = 'clojure'
    default_tag = 'lein'

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


class CreateNewProject(Exec):
    usage = '[<template>] [<name>]'
    short_help = 'Generate new project'
    consume_all_args = False

    weight = preset_command()

    def format_args(self, args):
        return 'lein', 'new', \
                args.get('<template>', None) or 'app', \
                args.get('<name>', None) or 'app', \
                '--to-dir', self.context.project_root, \
                '--force',
