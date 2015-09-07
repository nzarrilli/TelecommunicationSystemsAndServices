from File import ReadFile
from Model.NetworkModel import NetworkModel
from Network import RyuRuleCreator

__author__ = 'telcolab'

if __name__ == "__main__":

    # 1 Ottengo il dizionario degli switches
    switches = ReadFile.get_switches()

    # 2 Associo gli host ai vari switches
    switches = ReadFile.get_hosts(switches)

    # 3 Aggiorno il dizionario della rete aggiornando il collegamento tra i vari switches
    switches = ReadFile.add_links(switches)

    # 4 Aggiorno il dizionario degli switches impostando per ognuno la property "primoHopDict"
    network_model = ReadFile.add_paths(switches)

    # Stampo a video il risultato
    for key in switches:
        print "Dpid switch:", key
        if switches[key].path is not None:
            print "Paths:", switches[key].path
        for key_port in switches[key].ports:
            print ""
            print "Key port:", key_port
            print "Port number:", switches[key].ports[key_port].port_no
            print "Status:", switches[key].ports[key_port].status
            if switches[key].ports[key_port].host is not None:
                print "MAC address host:", switches[key].ports[key_port].host.mac_address
            if switches[key].ports[key_port].switch is not None:
                print "Dpid destination switch:", switches[key].ports[key_port].switch.dpid

        print "----------------------------------------------------------------------"

    # 5 Ottengo il dizionario dei sorgenti
    sources = ReadFile.get_sources()

    for key in sources:
        print "Source:", sources[key].mac_address
        print "Multicast id:", sources[key].multicast_id
        print "Destination list:", sources[key].mac_destination_list
        print "----------------------------------------------------------------------"

    # 6 Creo il nuovo modello della rete
    network_model = NetworkModel(switches, sources)

    # 7 Algoritmo installazione regole ryu

    # Lista degli switch nei percorsi
    path_switch_list = []

    for source in network_model.sources:
        switch = ReadFile.get_switch(network_model.switches, source)
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
            destination_port_dict = ReadFile.install_rules_ryu(destination_mac_address, switch, network_model, destination_port_dict)

            print ""

        for destination_key in destination_port_dict:
            print "DPID:", destination_key
            print "Lista di porte da configurare:", destination_port_dict[destination_key]
            RyuRuleCreator.install_rule(destination_key, source, network_model.sources[source].multicast_id,
                                        destination_port_dict[destination_key])
            if not path_switch_list.__contains__(destination_key):
                path_switch_list.append(destination_key)

    for switch in network_model.switches:
        if not path_switch_list.__contains__(switch):
            RyuRuleCreator.clean_group_stats(switch)
            RyuRuleCreator.clean_flow_stats(switch)
