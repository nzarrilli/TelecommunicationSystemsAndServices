__author__ = 'nzarrilli'

import os
import re

from Model.Host import Host
from Model.Switch import Switch
from Model.Port import Port


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


# Return the list of hosts
def get_hosts():
    filename = "Host.txt"

    # Open file
    in_file = __open_file__(filename)

    hosts_list = []

    # Read all lines
    for line in in_file:
        mac_address = re.split("[= ]+", line)[2]
        port = re.split("[= ]+", line)[4]
        dpid = re.split("[= ]+", line)[6]

        hosts_list.append(Host(mac_address, port, dpid))

    # Close file
    __close_file__(in_file)

    return hosts_list


# Return the list of switches
def get_switches():
    filename = "Switch.txt"

    # Open file
    in_file = __open_file__(filename)

    switches_list = []

    # Read all lines
    for line in in_file:
        content = re.split("[<> ,]+", line)

        # Recupero le informazioni
        dpid_switch = content[1].split("=")[1]
        ports = __set_ports__([], content[2:len(content) - 1])

        switches_list.append(Switch(dpid_switch, ports))

    # Close file
    __close_file__(in_file)

    return switches_list


# Retrieving information about the switch ports
def __set_ports__(ports_list, line):
    if "Port" in line[0]:

        # Recupero le informazioni
        dpid = line[1].split("=")[1]
        port_no = line[2].split("=")[1]
        status = line[3]

        # Aggiorno la lista delle porte
        ports_list.append(Port(dpid, port_no, status))

        # Controllo se ci sono altre porte da settare
        if len(line) > 4:
            __set_ports__(ports_list, line[4: len(line)])

    return ports_list


if __name__ == "__main__":
    # Recupera la lista di host
    hosts_list = get_hosts()

    # Recupera la lista degli switches
    switches_list = get_switches()
