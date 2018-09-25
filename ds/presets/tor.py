from base_container import Shell, ForeignContext, PersistentContext
from base_pull import Context as PullContext


class Context(PullContext, ForeignContext, PersistentContext):
    default_image = 'dperson/torproxy'
    container_name = 'tor'
