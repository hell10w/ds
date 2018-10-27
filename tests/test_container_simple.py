from ds.environment import get_environment


context = 'container_simple'


def test_switch_context(shell):
    shell.call_ds('switch-context', context)
    assert context == get_environment().get('context')


def test_bad_cmd(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_docker_ds('start', 'none')
    assert result.code == 1


def test_echo(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_docker_ds('start', '/bin/bash', '-c', 'echo ok')
    assert result.code == 0
    assert result.stdout.strip() == 'ok'
