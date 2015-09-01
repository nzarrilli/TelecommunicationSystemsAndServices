__author__ = 'telcolab'

class Sorgente(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, mac_address, gruppoMulticast):
        self.mac_address = mac_address
        self.gruppoMulticast = gruppoMulticast
        self.listaMacDest = []

    def addApplicationClient(self, mac_address):
        self.listaMacDest.append(mac_address)


