# pylint: disable=unused-import
from dsjk_tmux.presets.base import TmuxSessionContext
from dsjk_tmux.presets.base import v
from dsjk_tmux.presets.base import h
from dsjk_tmux.presets.base import w


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
