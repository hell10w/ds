import pytest

from ds import utils
from ds.command import kebab_to_snake


class ComplexObject:
    a = 0
    b = 'test'
    c = list(range(3))
    d = None
complex_object = ComplexObject()


def test_flatten():
    case = ('a', 'b', ['c'], ('d', 'e', ('f', 'g'), 'h'))
    assert utils.flatten(case) == list('abcdefgh')


def test_interactive():
    try:
        utils.is_interactive()
    except Exception:
        pytest.fail('is_interactive')


def test_tty():
    try:
        utils.get_tty_size()
        utils.get_tty_width()
    except Exception:
        pytest.fail('tty')


def test_random_passwords():
    assert utils.generate_random_string(10, 'a') == ('a' * 10)
    assert len(utils.generate_random_string(10)) == 10


def test_pretty_printer(capsys):
    utils.pretty_print_object(complex_object)
    captured = capsys.readouterr()
    assert captured.out == 'a: 0\nb: \'test\'\nc: [0, 1, 2]\nd: None\n'


def test_drop_empty():
    drop = utils.drop_empty(None, 'a', {}, 'b', None, None, 'c', 0)
    assert drop == ['a', {}, 'b', 'c', 0]


@pytest.mark.parametrize('a,b', [
    ('', ''),
    ('TestCase', 'test-case'),
    ('1Test', '1-test'),
    ('Test1Case', 'test1-case'),
])
def test_drop_empty(a, b):
    assert kebab_to_snake(a) == b
