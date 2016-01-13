__author__ = 'telcolab'


class NetworkModel(object):
    # The class "constructor" - It's actually an initializer
    def __init__(self, switches, sources):
        self.switches = switches
        self.sources = sources

    # Restituisce lo switch
    def get_switch(self, mac_address_source):
        global first_switch

        for key in self.switches:
            if self.switches[key].ports.keys().__contains__(mac_address_source):
                first_switch = self.switches[key]
                break

        return first_switch
