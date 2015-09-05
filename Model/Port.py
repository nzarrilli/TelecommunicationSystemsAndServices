__author__ = 'telcolab'


class Port(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, port_no, status, host=None, switch=None):
        self.port_no = port_no
        self.status = status
        self.host = host
        self.switch = switch

    def set_port(self, port_no):
        self.port_no = port_no

    def get_port(self):
        return self.port_no

    def set_status(self, status):
        self.status = status

    def set_host(self, host):
        self.host = host

    def set_switch(self, switch):
        self.switch = switch
