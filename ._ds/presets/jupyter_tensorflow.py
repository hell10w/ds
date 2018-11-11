from base_jupyter import JupyterContext
from base_pull import Context as PullContext


class Context(PullContext, JupyterContext):
    default_image = 'jupyter/tensorflow-notebook'
