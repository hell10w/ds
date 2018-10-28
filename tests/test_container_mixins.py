import os

from os.path import join, expanduser

from ds.presets.docker_base.mixins import UserMixin
from ds.presets.docker_base.mixins import HomeMountsMixin


def test_user():
    assert UserMixin().get_run_options().get('user') == os.getuid()

    class Context(UserMixin):
        container_user = 999

    assert Context().get_run_options().get('user') == Context.container_user


def test_home_mounts():
    class Context(HomeMountsMixin):
        container_home = 'a', 'b',
        home_mounts = [
            '.',
            '..',
        ]

    context = Context()

    mounts = {
        item['Target']: item['Source']
        for item in context.get_run_options().get('mounts')
    }

    home = expanduser('~')

    for dest in context.container_home:
        for src in context.home_mounts:
            full_dst = join(dest, src)
            assert full_dst in mounts

            full_src = join(home, src)
            assert mounts[full_dst] == full_src
