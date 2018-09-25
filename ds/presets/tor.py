from base_container import Shell
from base_pull import Context as _Context


class Context(_Context):
    default_image = 'dperson/torproxy'

    mount_project_root = False
    working_dir = None

    uid = None

    remove_on_stop = False

    detach = True

    container_name = 'tor'

    def get_all_commands(self):
        return super(Context, self).get_all_commands() + [
            #
        ]
