from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from logging import getLogger

from ds import context
from ds import fs
from ds.command import Command

logger = getLogger(__name__)


class Context(context.Context):
    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            OverridePreset,
            InstallAutocomplete,
            ListContexts,
        ]


class ListContexts(Command):
    short_help = 'Show all posible context modules'

    def invoke_with_args(self, args):
        print(' '.join(fs.find_contexts()))


class InstallAutocomplete(Command):
    short_help = 'NOT READY YET'
    usage = 'usage: {name} [<shell>]'

    def invoke_with_args(self, args):
        shell = args['<shell>'] or 'bash'
        script = fs.relative('autocomplete', shell)
        if not fs.exists(script):
            logger.error('Unknown shell: %s', shell)
            return
        print()
        print('source', script)
        print()


class OverridePreset(Command):
    short_help = 'Copy a preset to one of local directories'
    usage = 'usage: {name} [<preset>]'

    def invoke_with_args(self, args):
        variants = fs.find_contexts()
        context = self.context.executor.\
            fzf(variants, prompt='Preset')
        if not context:
            return

        variants = ['default', context]
        if set(variants) == 1:
            new_context = context
        else:
            new_context = self.context.executor.\
                fzf(variants, prompt='New context')

        additional_import = fs.additional_import()
        existing_additional_import = fs.existing_additional_import()

        variants = existing_additional_import + [
            path
            for path in additional_import
            if path not in existing_additional_import
        ]

        paths = self.context.executor.\
            fzf(variants, prompt='Install path', no_sort=True)
        if not paths:
            return

        from pprint import pprint
        pprint([context, new_context, paths])
