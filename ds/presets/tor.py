#!/usr/bin/env ds
from base_tor import TorContext


class Context(TorContext):
    pass

    #  bandwidth = None  # a tor relay bandwidth limit in KB, IE 50
    #  password = 'tor'  # configure HashedControlPassword for control port
    #  timezone = 'UTC'  # configure the zoneinfo timezone, IE EST5EDT
    #  countries = None  # configure the country to use for exit node selection
