__author__ = 'telcolab'


class NetworkModel(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, switches, sources):
        self.switches = switches
        self.sources = sources
