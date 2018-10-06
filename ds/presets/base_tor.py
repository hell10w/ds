from ds import text
from ds.command import Command
from base_container import ForeignContext
from base_container import PersistentContext
from base_container import Exec
from base_pull import Context as PullContext


class TorContext(PullContext, ForeignContext, PersistentContext):
    """
    https://hub.docker.com/r/dperson/torproxy/
    """

    default_image = 'dperson/torproxy'
    container_name = 'tor'
    restart = 'always'
    networks = 'host',

    bandwidth = None  # a tor relay bandwidth limit in KB, IE 50
    password = 'tor'  # configure HashedControlPassword for control port
    timezone = 'UTC'  # configure the zoneinfo timezone, IE EST5EDT
    countries = None  # configure the country to use for exit node selection

    def get_all_commands(self):
        return super(TorContext, self).get_all_commands() + [
            ShowExternalIp,
            NewNym,
            Heartbeat,
            Dump,
            ClearDnsCache,
        ]

    @property
    def environment(self):
        environment = super(TorContext, self).environment
        text.append_value(environment, 'BW', self.bandwidth)
        text.append_value(environment, 'PASSWORD', self.password)
        text.append_value(environment, 'TZ', self.timezone)
        text.append_value(environment, 'LOCATION', self.countries)
        return environment


class Control(Exec):
    def get_command_args(self):
        return 'torproxy.sh',


class TorControlCommand(Command):
    """
    https://gitweb.torproject.org/torspec.git/tree/control-spec.txt#n415
    """

    control_input = None

    def get_input(self):
        return self.control_input or ''

    def invoke_with_args(self, args):
        input_ = '\r\n'.join([
            'AUTHENTICATE "{}"'.format(self.context.password or ''),
            self.get_input(),
            'QUIT',
            '',
        ])
        client = ('nc', '127.0.0.1', '9051')
        self.context.executor.append(client, input=input_)
        print(self.context.executor.commit().stdout.strip())


class NewNym(TorControlCommand):
    short_help = 'Switch to clean circuits, so new application requests don\'t share any circuits with old ones. Also clears the client-side DNS cache. '
    control_input = 'SIGNAL NEWNYM'


class Heartbeat(TorControlCommand):
    short_help = 'Make Tor dump an unscheduled Heartbeat message to log'
    control_input = 'SIGNAL HEARTBEAT'


class Dump(TorControlCommand):
    short_help = 'Dump stats: log information about open connections and circuits'
    control_input = 'SIGNAL DUMP'


class ClearDnsCache(TorControlCommand):
    short_help = 'Forget the client-side cached IPs for all hostnames'
    control_input = 'SIGNAL CLEARDNSCACHE'


class ShowExternalIp(Command):
    short_help = 'Get an external ip via request to httpbin.org'

    def invoke_with_args(self, args):
        socks = '127.0.0.1:9050'
        url = 'https://httpbin.org/ip'
        self.context.executor.append([
            '/bin/bash',
            '-c',
            'curl -s --socks5 {} {} | jq ".origin"'.format(socks, url),
        ])
        print(self.context.executor.commit().stdout.strip())
