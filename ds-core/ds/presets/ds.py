from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from logging import getLogger
from os.path import exists
from os.path import join
from shutil import copyfile

from six.moves import input

from ds import context
from ds.path import relative
from ds.path import get_additional_import
from ds.path import get_possible_imports
from ds.discover import find_contexts
from ds.command import Command
from ds.command import preset_base_command


logger = getLogger(__name__)


BASHRC = """
dscomplete={path}
[ -f $dscomplete ] && source $dscomplete
"""


class Context(context.Context):
    def get_commands(self):
        return super(Context, self).get_commands() + [
            InstallAutocomplete,
            ListContexts,
            OverridePreset,
        ]


class ListContexts(Command):
    short_help = 'Show all possible context modules'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        print(' '.join([item.display_name() for item in find_contexts()]))


class InstallAutocomplete(Command):
    short_help = ''
    usage = '[<shell>]'

    weight = preset_base_command()

    def invoke_with_args(self, args):
        shell = args['<shell>'] or 'bash'
        script = relative('autocomplete', shell)
        if not exists(script):
            logger.error('Unknown shell: %s', shell)
            return
        print('Add to .bashrc:')
        print(BASHRC.format(path=script))


class OverridePreset(Command):
    short_help = 'Copy a preset to one of local directories'

    weight = preset_base_command()

    default_option = 'default'
    other_option = '(other)'

    def invoke_with_args(self, args):
        selected_context = self.context.executor.\
            ask_for_context(prompt='Preset')
        if not selected_context:
            return

        variants = [self.other_option, self.default_option]
        if selected_context.module_name != self.default_option:
            variants.append(selected_context.module_name)

        overridden_name = self.context.executor.\
            fzf(variants, prompt='New context')
        if not overridden_name:
            return

        if overridden_name == self.other_option:
            try:
                overridden_name = input('New context name: ')
            except EOFError:
                overridden_name = None
        if not overridden_name:
            return

        additional_import = get_additional_import()
        possible_imports = get_possible_imports()

        variants = additional_import + [
            path for path in possible_imports
            if path not in additional_import
        ]

        overridden_path = self.context.executor.\
            fzf(variants, prompt='Install path', no_sort=True)
        if not overridden_path:
            return

        if not exists(overridden_path):
            os.makedirs(overridden_path)

        overridden_name = join(overridden_path, overridden_name) + '.py'

        if exists(overridden_name):
            confirm = 'File "{}" already exists. Override?'.format(overridden_name)
            if not self.context.executor.yesno(confirm):
                return

        copyfile(selected_context.file_path(), overridden_name)
        logger.info('New context copied to "%s"', overridden_name)

        self.context.executor.edit_file(overridden_name)
