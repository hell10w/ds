import sys
from logging import getLogger

from ds import fs

logger = getLogger(__name__)


def main():
    sys.path = fs.existing_additional_import() + sys.path

    try:
        from context_loader import load_context
    except ImportError:
        from ds.load_context import load_context

    Context = load_context()
    if Context is None:
        logger.error('Context is not loaded')
    Context().run()


if __name__ == '__main__':
    main()
