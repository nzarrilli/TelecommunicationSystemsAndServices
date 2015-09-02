__author__ = 'telcolab'


class Switch(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, dpid, ports, path=None):
        self.dpid = dpid
        self.ports = ports
        self.path = path

    def set_paths(self, path):
        self.path = path
