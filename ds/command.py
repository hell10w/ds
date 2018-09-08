from weakref import ref

from six import with_metaclass

from ds import meta


class CommandMeta(meta.CollectMeta):
    meta_defaults = dict(
        abstract=False,
        hidden=False,
        name=meta.AUTOFILL,
        usage='',
        short_help='',
    )


class Command(with_metaclass(CommandMeta)):
    class Meta:
        abstract = True

    def __init__(self, context):
        self._context = ref(context)

    @property
    def context(self):
        return self._context()


class Test(Command):
    class Meta:
        pass


class Test2(Command):
    class Meta:
        hidden = True


class Test3(Command):
    pass


class TestThis(Command):
    pass
