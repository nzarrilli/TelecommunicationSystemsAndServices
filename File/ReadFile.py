__author__ = 'telcolab'

import os
import re

from Model.Host import Host
from Model.Switch import Switch
from Model.Port import Port
from Model.Sorgente import Sorgente
from Network import RyuRuleCreator


def __open_file__(filename):
    try:
        base_dir = os.getenv("HOME")
        ryu_dir = "ryu"
        app_dir = "app"

        # Creazione della path
        path = os.path.join(base_dir, ryu_dir, ryu_dir, app_dir, filename)

        # Open file
        in_file = open(path, "r")

        return in_file
    except IOError, ex:
        print ex

    return None


def __close_file__(in_file):
    # Close file
    in_file.close()

    return None


# Return the dictionary of switches
def get_switches():
    filename = "Switch.txt"

    # Open file
    in_file = __open_file__(filename)

    switches_dict = {}

    # Read all lines
    for line in in_file:
        content = re.split("[<> ,]+", line)

        # Recupero le informazioni
        dpid_switch = content[1].split("=")[1]
        ports = __set_ports__({}, content[2:len(content) - 1])

        switches_dict[dpid_switch] = Switch(dpid_switch, ports)

    # Close file
    __close_file__(in_file)

    return switches_dict


# Retrieving information about the switch ports
def __set_ports__(ports_dict, line):
    if "Port" in line[0]:

        # Recupero le informazioni
        # dpid = line[1].split("=")[1]
        port_no = line[2].split("=")[1]
        status = line[3]

        # Aggiorno al dizionario le porte
        ports_dict[port_no] = Port(port_no, status)

        # Controllo se ci sono altre porte da settare
        if len(line) > 4:
            __set_ports__(ports_dict, line[4: len(line)])

    return ports_dict


# Return the list of hosts
def get_hosts(network):
    filename = "Host.txt"

    # Open file
    in_file = __open_file__(filename)

    # Read all lines
    for line in in_file:
        mac_address = re.split("[= ]+", line)[2]
        port = re.split("[= ]+", line)[4]
        dpid = re.split("[= >]+", line)[6]

        # Cambio la chiave del dizionario della vecchia porta e poi elimino quella vecchia
        network[dpid].ports[mac_address] = network[dpid].ports.pop(port)
        # Aggiungo l'host alla lista delle porte
        network[dpid].ports[mac_address].set_host(Host(mac_address))

    # Close file
    __close_file__(in_file)

    return network


# Aggiungo alla rete i collegamenti tra i vari switch
def add_links(network):
    filename = "Link.txt"

    # Open file
    in_file = __open_file__(filename)

    suffix_dpid = "dpid="

    # Read all lines
    for line in in_file:
        dpid_source = re.split("[<>,= ]+", line)[2]
        port_source = re.split("[<>,= ]+", line)[4]
        status_source = re.split("[<>,= ]+", line)[5]
        dpid_destination = re.split("[<>,= ]+", line)[8]

        # Aggiungo il dpid dello switch di destinazione
        network[dpid_source].ports[suffix_dpid + dpid_destination] = network[dpid_source].ports.pop(port_source)
        # Aggiorno la porta
        network[dpid_source].ports[suffix_dpid + dpid_destination].set_port = port_source
        # Aggiorno lo stato della porta
        network[dpid_source].ports[suffix_dpid + dpid_destination].set_status = status_source
        # Aggiungo lo switch di destinazione
        network[dpid_source].ports[suffix_dpid + dpid_destination].set_switch(network[dpid_destination])

    # Close file
    __close_file__(in_file)

    return network


# Aggiungo alla rete i percorsi tra i vari switch
def add_paths(network):
    filename = "Path.txt"

    # Open file
    in_file = __open_file__(filename)

    # Read all lines
    for line in in_file:
        new_line = re.split("[\{\}]+", line)
        source = new_line[1].replace(": ", "")

        destination_dict = __get_destination__({}, new_line[2].replace("],", "]").replace(", ", ",").replace(": ", " ").split(" "))

        network[source].set_paths(destination_dict)

    # Close file
    __close_file__(in_file)

    return network


