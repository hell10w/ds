import sys
from logging import getLogger
from collections import namedtuple
from functools import partial

try:
    import libtmux
except ImportError:
    print('Install libtmux with `pip install libtmux`')
    sys.exit()

from ds import context
from ds import fs
from ds.command import Command

logger = getLogger(__name__)

LAYOUT_EVEN_HORIZONTAL = 'even-horizontal'
LAYOUT_EVEN_VERTICAL = 'even-vertical'
LAYOUT_MAIN_HORIZONTAL = 'main-horizontal'
LAYOUT_MAIN_VERTICAL = 'main-vertical'
LAYOUT_TILED = 'tiled'


class TmuxSessionContext(context.Context):
    # https://libtmux.git-pull.com/en/latest/api.html#server-object
    tmux_server_kwargs = {}

    @property
    def session_name(self):
        return fs.get_project_name()

    @property
    def windows(self):
        return [
            w(
                'uname -a',
                name='first',
            ),
            w(
                'date',
                'htop',
                name='second',
                path='/tmp/',
            ),
            w(
                'echo "hi"',
                vs(
                    'l',
                    'date',
                    hs(
                        'echo "ololo"',
                    ),
                    hs(
                        'echo "alalala"',
                    ),
                    path='/var/tmp',
                ),
            ),
        ]

    @property
    def envs(self):
        return {}

    def get_all_commands(self):
        return super(TmuxSessionContext, self).get_all_commands() + [
            Sessions,
            Status,
            Attach,
            Up,
            Kill,
        ]


class Context(TmuxSessionContext):
    pass


class Window(object):
    def __init__(self, *args, **kwargs):
        self.items = args
        self.name = kwargs.get('name', None)
        self.path = kwargs.get('path', None)
        self.layout = kwargs.get('layout', None)
        self.opts = kwargs.get('opts', None) or {}

    def realize(self, session, index):
        window = session.new_window(window_name=self.name,
                                    start_directory=self.path,
                                    window_index=index,
                                    attach=index == 0)

        for option, value in self.opts.items():
            window.set_window_option(option, value)
        if self.layout:
            window.set_window_layout(self.layout)

        pane = window.list_panes()[0]
        Split.realize_items(pane, self.items)
        #  for item in self.items:
        #      if isinstance(item, Split):
        #          pane = item.realize(session, window, pane)
        #      else:
        #          pane.send_keys(item)
        #          pane.enter()

        return window

w = Window


class Split(object):
    def __init__(self, *args, **kwargs):
        self.items = args
        self.path = kwargs.get('path', None)
        self.width = kwargs.get('width', None)
        self.height = kwargs.get('height', None)
        self.vertical = not kwargs.get('vertical', True)

    @classmethod
    def realize_items(cls, base_pane, items):
        for item in items:
            if isinstance(item, Split):
                item.realize(base_pane)
            else:
                base_pane.send_keys(item)
                base_pane.enter()

    def realize(self, pane):
        pane = pane.split_window(start_directory=self.path,
                                 vertical=self.vertical)

        if self.width is not None:
            pane.set_width(self.width)
        if self.height is not None:
            pane.set_height(self.height)

        Split.realize_items(pane, self.items)

        return pane

s = Split
vs = Split
hs = partial(Split, vertical=False)


class TmuxCommand(Command):
    @property
    def server(self):
        server = getattr(self.context, '_tmux_server', None)
        if server is None:
            server = libtmux.Server(**self.context.tmux_server_kwargs)
            setattr(self.context, '_tmux_server', server)
        return server

    @property
    def session(self):
        return self.server.find_where({
            'session_name': self.context.session_name,
        })

    def ensure_session_exists(self, expected=True):
        if bool(self.session) ^ expected:
            logger.error('Session %s', {
                False: 'exists',
                True: 'is not exists',
            }[expected])
            return False
        return True


class Sessions(TmuxCommand):
    short_help = 'Show all sessions'

    def invoke_with_args(self, args):
        from pprint import pprint
        pprint(self.server.list_sessions())


class Up(TmuxCommand):
    short_help = 'Start session'

    def invoke_with_args(self, args):
        if not self.ensure_session_exists(expected=False):
            return

        session = self.server.new_session(session_name=self.context.session_name)
        for key, value in self.context.envs.items():
            session.set_environment(key, value)

        windows = self.context.windows
        if not windows:
            return

        temporary = session.list_windows()[0]
        temporary.move_window(len(windows))

        for index, window in enumerate(windows):
            window.realize(session, index)

        temporary.kill_window()


class Kill(TmuxCommand):
    short_help = 'Kill session'

    def invoke_with_args(self, args):
        if not self.ensure_session_exists():
            return
        self.session.kill_session()


class Status(TmuxCommand):
    short_help = 'Session status'

    def invoke_with_args(self, args):
        raise NotImplementedError


class Attach(TmuxCommand):
    short_help = 'Attach session'

    def invoke_with_args(self, args):
        if not self.ensure_session_exists():
            return
        self.session.attach_session()
