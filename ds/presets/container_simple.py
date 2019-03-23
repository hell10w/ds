from __future__ import unicode_literals
import os

from ds.presets.docker_base import PullContext
from ds.presets.docker_base import DefaultNaming
from ds.presets.docker_base import UserMixin
from ds.presets.docker_base import HomeMountsMixin
from ds.presets.docker_base import ProjectMountMixin


class Context(ProjectMountMixin, UserMixin, HomeMountsMixin,
              DefaultNaming, PullContext):
    @property
    def default_image(self):
        return os.environ.get('DS_IMAGE', 'debian')

    @property
    def default_tag(self):
        return os.environ.get('DS_TAG', 'latest')

    def get_run_options(self, **options):
        options['detach'] = bool(os.environ.get('DS_DETACH', None))
        options['auto_remove'] = bool(os.environ.get('DS_AUTO_REMOVE', True))
        return super(Context, self).get_run_options(**options)
