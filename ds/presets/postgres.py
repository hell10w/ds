from base_container import ForeignContext
from base_container import PersistentContext
from base_pull import Context as PullContext
from base_postgres import PostgresContext


class Context(PostgresContext, ForeignContext, PersistentContext, PullContext):
    default_image = 'postgres'
