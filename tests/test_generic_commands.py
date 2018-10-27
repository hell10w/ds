from ds.environment import get_environment


context = 'dsjk'


def test_switch_context(shell):
    shell.call_ds('switch-context', context)
    assert context == get_environment().get('context')


def test_show_context(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('show-context')
    assert result.code == 0


def test_edit_context(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('edit-context')
    assert result.code == 0


def test_list_context(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('list-contexts')
    assert result.code == 0


def test_install_autocomplete(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('install-autocomplete')
    assert result.code == 0
