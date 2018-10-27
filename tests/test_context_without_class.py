from ds import errors


context = 'test-context-without-class'


def test_context_without_class(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('-h')
    assert result.code == errors.NO_CONTEXT_CLASS


def test_fallback(shell):
    shell.call_ds('switch-context', context)
    result = shell.call_ds('-h')
    assert result.code == errors.NO_CONTEXT_CLASS
    result = shell.call_ds('-h')
    assert result.code == 0
