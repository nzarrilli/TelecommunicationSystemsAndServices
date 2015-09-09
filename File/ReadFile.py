import os
import re

from Model.Host import Host
from Model.Switch import Switch
from Model.Port import Port
from Model.Source import Source

__author__ = 'telcolab'


# Funzione che si occupa della apertura del file
def __open_file__(filename):
    try:
        base_dir = os.getenv("HOME")
        ryu_dir = "ryu"
        app_dir = "app"

        # Creazione della path
        path = os.path.join(base_dir, ryu_dir, ryu_dir, app_dir, filename)

        # Apertura file
        in_file = open(path, "r")

        return in_file
    except IOError, ex:
        print ex

    return None


# Funzione che si occupa di chiudere il file precedentemente aperto
def __close_file__(in_file):
    # Close file
    in_file.close()

    return None


# Funzione che legge tutti gli switches contenuti nel file "Switches.txt"
def get_switches():
    filename = "Switch.txt"

    # Apertura file
    in_file = __open_file__(filename)

    switches_dict = {}

    # Lettura di tutte le linee del file
    for line in in_file:
        content = re.split("[<> ,]+", line)

        # Recupero le informazioni
        dpid_switch = content[1].split("=")[1]
        ports = __set_ports__({}, content[2:len(content) - 1])

        switches_dict[dpid_switch] = Switch(dpid_switch, ports)

    # Chiusura file
    __close_file__(in_file)

    return switches_dict


# Funzione che si occupa di inizializzare le porte degli switches
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


# Funzione che legge tutti gli hosts contenuti nel file "Host.txt"
def get_hosts(network):
    filename = "Host.txt"

    # Apertura file
    in_file = __open_file__(filename)

    # Lettura di tutte le linee del file
    for line in in_file:
        mac_address = re.split("[= ]+", line)[2]
        port = re.split("[= ]+", line)[4]
        dpid = re.split("[= >]+", line)[6]

        # Cambio la chiave del dizionario della vecchia porta e poi elimino quella vecchia
        network[dpid].ports[mac_address] = network[dpid].ports.pop(port)
        # Aggiungo l'host alla lista delle porte
        network[dpid].ports[mac_address].set_host(Host(mac_address))

    # Chiusura file
    __close_file__(in_file)

    return network


# Aggiungo alla rete i collegamenti tra i vari switch
def add_links(network):
    filename = "Link.txt"

    # Apertura file
    in_file = __open_file__(filename)

    suffix_dpid = "dpid="

    # Lettura di tutte le linee del file
    for line in in_file:
        dpid_source = re.split("[<>,= ]+", line)[2]
        port_source = re.split("[<>,= ]+", line)[4]
        status_source = re.split("[<>,= ]+", line)[5]
        dpid_destination = re.split("[<>,= ]+", line)[8]

        # Aggiungo il dpid dello switch di destinazione
        network[dpid_source].ports[suffix_dpid + dpid_destination] = network[dpid_source].ports.pop(port_source)
        # Aggiorno la porta
        network[dpid_source].ports[suffix_dpid + dpid_destination].set_port(port_source)
        # Aggiorno lo stato della porta
        network[dpid_source].ports[suffix_dpid + dpid_destination].set_status(status_source)
        # Aggiungo lo switch di destinazione
        network[dpid_source].ports[suffix_dpid + dpid_destination].set_switch(network[dpid_destination])

    # Chiusura file
    __close_file__(in_file)

    return network


# Aggiungo alla rete i percorsi tra i vari switch
def add_paths(network):
    filename = "Path.txt"

    # Apertura file
    in_file = __open_file__(filename)

    # Lettura di tutte le linee del file
    for line in in_file:
        new_line = re.split("[\{\}]+", line)
        source = new_line[1].replace(": ", "")

        destination_dict = __get_destination__({}, new_line[2].replace("],", "]").replace(", ", ",").replace(": ",
                                                                                                             " ").split(
            " "))

        network[source].set_paths(destination_dict)

    # Chiusura file
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

    # Apertura file
    in_file = __open_file__(filename)

    sources_dict = {}

    # Lettura di tutte le linee del file
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

    # Chiusura file
    __close_file__(in_file)

    return sources_dict
