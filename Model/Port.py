__author__ = 'nzarrilli'


class Port(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, dpid, port_no, status):
        self.dpid = dpid
        self.port_no = port_no
        self.status = status
