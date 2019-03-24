import pytest

from ds.environment import get_environment


context = 'plain-context'


def test_switch_context(shell):
    shell.call_ds('switch-context', context)
    assert context == get_environment().get('context')


def test_additional_summary(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('-h')
    assert result.code == 0
    assert 'Test:\n a  1\n b  2' in result.stdout


def test_commands_list(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('-h')
    assert result.code == 0


@pytest.mark.parametrize('what', [
    None,
    '',
    'test',
    'with space',
])
def test_invoke_command(shell, what):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('echo-test', what)
    assert result.code == 0
    assert result.stdout.strip() == (what or '')
