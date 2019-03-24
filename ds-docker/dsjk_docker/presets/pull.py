from __future__ import unicode_literals
import os

from dsjk_docker.presets.base import PullContext
from dsjk_docker.presets.base import DefaultNaming
from dsjk_docker.presets.base import UserMixin
from dsjk_docker.presets.base import HomeMountsMixin
from dsjk_docker.presets.base import ProjectMountMixin


class Context(ProjectMountMixin, UserMixin, HomeMountsMixin,
              DefaultNaming, PullContext):
    @property
    def default_image(self):
        return os.environ.get('IMAGE', 'debian')

    @property
    def default_tag(self):
        return os.environ.get('TAG', 'latest')

    def get_run_options(self, **options):
        options['detach'] = bool(os.environ.get('DETACH', None))
        options['auto_remove'] = bool(os.environ.get('AUTO_REMOVE', True))
        return super(Context, self).get_run_options(**options)
