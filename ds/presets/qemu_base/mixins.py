from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import random
from os.path import join

from ds import context
from ds.environment import PwdEnvironment
from ds.utils.drop_empty import drop_empty


class QemuEnvironment(PwdEnvironment):
    env_filename = '.ds-qemu'


class QemuEnvironmentMixin(context.Context):
    def __init__(self, **options):
        self._qemu_enviroment = None
        super(QemuEnvironmentMixin, self).__init__(**options)

    @property
    def qemu_environment(self):
        if self._qemu_enviroment is None:
            self._qemu_enviroment = QemuEnvironment()
        return self._qemu_enviroment


class SocketOperateMixin(QemuEnvironmentMixin):
    def connect_to(self, address):
        protocol, address = address.split(':', 1)
        address, opts = address.split(',', 1)
        if protocol == 'unix':
            self.executor.append(('rlwrap', 'nc', '-U', address))
        elif protocol in ['tcp', 'telnet']:
            self.executor.append(['rlwrap', 'nc'] + address.split(':'))
        else:
            raise NotImplementedError

    def send_to(self, address, data):
        protocol, address = address.split(':', 1)
        address, opts = address.split(',', 1)
        data = data + '\n'
        if protocol == 'unix':
            self.executor.append(('nc', '-U', address), input=data)
            self.executor.commit()
        elif protocol in ['tcp', 'telnet']:
            self.executor.append(['nc'] + address.split(':'), input=data)
            self.executor.commit()
        else:
            raise NotImplementedError

    def format_address(self, protocol, path, **options):
        return ':'.join([
            protocol,
            ','.join(drop_empty(*[
                path,
                ','.join([key for key, value in options.items() if value]),
            ])),
        ])

    def format_unix(self, path, **options):
        return self.format_address('unix', path, **options)

    def format_tcp(self, path, **options):
        return self.format_address('tcp', path, **options)

    def format_telnet(self, path, **options):
        return self.format_address('telnet', path, **options)


class TelnetSerialMixin(SocketOperateMixin):
    @property
    def telnet_address(self):
        default = lambda: '127.0.0.1:{}'.format(random.randint(24000, 25000))
        return self.qemu_environment.get('telnet-address', default=default)

    @property
    def telnet(self):
        if not self.telnet_address:
            return
        nowait = not self.wait_telnet
        return self.format_telnet(self.telnet_address, server=True, nowait=nowait)


class TcpMonitorMixin(SocketOperateMixin):
    @property
    def monitor_address(self):
        default = lambda: '127.0.0.1:{}'.format(random.randint(24000, 25000))
        return self.qemu_environment.get('monitor-address', default=default)

    @property
    def monitor(self):
        if not self.monitor_address:
            return
        return self.format_tcp(self.monitor_address, server=True, nowait=True)


class UnixMonitorMixin(SocketOperateMixin):
    @property
    def monitor_path(self):
        default = join(self.project_root, '.qemu-monitor')
        return self.qemu_environment.get('monitor-path', default=default)

    @property
    def monitor(self):
        if not self.monitor_path:
            return
        return self.format_unix(self.monitor_path, server=True, nowait=True)


class TcpShellMixin(SocketOperateMixin):
    @property
    def shell_address(self):
        default = lambda: '127.0.0.1:{}'.format(random.randint(24000, 25000))
        return self.qemu_environment.get('shell-address', default=default)

    @property
    def shell(self):
        if not self.shell_address:
            return
        nowait = not self.wait_shell
        return self.format_telnet(self.shell_address, server=True, nowait=nowait)


class UnixShellMixin(SocketOperateMixin):
    @property
    def shell_path(self):
        default = join(self.project_root, '.qemu-shell')
        return self.qemu_environment.get('shell-path', default=default)

    @property
    def shell(self):
        if not self.shell_path:
            return
        nowait = not self.wait_shell
        return self.format_unix(self.shell_path, server=True, nowait=nowait)
