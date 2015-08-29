__author__ = 'telcolab'

class NetworkModel(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self):
        self.hosts = {} # dizionario degli hosts. chiave: mac_addr, valore: oggetto host
        self.switches = {} # dizionario degli switches. chiave: dpid, valore: oggetto switch
        self.sensori = {} # dizionario dei sensori. chiave: mac_addr, valore: oggetto sensore

    def addHost(self, host):
        self.hosts[host.mac_address] = host

    def addSwitch(self, switch):
        self.switches[switch.dpid] = switch

    def addSensore(self, sensore):
        self.sensori[sensore.mac_address] = sensore