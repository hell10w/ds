# pylint: disable=unused-import
from base_tmux import hs
from base_tmux import LAYOUT_EVEN_HORIZONTAL
from base_tmux import LAYOUT_EVEN_VERTICAL
from base_tmux import LAYOUT_MAIN_HORIZONTAL
from base_tmux import LAYOUT_MAIN_VERTICAL
from base_tmux import LAYOUT_TILED
from base_tmux import TmuxSessionContext
from base_tmux import vs
from base_tmux import w


class Context(TmuxSessionContext):
    def get_schema(self):
        """
        [
            w(name='first')(
                'uname -a',
            ),
            w(name='second', path='/tmp/')(
                'date',
                'htop',
            ),
            w()(
                'echo "hi"',
                vs(path='/var/tmp')(
                    'l',
                    'date',
                    hs(
                        'echo "ololo"',
                    ),
                    hs(
                        'echo "alalala"',
                    ),
                ),
            ),
        ]
        """
        return []
