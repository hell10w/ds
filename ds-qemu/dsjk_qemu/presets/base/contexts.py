from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from logging import getLogger
import random

from ds import context
from dsjk_qemu.presets.base import commands
from dsjk_qemu.presets.base import mixins


logger = getLogger(__name__)


class BaseQemuContext(mixins.SocketOperateMixin, context.Context):
    name = None

    enable_kvm = True

    memory = None
    smp = None

    soundhw = None

    display = None
    nographic = None

    cdrom = None
    hda = None
    hdb = None
    hdc = None
    hdd = None

    drive = ()
    net = ()
    device = ()
    usbdevice = 'tablet',
    serial = ()
    chardev = ()

    daemonize = False

    vnc = None

    monitor = None

    telnet = None
    wait_telnet = False

    shell = None
    wait_shell = False

    qemu_arch = 'x86_64'
    viewer_bin = 'xvncviewer'
    qemu_img = 'qemu-img'

    @property
    def qemu_bin(self):
        return 'qemu-system-{}'.format(self.qemu_arch)

    def get_run_options(self):
        return (
            ('-name', str(self.name)) if self.name else (),
            '-daemonize' if self.daemonize else (),
            '-enable-kvm' if self.enable_kvm else (),
            ('-m', str(self.memory)) if self.memory else (),
            ('-smp', str(self.smp)) if self.smp else (),
            ('-soundhw', self.soundhw) if self.soundhw else (),
            ('-display', self.display) if self.display else (),
            '-nographic' if self.nographic else (),
            [
                ('-serial', item)
                for item in self.serial
            ],
            [
                ('-net', item)
                for item in self.net
            ],
            [
                ('-drive', item)
                for item in self.drive
            ],
            [
                ('-usbdevice', item)
                for item in self.usbdevice
            ],
            [
                ('-device', item)
                for item in self.device
            ],
            [
                ('-chardev', item)
                for item in self.chardev
            ],
            ('-cdrom', self.cdrom) if self.cdrom else (),
            ('-hda', self.hda) if self.hda else (),
            ('-hdb', self.hdb) if self.hdb else (),
            ('-hdc', self.hdc) if self.hdc else (),
            ('-hdd', self.hdd) if self.hdd else (),
            ('-vnc', self.vnc) if self.vnc else (),
            ('-monitor', self.monitor) if self.monitor else (),
            ('-serial', self.shell) if self.shell else (),
            ('-serial', self.telnet) if self.telnet else (),
        )

    def get_commands(self):
        return super(BaseQemuContext, self).get_commands() + [
            commands.CreateDisk,
            commands.Start,
            commands.RunIso,
            commands.RunDisk,
            commands.RunIsoAndDisk,
            commands.Reset if self.monitor else None,
            commands.Stop if self.monitor else None,
            commands.Info if self.monitor else None,
            commands.AttachMonitor if self.monitor else None,
            commands.AttachShell if self.shell else None,
            commands.AttachTelnet if self.telnet else None,
            commands.Viewer if self.vnc else None,
            commands.Kill,
        ]


class BasicQemuContext(mixins.TcpMonitorMixin, mixins.TelnetSerialMixin,
                       BaseQemuContext):
    smp = None
    memory = 1024

    soundhw = 'ac97'

    net = 'nic', 'user',

    display = 'none'

    nographic = None
    daemonize = True

    vnc_host = '127.0.0.1'
    vnc_display = None

    def get_name(self):
        return self.project_name

    @property
    def name(self):
        return self.get_name()

    @property
    def vnc(self):
        display = self.vnc_display
        if display is None:
            default = random.randint(0, 300)
            display = self.qemu_environment.get('display', default=default)
        return '{host}:{display}'.format(host=self.vnc_host, display=display)
