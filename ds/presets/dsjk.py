from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from os.path import join
from os.path import exists
from logging import getLogger
from shutil import copyfile
import os

from ds import context
from ds import fs
from ds.command import Command

logger = getLogger(__name__)

BASHRC = """
dscomplete={path}
[ -f $dscomplete ] && source $dscomplete
"""


class Context(context.Context):
    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            InstallAutocomplete,
            ListContexts,
            OverridePreset,
        ]


class ListContexts(Command):
    short_help = 'Show all posible context modules'

    def invoke_with_args(self, args):
        print(' '.join([item[0] for item in fs.find_contexts()]))


class InstallAutocomplete(Command):
    short_help = 'NOT READY YET'
    usage = 'usage: {name} [<shell>]'

    def invoke_with_args(self, args):
        shell = args['<shell>'] or 'bash'
        script = fs.relative('autocomplete', shell)
        if not exists(script):
            logger.error('Unknown shell: %s', shell)
            return
        print('Add to .bashrc:')
        print(BASHRC.format(path=script))


class OverridePreset(Command):
    short_help = 'Copy a preset to one of local directories'
    usage = 'usage: {name} [<preset>]'

    def invoke_with_args(self, args):
        variants = [
            ' '.join(item)
            for item in fs.find_contexts()
        ]
        preset = self.context.executor.\
            fzf(variants, prompt='Preset')
        if not preset:
            return
        src, src_path = preset.split(' ', 1)

        variants = ['default', src]
        if set(variants) == 1:
            dst = src
        else:
            dst = self.context.executor.\
                fzf(variants, prompt='New context')
            if not dst:
                return

        additional_import = fs.additional_import()
        existing_additional_import = fs.existing_additional_import()

        variants = existing_additional_import + [
            path
            for path in additional_import
            if path not in existing_additional_import
        ]

        dst_path = self.context.executor.\
            fzf(variants, prompt='Install path', no_sort=True)
        if not dst_path:
            return

        if not exists(dst_path):
            os.makedirs(dst_path)

        src = join(src_path, src) + '.py'
        dst = join(dst_path, dst) + '.py'

        if exists(dst):
            confirm = 'File "{}" already exists. Override?'.format(dst)
            if not self.context.executor.yesno(confirm):
                return

        copyfile(src, dst)
        logger.info('New context copied to "%s"', dst)

        editor = os.environ.get('EDITOR')
        if not editor:
            return

        self.context.executor.append((editor, dst, ))
