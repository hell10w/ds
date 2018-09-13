from ds.command import Command


class Start(Command):
    class Meta:
        usage = 'usage: {name} [<args>...]'
        consume_all_args = True

    def invoke_with_args(self, args):
        return [
            ('docker', 'run'),
            '-d' if self.context.detach,
            '--rm' if self.context.rm,
            ('-u', '{}:{}'.format(self.context.uid, self.context.gid)) if self.context.gid is not None,
            [
                ('-v', mountpoint)
                for mountpoint in self.context.mounts
            ],
            ('--name', self.context.container_name),
            self.context.image_name,
            args.get('<args>'),
        ]


class Stop(Command):
    def invoke_with_args(self, args):
        return [
            ('docker', 'stop'),
            self.context.container_name,
        ]


class Restart(Command):
    class Meta:
        usage = 'usage: {name} [<args>...]'
        consume_all_args = True

    def invoke_with_args(self, args):
        with ignore_errors():
            self.flow.invoke_command('stop')
        return self.flow.invoke_command('start')
