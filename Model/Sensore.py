__author__ = 'telcolab'

class Sensore(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, mac_address):
        self.mac_address = mac_address
        self.gruppoMulticast = -1
        self.listaMacDest = []

    def addApplicationClient(self, mac_address):
        self.listaMacDest.append(mac_address)


