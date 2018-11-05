from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from logging import getLogger

from ds.command import Command
from ds.utils.flatten import flatten


logger = getLogger()


class Help(Command):
    short_help = 'Show all possible context modules'

    def invoke_with_args(self, args):
        pass


class CreateDisk(Command):
    usage = '[--format=<format>] [--size=<size>] [<name>]'

    def invoke_with_args(self, args):
        size = args.get('<size>', None) or '1G'
        format_ = args.get('<format>', None) or 'qcow2'
        name = args.get('<name>', None)
        if not name:
            name = 'disk-{}-{}.{}'.format(self.context.project_name,
                                          size, format_)
        self.context.executor.append(flatten((
            self.context.qemu_img,
            'create',
            ('-f', format_),
            name,
            size,
        )))


class RunIso(Command):
    usage = '<iso> [<args>...]'

    def invoke_with_args(self, args):
        self.context.start(('-cdrom', args.get('<iso>'), args.get('<args>')))


class RunDisk(Command):
    usage = '<disk> [<args>...]'

    def invoke_with_args(self, args):
        self.context.start(('-hda', args.get('<disk>'), args.get('<args>')))


class RunIsoAndDisk(Command):
    usage = '--iso=<iso> --disk=<disk> [<args>...]'

    def invoke_with_args(self, args):
        self.context.start(('-hda', args.get('<disk>'),
                            '-cdrom', args.get('<iso>'),
                            args.get('<args>')))


class Start(Command):
    consume_all_args = True

    def invoke_with_args(self, args):
        self.context.executor.append(flatten((
            self.context.qemu_bin,
            self.context.get_run_options(),
            args,
        )))
        if self.context.vnc:
            self.context.viewer()


class Viewer(Command):
    def invoke_with_args(self, args):
        display = self.context.qemu_environment. \
            get('display')
        assert display

        address = '{host}:{display}'.format(host=self.context.vnc_host,
                                            display=5900 + display)

        self.context.executor.append(flatten((
            self.context.viewer_bin,
            address,
        )))


class UnixShell(Command):
    def invoke_with_args(self, args):
        shell = self.context.shell
        if not shell:
            logger.error('Context option `shell` is not defined')
            return
        self.context.connect_to(shell)


class MonitorShell(Command):
    def ensure_monitor(self):
        if not self.context.monitor:
            logger.error('Context option `monitor` is not defined')
            return
        return True

    def invoke_with_args(self, args):
        if not self.ensure_monitor():
            return
        self.context.connect_to(self.context.monitor)


class Stop(MonitorShell):
    def invoke_with_args(self, args):
        if not self.ensure_monitor():
            return
        self.context.send_to(self.context.monitor, 'quit')


class Reset(MonitorShell):
    def invoke_with_args(self, args):
        if not self.ensure_monitor():
            return
        self.context.send_to(self.context.monitor, 'system_reset')


class Info(MonitorShell):
    consume_all_args = True

    def invoke_with_args(self, args):
        if not self.ensure_monitor():
            return
        self.context.send_to(self.context.monitor, ' '.join([
            'info',
            ' '.join(args),
        ]) + '\n')


class Kill(MonitorShell):
    def invoke_with_args(self, args):
        self.context.executor.append(('ps', 'ax'))
        result = self.context.executor.commit()
        if result.code:
            logger.error('Can\'t get a process list')
            return

        stdout = result.stdout.decode('utf-8').split('\n')
        for item in stdout:
            is_qemu = self.context.qemu_bin in item and \
                      '-name {}'.format(self.context.name) in item
            if not is_qemu:
                continue

            pid = item.split(' ', 1)[0]
            self.context.executor.append(('kill', pid))
            return

        logger.error('Process is not found')
