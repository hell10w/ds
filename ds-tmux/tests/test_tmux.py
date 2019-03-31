from dsjk_tmux.presets.base import TmuxSessionContext
from dsjk_tmux.presets.base import w
from dsjk_tmux.presets.base import v
from dsjk_tmux.presets.base import h


class TmuxTestContext(TmuxSessionContext):
    session_name = 'ds-tmux-test'

    def get_schema(self):
        return [
            w(name='test-a', path='/')(
                'date',
            ),
            w(name='test-b', path='/tmp/')(
                v(),
            ),
            w(name='test-c')(),
            w()(),
        ]


def test_context_without_class(capsys):
    context = TmuxTestContext()
    context.up()
    context.inspect(context.session_name)
    captured = capsys.readouterr()
    stdout = captured.out
    context.kill()

    assert stdout
    for window in context.get_schema():
        if not window.name:
            continue
        assert window.name in stdout
