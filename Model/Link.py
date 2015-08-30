__author__ = 'telcolab'


class Link(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, dpidSorg, portSorg, dpidDest, portDest):
        self.dpidSorg = dpidSorg
        self.portSorg = portSorg
        self.dpidDest = dpidDest
        self.portDest = portDest
