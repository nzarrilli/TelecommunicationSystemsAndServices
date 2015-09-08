from File import ReadFile
from Model.NetworkModel import NetworkModel
from Network import RyuRuleCreator

__author__ = 'telcolab'

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

    # # 7 Clean switch rules
    # for key_dpid_switch in network_model.network:
    #     RyuRuleCreator.clean_flow_stats(key_dpid_switch)
    #     RyuRuleCreator.clean_group_stats(key_dpid_switch)

    # 8 Algoritmo installazione regole ryu


    path_switch_list = [] # Lista switch coinvolti in qualche percorso
    switch_multicast_ids_dict = {} # chiave: dpid, valore:lista multicast_id installati dall'algoritmo sullo switch

    for source in network_model.sources:
        switch = ReadFile.__get_switch__(network_model.switches, source)
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
            destination_port_dict = ReadFile.install_rules_ryu(destination_mac_address, switch, network_model,
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
                # Se m_id non e' presente nella lista di m_ids impostati dall'algoritmo cancello le entries ormai obsolete
                if not switch_multicast_ids_dict[switch].__contains__(m_id):
                    RyuRuleCreator.remove_unused_multicast_id_stats(switch, m_id)
