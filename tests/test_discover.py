from os.path import join

from ds.discover import get_modules
from ds.path import pwd


def test_modules_enumeration():
    assert get_modules(join(pwd(), './.ds/discover/')) == list('abc')
