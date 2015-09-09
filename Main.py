from File import ReadFile
from Model.NetworkModel import NetworkModel
from Network import RyuRuleCreator

__author__ = 'telcolab'


# Funzione che aggiunge al dizionario la porta di collegamento tra lo switch sorgente e quello di destinazione
def __add_destination_port__(dest_port_dict, dpid_switch, port_no):
    if not dest_port_dict.keys().__contains__(dpid_switch):
        dest_port_dict[dpid_switch] = []

    if not dest_port_dict[dpid_switch].__contains__(port_no):
        dest_port_dict[dpid_switch].append(port_no)

    return dest_port_dict


def install_rules_ryu(dest_mac_address, current_switch, network_mod, dest_port_dict):
    # Recupero le informazioni sullo switch al quale e' collegato l'host di destinazione
    destination_switch = network_mod.get_switch(dest_mac_address)

    # Controlliamo che lo switch corrente non e' lo stesso di quello di destinazione
    if current_switch.dpid != destination_switch.dpid:

        # Recupero dpid dello switch successivo dalla lista dei paths
        next_switch_dpid = current_switch.path[destination_switch.dpid][1]

        # Recupero la porta di collegamento dello switch successivo
        destination_port = current_switch.get_switch_port(next_switch_dpid)

        # Aggiungo al dizionario la porta di collegamento tra lo switch corrente e lo switch successivo
        dest_port_dict = __add_destination_port__(dest_port_dict, current_switch.dpid, destination_port)

        print "Switch", current_switch.dpid, "--> Port", destination_port, "--> Switch", next_switch_dpid

        # Richiamo il metodo passandogli lo switch successivo
        install_rules_ryu(dest_mac_address, network_mod.switches[next_switch_dpid], network_mod,
                          dest_port_dict)

    else:  # Se siamo arrivati all'ultimo switch dobbiamo inoltrare il pacchetto sulla porta dell'host
        if destination_switch.ports[dest_mac_address].host is not None \
                and destination_switch.ports[dest_mac_address].host.mac_address == dest_mac_address:
            # Recupero la porta di collegamento tra l'host e lo switch
            destination_port = destination_switch.ports[dest_mac_address].port_no
            # Aggiungo al dizionario la porta di collegamento tra lo switch corrente e lo switch successivo
            dest_port_dict = __add_destination_port__(dest_port_dict, current_switch.dpid,
                                                      destination_port)

            print "Switch", current_switch.dpid, "--> Port", destination_port, "--> Host", dest_mac_address

    return dest_port_dict


if __name__ == "__main__":

    # 1 Ottengo il dizionario degli switches
    network = ReadFile.get_switches()

    # 2 Associo gli host ai vari switches
    network = ReadFile.get_hosts(network)

    # 3 Aggiorno il dizionario della rete aggiornando il collegamento tra i vari switches
    network = ReadFile.add_links(network)

    # 4 Aggiorno il dizionario degli switches impostando per ognuno la property "primoHopDict"
    network_model = ReadFile.add_paths(network)

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
    sources = ReadFile.get_sources()

    for key in sources:
        print "Source:", sources[key].mac_address
        print "Multicast id:", sources[key].multicast_id
        print "Destination list:", sources[key].mac_destination_list
        print "----------------------------------------------------------------------"

    # 6 Creo il nuovo modello della rete
    network_model = NetworkModel(network, sources)

    # 7 Algoritmo installazione regole ryu
    # Lista switch coinvolti in qualche percorso
    path_switch_list = []
    # chiave: dpid, valore:lista multicast_id installati dall'algoritmo sullo switch
    switch_multicast_ids_dict = {}

    for source in network_model.sources:
        switch = network_model.get_switch(source)
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
            destination_port_dict = install_rules_ryu(destination_mac_address, switch, network_model,
                                                      destination_port_dict)

            print ""

        for destination_key in destination_port_dict:
            print "DPID:", destination_key
            print "Lista di porte da configurare:", destination_port_dict[destination_key]
            RyuRuleCreator.install_rule(destination_key, source, network_model.sources[source].multicast_id,
                                        destination_port_dict[destination_key])
            # Aggiunta dello switch alla lista di switch sul quale il nostro algoritmo ha installato regole
            if not path_switch_list.__contains__(destination_key):
                path_switch_list.append(destination_key)

            # Aggiunta del multicast_id alla lista di quelli presenti sullo switch.
            if not switch_multicast_ids_dict.keys().__contains__(destination_key):
                switch_multicast_ids_dict[destination_key] = []
            switch_multicast_ids_dict[destination_key].append(network_model.sources[source].multicast_id)

    # Rimozione di tutte le regole precedentemente installate ed ora inutilizzate
    for switch in network_model.switches:
        if not path_switch_list.__contains__(switch):
            # Cancellazione di tutte le regole appartenenti a switch che non sono piu' sul percorso
            RyuRuleCreator.clean_group_stats(switch)
            RyuRuleCreator.clean_flow_stats(switch)
        else:
            multicast_ids = RyuRuleCreator.get_multicast_ids(switch)
            print "Switch", switch, "multicast_ids_API:", multicast_ids
            print "Switch", switch, "multicast_ids_installed:", switch_multicast_ids_dict[switch]
            for m_id in multicast_ids:
                # Se m_id non e' presente nella lista di m_ids impostati dall'algoritmo cancello le entries ormai
                # obsolete
                if not switch_multicast_ids_dict[switch].__contains__(m_id):
                    RyuRuleCreator.remove_unused_multicast_id_stats(switch, m_id)
