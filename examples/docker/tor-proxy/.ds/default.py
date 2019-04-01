from __future__ import unicode_literals

from dsjk_docker.presets.base import PullContext


class Context(PullContext):
    default_image = 'dperson/torproxy'
    container_name = 'tor'

    def get_run_options(self, **options):
        options['detach'] = True
        return super(Context, self).get_run_options(**options)
