from ds import errors


context = 'bad-context'


def test_bad_context(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('-h')
    assert result.code == errors.NO_CONTEXT_MODULE


def test_fallback(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('-h')
    assert result.code == errors.NO_CONTEXT_MODULE
    result = shell.call_ds('-h')
    assert result.code == 0
