__author__ = 'nzarrilli'


class Port(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, port_no, status=None, host=None):
        self.port_no = port_no
        self.status = status
        self.host = host
