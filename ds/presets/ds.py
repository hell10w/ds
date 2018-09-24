from logging import getLogger

from ds import context
from ds import fs
from ds.command import Command

logger = getLogger(__name__)


class DockerContext(context.Context):
    def get_all_commands(self):
        return super(DockerContext, self).get_all_commands() + [
            ListContexts,
            InstallAutocomplete,
        ]


class ListContexts(Command):
    def invoke_with_args(self, args):
        print(' '.join(fs.find_contexts()))


class InstallAutocomplete(HiddenCommand):
    usage = 'usage: {name} [<shell>]'

    def invoke_with_args(self, args):
        shell = args['<shell>'] or 'bash'
        script = fs.relative('autocomplete', shell)
        if not fs.exists(script):
            logger.error('Unknown shell: %s', shell)
            return
        #  self.context.executor()