# Recupero i nodi
def __get_destination__(destination_dict, line):

    if len(line) >= 2:
        destination = line[0]
        nodes = re.split("[\[\],]+", line[1])

        nodes_list = []

        # Creo la lista dei nodi
        for i in range(1, len(nodes)-1):
            nodes_list.append(nodes[i])

        destination_dict[destination] = nodes_list

        __get_destination__(destination_dict, line[2:len(line)])

    return destination_dict


def get_sorgenti():
    filename = "Sorgenti.txt"

    # Open file
    in_file = __open_file__(filename)

    sensori_dict = {}

    # Read all lines
    for line in in_file:
        mac_address_sorg = re.split("[:]+", line)[1]
        multicastID = re.split("[:]+", line)[2]
        mac_address_dest = re.split("[:]+", line)[3]
        if not sensori_dict.keys().__contains__(mac_address_sorg):
            sensori_dict[mac_address_sorg] = (Sorgente(mac_address_sorg, multicastID))
        else:
            tmpSensore = sensori_dict[mac_address_sorg]
            tmpSensore.addApplicationClient(mac_address_dest)
            sensori_dict[mac_address_sorg] = tmpSensore  # TODO se e' come java quest'istruzione non serve

    # Close file
    __close_file__(in_file)

    return sensori_dict


def installaRegoleRyu(primoSwitch, sensore, networkModel):
    destPortSet = []
    for mac_destinazione in sensore.listaMacDest:
        hostDest = networkModel.hosts[mac_destinazione]
        switchDest = networkModel.switches[hostDest.dpid]
        nextSwitchDpid = primoSwitch.primoHopDict[switchDest.dpid]
        installaRegoleRyu(networkModel.switches[nextSwitchDpid], sensore, networkModel)  # ricorsione
        if nextSwitchDpid != switchDest.dpid:  # se non siamo ancora arrivati all'ultimo switch
            link = primoSwitch.linksDict[nextSwitchDpid]
            if not destPortSet.__contains__(link.portSorg):
                destPortSet.append(link.portSorg)
            if destPortSet.__sizeof__() > 0:
                RyuRuleCreator.install_rule(primoSwitch.dpid, sensore.mac_address, sensore.gruppoMulticast, destPortSet)
        else:  # se siamo arrivati all'ultimo switch dobbiamo inoltrare il pacchetto sulla porta dell'host
            if not destPortSet.__contains__(hostDest.port):
                destPortSet.append(hostDest.port)
                RyuRuleCreator.install_rule(primoSwitch.dpid, sensore.mac_address, sensore.gruppoMulticast, destPortSet)


if __name__ == "__main__":

    # 1 Ottengo il dizionario degli switches
    network = get_switches()

    # 2 Associo gli host ai vari switches
    network = get_hosts(network)

    # 3 Aggiorno il dizionario della rete aggiornando il collegamento tra i vari switches
    network = add_links(network)

    # 4 Aggiorno il dizionario degli switches impostando per ognuno la property "primoHopDict"
    networkModel = add_paths(network)

    # Stampo a video il risultato
    for key in network:
        print "Dpid switch:", key
        if network[key].path is not None:
            print "Paths:", network[key].path
        for key_port in network[key].ports:
            print ""
            print "Key port:", key_port
            print "Port number:", network[key].ports[key_port].port_no
            print "Status:", network[key].ports[key_port].status
            if network[key].ports[key_port].host is not None:
                print "MAC address host:", network[key].ports[key_port].host.mac_address
            if network[key].ports[key_port].switch is not None:
                print "Dpid destination switch:", network[key].ports[key_port].switch.dpid

        print "----------------------------------------------------------------------"

        # 1.4 Ottengo il dizionario dei sensori
        # networkModel.sensori = get_sorgenti()



        # 2 Algoritmo installazione regole ryu
        # for sensore in networkModel.sensori:
        #    host = Host[sensore.mac_address]
        #    primoSwitch = networkModel.switches[host.dpid]
        #    installaRegoleRyu(primoSwitch, sensore, networkModel)
