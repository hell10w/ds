from base_pull import Context as PullContext
from base_postgres import PostgresContext


class Context(PostgresContext, PullContext):
    default_image = 'postgres'

    detach = True
    remove_on_stop = False

    mount_project_root = False
    working_dir = None
