from logging import getLogger

from ds.import_tools import try_to_import


logger = getLogger(__name__)


def main():
    module = try_to_import('ds.flow')
    Flow = getattr(module, 'Flow')
    while True:
        Flow = Flow().run()
        if Flow is None:
            break


if __name__ == '__main__':
    main()
