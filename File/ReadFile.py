__author__ = 'telcolab'

import os
import re

from Model.Host import Host
from Model.Switch import Switch
from Model.Port import Port
from Model.Source import Source
from Model.NetworkModel import NetworkModel
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

        destination_dict = __get_destination__({}, new_line[2].replace("],", "]").replace(", ", ",").replace(": ",
                                                                                                             " ").split(
            " "))

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
        for i in range(1, len(nodes) - 1):
            nodes_list.append(nodes[i])

        destination_dict[destination] = nodes_list

        __get_destination__(destination_dict, line[2:len(line)])

    return destination_dict


# Recupero i sorgenti e le destinazioni
def get_sources():
    filename = "Sorgenti.txt"

    # Open file
    in_file = __open_file__(filename)

    sources_dict = {}

    # Read all lines
    for line in in_file:
        new_line = re.split("[\n:]+", line)

        mac_address_sorg = ':'.join(new_line[0:6])
        multicast_id = new_line[6]
        mac_address_dest = ':'.join(new_line[7:13])

        if not sources_dict.keys().__contains__(mac_address_sorg):
            sources_dict[mac_address_sorg] = Source(mac_address_sorg, multicast_id)
            sources_dict[mac_address_sorg].add_application_client(mac_address_dest)
        else:
            temp_source = sources_dict[mac_address_sorg]
            temp_source.add_application_client(mac_address_dest)
            sources_dict[mac_address_sorg] = temp_source

    # Close file
    __close_file__(in_file)

    return sources_dict


# Restituisce lo switch
def __get_switch__(network, mac_address_source):
    global first_switch

    for key in network:
        if network[key].ports.keys().__contains__(mac_address_source):
            first_switch = network[key]
            break

    return first_switch


# Funzione che aggiunge al dizionario la porta di collegamento tra lo switch sorgente e quello di destinazione
def __add_destination_port__(destination_port_dict, dpid_switch, port_no):
    if not destination_port_dict.keys().__contains__(dpid_switch):
        destination_port_dict[dpid_switch] = []
        destination_port_dict[dpid_switch].append(port_no)
    else:
        destination_port_dict[dpid_switch].append(port_no)

    return destination_port_dict


def new(destination_mac_address, current_switch, network_model, destination_port_dict):
    # Recupero le informazioni sullo switch al quale e' collegato l'host di destinazione
    destination_switch = __get_switch__(network_model.network, destination_mac_address)

    # Controlliamo che lo switch corrente non e' lo stesso di quello di destinazione
    if current_switch.dpid != destination_switch.dpid:

        # Recupero dpid dello switch successivo dalla lista dei paths
        next_switch_dpid = current_switch.path[destination_switch.dpid][1]

        # Recupero la porta di collegamento dello switch successivo
        destination_port = current_switch.get_switch_port(next_switch_dpid)

        # Aggiungo al dizionario la porta di collegamento tra lo switch corrente e lo switch successivo
        destination_port_dict = __add_destination_port__(destination_port_dict, current_switch.dpid, destination_port)

        print "Switch", current_switch.dpid, "--> Port", destination_port, "--> Switch", next_switch_dpid

        # Richiamo il metodo passandogli lo switch successivo
        new(destination_mac_address, network[next_switch_dpid], network_model, destination_port_dict)

    else:  # Se siamo arrivati all'ultimo switch dobbiamo inoltrare il pacchetto sulla porta dell'host
        for key_port in destination_switch.ports:
            if destination_switch.ports[key_port].host is not None \
                    and destination_switch.ports[key_port].host.mac_address == destination_mac_address:
                # Recupero la porta di collegamento tra l'host e lo switch
                destination_port = destination_switch.ports[key_port].port_no
                # Aggiungo al dizionario la porta di collegamento tra lo switch corrente e lo switch successivo
                destination_port_dict = __add_destination_port__(destination_port_dict, current_switch.dpid,
                                                                 destination_port)

                print "Switch", current_switch.dpid, "--> Port", destination_port, "--> Host", destination_mac_address
                break

    return destination_port_dict


if __name__ == "__main__":

    # 1 Ottengo il dizionario degli switches
    network = get_switches()

    # 2 Associo gli host ai vari switches
    network = get_hosts(network)

    # 3 Aggiorno il dizionario della rete aggiornando il collegamento tra i vari switches
    network = add_links(network)

    # 4 Aggiorno il dizionario degli switches impostando per ognuno la property "primoHopDict"
    network_model = add_paths(network)

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

    # 5 Ottengo il dizionario dei sorgenti
    sources = get_sources()

    for key in sources:
        print "Source:", sources[key].mac_address
        print "Multicast id:", sources[key].multicast_id
        print "Destination list:", sources[key].mac_destination_list
        print "----------------------------------------------------------------------"

    # 6 Creo il nuovo modello della rete
    network_model = NetworkModel(network, sources)

    # 7 Algoritmo installazione regole ryu
    for source in network_model.sources:
        switch = __get_switch__(network_model.network, source)
        print "#######################################################"
        print "MAC address della sorgente:", source
        print "La sorgente e' collegata alla switch:", switch.dpid
        print "#######################################################"

        # Creo il dizionario che contiene come chiave il DPID dello switch e come valore la lista di porte di
        # destinazione
        destination_port_dict = {}

        # Controllo tutte le possibili destinazioni della sorgente
        for destination_mac_address in network_model.sources[source].mac_destination_list:
            # Stampo la lista dei MAC address delle destinazioni della sorgente
            print "MAC address di destinazione:", destination_mac_address

            # Richiamo la funzione che si occupa di verificare quali sono gli switch o gli host collegati per arrivare
            # alla destinazione
            destination_port_dict = new(destination_mac_address, switch, network_model, destination_port_dict)

            print ""

        for destination_key in destination_port_dict:
            print "DPID:", destination_key
            print "Lista di porte da configurare:", destination_port_dict[destination_key]
            # TODO Aggiungere la chiamata per installare le regole
            RyuRuleCreator.install_rule(destination_key, source, network_model.sources[source].multicast_id,
                                        destination_port_dict[destination_key])
