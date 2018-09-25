from base_container import ForeignContext
from base_container import PersistentContext
from base_pull import Context as PullContext


class Context(PullContext, ForeignContext, PersistentContext):
    default_image = 'dperson/torproxy'
    container_name = 'tor'
