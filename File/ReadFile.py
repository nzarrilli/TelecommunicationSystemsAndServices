__author__ = 'nzarrilli'

# Questo script legge il contenuto di un file .txt
# Guida: http://www.afterhoursprogramming.com/tutorial/Python/Reading-Files/

import os
import re

from Model.Host import Host


# Return the list of hosts
def get_host(root_path):
    try:
        filename = "Host.txt"

        # Open file
        in_file = open(os.path.join(root_path, filename), "r")

        host_list = []

        # Read all lines
        for line in in_file:
            mac_address = re.split("[= ]+", line)[2]
            port = re.split("[= ]+", line)[4]
            dpid = re.split("[= ]+", line)[6]

            host_list.append(Host(mac_address, port, dpid))

        # Close file
        in_file.close()

        return host_list

    except IOError, ex:
        print ex

    return None


if __name__ == "__main__":
    base_dir = os.getenv("HOME")
    ryu_dir = "ryu"
    app_dir = "app"

    # Creazione della path
    root_path = os.path.join(base_dir, ryu_dir, ryu_dir, app_dir)

    # Recupera la lista di host
    host_list = get_host(root_path)
