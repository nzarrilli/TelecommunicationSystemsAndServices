__author__ = 'nzarrilli'


class Host(object):
    mac_address = ""
    port = 0
    dpid = 0

    # The class "constructor" - It's actually an initializer
    def __init__(self, mac_address, port, dpid):
        self.mac_address = mac_address
        self.port = port
        self.dpid = dpid
