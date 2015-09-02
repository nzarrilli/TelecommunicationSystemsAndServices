__author__ = 'telcolab'


class Source(object):

    # The class "constructor" - It's actually an initializer
    def __init__(self, mac_address, multicast_id):
        self.mac_address = mac_address
        self.multicast_id = multicast_id
        self.mac_destination_list = []

    def add_application_client(self, mac_address):
        self.mac_destination_list.append(mac_address)


