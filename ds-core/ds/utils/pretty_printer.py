from collections import OrderedDict
from pprint import pformat
from logging import getLogger


logger = getLogger(__name__)


def pretty_print_object(instance):
    for key in dir(instance):
        if key.startswith('_'):
            continue
        try:
            value = getattr(instance, key)
        except:
            logger.error('Error while getting value of "%s"', key)
            continue
        if callable(value):
            continue
        if isinstance(value, OrderedDict):
            value = dict(value)
        formatted_value = pformat(value, indent=1)
        sep = {
            False: ' ',
            True: '\n',
        }['\n' in formatted_value]
        print((':' + sep).join([key, formatted_value]))
