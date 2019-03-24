from __future__ import unicode_literals
from __future__ import print_function
import sys
from logging import getLogger

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter

from ds.utils import flatten
from ds.utils import drop_empty


logger = getLogger(__name__)


class Repl(object):
    RELOAD, QUIT = range(1, 3)
    repl_actions = {
        'r': RELOAD,
        'reload': RELOAD,
        'q': QUIT,
        'quit': QUIT,
    }

    def __init__(self, context):
        self.context = context

    def __call__(self, args):
        completer = self.completer()
        style = self.style()

        session = PromptSession(
            message='> ',
            bottom_toolbar=self.bottom_toolbar,
            vi_mode=True,
            complete_while_typing=True,
            completer=completer,
            style=style,
        )

        while True:
            try:
                input_ = session.prompt()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

            try:
                self.process_input(input_)
            except KeyboardInterrupt:
                pass

        logger.info('Done')

    def call_repl(self, input_):
        repl_action = self.repl_actions.get(input_, None)

        if repl_action == self.RELOAD:
            self.context.executor.append(sys.argv)
            self.context.executor.commit(replace=True)

        elif repl_action == self.QUIT:
            sys.exit()

        else:
            logger.error('Unknown repl command')

    def call_shell(self, input_):
        args = flatten([
            '/bin/bash',
            '-c',
            input_,
        ])
        self.context.executor.\
            append(args, skip_stdin=True, skip_stdout=True, skip_stderr=True)
        self.context.executor.commit()

    def call_context(self, input_):
        args = flatten([sys.argv[:-1], input_])
        self.context.executor.\
            append(args, skip_stdin=True, skip_stdout=True, skip_stderr=True)
        self.context.executor.commit()

    def process_input(self, input_):
        if not input_:
            return

        if input_.startswith(':'):
            return self.call_repl(input_[1:])

        elif input_.startswith('!'):
            return self.call_shell(input_[1:])

        return self.call_context(input_)

    def bottom_toolbar(self):
        return ' '.join(drop_empty(
            self.context.project_name,
            self.context.project_root,
            self.context.source_file,
        ))

    def completer(self):
        variants = []
        # variants += list(map(six.u, self.context.commands.keys()))
        variants += list(self.context.commands.keys())
        variants += list(self.repl_actions.keys())
        variants += ['-h', ]
        return WordCompleter(variants)

    def style(self):
        return Style.from_dict({
            'completion-menu.completion': 'bg:#008888 #ffffff',
            'completion-menu.completion.current': 'bg:#00aaaa #000000',
            'scrollbar.background': 'bg:#88aaaa',
            'scrollbar.button': 'bg:#222222',
        })
