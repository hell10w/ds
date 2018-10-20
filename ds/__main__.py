import sys
from logging import getLogger

from ds import fs

logger = getLogger(__name__)


def main():
    sys.path = fs.existing_additional_import() + sys.path

    if len(sys.argv) < 2:
        logger.error('Context required')
        sys.exit(1)

    try:
        from context_loader import load_context
    except ImportError:
        from ds.load_context import load_context

    Context = load_context(sys.argv[1])
    if not Context:
        sys.exit(1)

    Context().run()


if __name__ == '__main__':
    main()
