__author__ = 'telcolab'


class Switch(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, dpid, ports):
        self.dpid = dpid
        self.ports = ports
