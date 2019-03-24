from pprint import pformat

from ds.utils import format_columns
from ds.utils import get_tty_width


class Summary(object):
    def __init__(self, title):
        self.title = title

    def render(self):
        pass


class TableSummary(Summary):
    def __init__(self, title, cells):
        self.cells = cells
        super(TableSummary, self).__init__(title)

    def render(self):
        return format_columns(*self.cells)


class FormatSummary(Summary):
    def __init__(self, title, data, **options):
        self.data = data
        self.options = options
        super(FormatSummary, self).__init__(title)

    def render(self):
        opts = self.options
        opts.setdefault('width', max([80, get_tty_width()]))
        return pformat(self.data, **opts)
