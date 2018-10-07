from python import PythonContext


class JupyterContext(PythonContext):
    """
    https://jupyter-docker-stacks.readthedocs.io/
    """

    networks = 'host',
