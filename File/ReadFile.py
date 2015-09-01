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


# Return the list of switches
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
        dpid = line[1].split("=")[1]
        port_no = line[2].split("=")[1]
        status = line[3]

        # Aggiorno al dizionario le porte
        ports_dict[dpid] = Port(port_no, status)

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

        # Associo la porta
        network[dpid].ports[mac_address] = Port(port, None, Host(mac_address))

    # Close file
    __close_file__(in_file)

    return network


def addLinks(networkModel):
    filename = "Link.txt"
    # TODO leggere Link.txt e impostare per ogni switch della rete il dizionario linksDict (chiave: dpidDest, valore: oggetto Link)
    return networkModel


def addPaths(networkModel):
    filename = "Path.txt"
    # TODO leggere Path.txt e impostare per ogni switch della rete il dizionario primoHopDict (chiave: dpidDest, valore: dpid switch successivo)
    return networkModel


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

    # 1.2 Ottengo il dizionario degli host
    network = get_hosts(network)

    # Creazione del NetworkModel
    # network_model = NetworkModel(switches)

    # 1.2 Ottengo il dizionario degli switches
    # networkModel.switches = get_switches()

    # 1.3 Aggiorno il dizionario degli switches impostando per ognuno la property "linksDict"
    # networkModel = addLinks(networkModel)

    # 1.4 Ottengo il dizionario dei sensori
    # networkModel.sensori = get_sorgenti()

    # 1.5 Aggiorno il dizionario degli switches impostando per ognuno la property "primoHopDict"
    # networkModel = addPaths(networkModel)

    # 2 Algoritmo installazione regole ryu
    # for sensore in networkModel.sensori:
    #    host = Host[sensore.mac_address]
    #    primoSwitch = networkModel.switches[host.dpid]
    #    installaRegoleRyu(primoSwitch, sensore, networkModel)
