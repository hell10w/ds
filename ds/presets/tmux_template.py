# pylint: disable=unused-import
from tmux_base import TmuxSessionContext
from tmux_base import v
from tmux_base import h
from tmux_base import w


class Context(TmuxSessionContext):
    def get_schema(self):
        return [
            w(name='first')(
                'uname -a',
            ),
            w(name='second', path='/tmp/')(
                'date',
                'htop',
            ),
            w()(
                'echo "hi"',
                v(path='/var/tmp')(
                    'l',
                    'date',
                    h(
                        'echo "horizontal split 1"',
                    ),
                    h(
                        'echo "horizontal split 2"',
                    ),
                ),
            ),
        ]
