from __future__ import unicode_literals
import sys
from functools import partial
from logging import getLogger

import six
try:
    import libtmux
except ImportError:
    print('Install libtmux with `pip install libtmux`')
    sys.exit(1)

from ds import context
from ds.command import Command

logger = getLogger(__name__)


class SchemaRealizer(object):
    def realize(self, server, context):
        session = server.new_session(session_name=context.session_name)
        for key, value in context.envs.items():
            session.set_environment(key, value)

        windows = context.schema
        if not windows:
            return

        temporary = session.list_windows()[0]
        temporary.move_window(len(windows))

        for index, window in enumerate(windows):
            self.realize_window(session, window, index)

        temporary.kill_window()

    def realize_window(self, session, window_schema, index):
        window = session.new_window(
            window_name=window_schema.name,
            start_directory=window_schema.path,
            window_index=index,
            attach=index == 0)

        for option, value in window_schema.opts.items():
            window.set_window_option(option, value)

        pane = window.list_panes()[0]
        self.realize_items(pane, window_schema.items)

        return window

    def realize_items(self, pane, items):
        for item in items:
            if not item:
                continue
            if isinstance(item, Split):
                self.realize_split(pane, item)
            elif isinstance(item, six.string_types):
                pane.send_keys(item)

    def realize_split(self, previous, split_schema):
        pane = previous.split_window(
            start_directory=split_schema.path, vertical=split_schema.vertical)

        if split_schema.width is not None:
            pane.set_width(split_schema.width)
        if split_schema.height is not None:
            pane.set_height(split_schema.height)

        self.realize_items(pane, split_schema.items)


class TmuxSessionContext(context.Context):
    # https://libtmux.git-pull.com/en/latest/api.html#server-object
    tmux_server_kwargs = {}

    schema_realize_class = SchemaRealizer

    @property
    def session_name(self):
        return self.project_name

    @property
    def schema(self):
        return self.get_schema()

    def get_schema(self):
        return []

    @property
    def envs(self):
        return {}

    def get_commands(self):
        return super(TmuxSessionContext, self).get_commands() + [
            Status,
            Up,
            Kill,
            Attach,
            Inspect,
        ]


class _CollectByCall(object):
    def __init__(self, *args, **kwargs):
        self._items = []

    def __call__(self, *args):
        self._items += args
        return self

    @property
    def items(self):
        return self._items


class Window(_CollectByCall):
    def __init__(self, name=None, path=None, opts=None, **kwargs):
        super(Window, self).__init__()
        self.kwargs = kwargs
        self.name = name
        self.path = path
        self.opts = opts or {}


w = Window


class Split(_CollectByCall):
    def __init__(self,
                 path=None,
                 width=None,
                 height=None,
                 vertical=True,
                 **kwargs):
        super(Split, self).__init__()
        self.kwargs = kwargs
        self.path = path
        self.width = width
        self.height = height
        self.vertical = vertical


s = Split
v = Split
h = partial(Split, vertical=False)


class TmuxCommand(Command):
    @property
    def server(self):
        server = getattr(self.context, '_tmux_server', None)
        if server is None:
            server = libtmux.Server(**self.context.tmux_server_kwargs)
            setattr(self.context, '_tmux_server', server)
        return server

    def find_session_by_name(self, name):
        return self.server.find_where({
            'session_name': name,
        })

    @property
    def session(self):
        return self.find_session_by_name(self.context.session_name)

    def ensure_session_exists(self, expected=True):
        if bool(self.session) ^ expected:
            logger.error('Session %s', {
                False: 'exists',
                True: 'is not exists',
            }[expected])
            return False
        return True


class Up(TmuxCommand):
    short_help = 'Start session'

    def invoke_with_args(self, args):
        if not self.ensure_session_exists(expected=False):
            return

        realizer = self.context.schema_realize_class()
        realizer.realize(self.server, self.context)


class Kill(TmuxCommand):
    short_help = 'Kill session'

    def invoke_with_args(self, args):
        if not self.ensure_session_exists():
            return
        self.session.kill_session()


class Status(TmuxCommand):
    short_help = 'Session status'

    def invoke_with_args(self, args):
        if self.session is None:
            print('Session does not exist')
        else:
            print('Session exists')


class Attach(TmuxCommand):
    short_help = 'Attach session'

    def invoke_with_args(self, args):
        if not self.ensure_session_exists():
            return
        self.session.attach_session()


class Inspect(TmuxCommand):
    usage = 'usage: {name} <session>'
    short_help = 'Inspect session'

    template_window = 'w(name=\'{name}\', path=\'{path}\')(),'

    def invoke_with_args(self, args):
        def escape(value):
            return value.replace('\'', '\\\'')

        session_name = args['<session>']
        session = self.find_session_by_name(session_name)
        assert session, 'Session not found'

        print('session_name = \'{}\''.format(escape(session_name)))

        for window in session.list_windows():
            first_pane = window.list_panes()[0]

            name = window.get('window_name') or ''

            path = first_pane.get('pane_current_path')
            path = path.replace('\'', '\\\'')

            item = self.template_window.format(
                name=escape(name), path=escape(path))
            for line in item.splitlines():
                print(line)
