import urllib2
import json

__author__ = "telcolab"

base_url = "http://localhost:8080"


def get_flow_stats(dpid_switch):
    url_get_flow_stats = "/stats/flow/"
    url = base_url + url_get_flow_stats + str(dpid_switch)

    return json.loads(urllib2.urlopen(url=url).read())


def get_group_stats(dpid_switch):
    url_get_group_stats = "/stats/groupdesc/"
    url = base_url + url_get_group_stats + str(dpid_switch)

    return json.loads(urllib2.urlopen(url=url).read())


def get_multicast_ids(dpid_switch):
    group_stats = get_group_stats(dpid_switch)

    multicast_ids_list = []
    if group_stats[dpid_switch]: # Questa istruzione verifica se la lista NON e' vuota
        for group_entry in group_stats[dpid_switch]:
            multicast_ids_list.append(str(group_entry["group_id"]))

    return multicast_ids_list


def clean_flow_stats(dpid_switch):
    url_clean_switch = "/stats/flowentry/delete"

    url = base_url + url_clean_switch

    json_root = {"dpid": int(dpid_switch)}
    json_data = json.dumps(json_root, sort_keys=False, indent=4, separators=(",", ": "))

    urllib2.urlopen(url=url, data=json_data).read()

    print "Cancellate tutte flow entries dello switch:", dpid_switch


def clean_group_stats(dpid_switch):
    url_clean_switch = "/stats/groupentry/delete"

    url = base_url + url_clean_switch

    group_stats = get_group_stats(dpid_switch)

    for rule in group_stats[dpid_switch]:
        json_root = {"dpid": int(dpid_switch), "group_id": rule["group_id"]}
        json_data = json.dumps(json_root, sort_keys=False, indent=4, separators=(",", ": "))

        urllib2.urlopen(url=url, data=json_data).read()

        print "Cancellata group entry con id", rule["group_id"], "dallo switch", dpid_switch


def remove_unused_multicast_id_stats(dpid_switch, multicast_id):
    url_clean_switch = "/stats/groupentry/delete"

    url = base_url + url_clean_switch

    json_root = {"dpid": int(dpid_switch), "group_id": multicast_id}
    json_data = json.dumps(json_root, sort_keys=False, indent=4, separators=(",", ": "))

    urllib2.urlopen(url=url, data=json_data).read()

    print "Cancellata group entry inutilizzata con id", multicast_id, "dallo switch", dpid_switch


    url_clean_switch = "/stats/flowentry/delete"

    url = base_url + url_clean_switch

    json_root = {"dpid": int(dpid_switch)}
    actions = []
    action_dictionary = {"type": "GROUP", "group_id": int(multicast_id)}
    actions.append(action_dictionary)
    json_root["actions"] = actions
    json_data = json.dumps(json_root, sort_keys=False, indent=4, separators=(",", ": "))

    urllib2.urlopen(url=url, data=json_data).read()

    print "Cancellata flow entry inutilizzata con id", multicast_id, "dallo switch", dpid_switch


def __group_entry_api_call(api, dpid, multicast_id, list_output_ports):
    # Creazione e invio via POST della group entry
    url_add_entry = "/stats/groupentry/" + api
    url = base_url + url_add_entry

    json_root = {"dpid": int(dpid), "type": "ALL", "group_id": int(multicast_id)}
    buckets = []

    for port in list_output_ports:
        buckets_dict = {}
        actions_list = []
        actions_dict = {"type": "OUTPUT", "port": int(port)}
        actions_list.append(actions_dict)
        buckets_dict["actions"] = actions_list
        buckets.append(buckets_dict)

    json_root["buckets"] = buckets
    json_data = json.dumps(json_root, sort_keys=False, indent=4, separators=(",", ": "))

    if api == "add":
        print "GROUP ENTRY CREATA: \n" + json_data
    else:
        print "GROUP ENTRY MODIFICATA: \n" + json_data

    # Invio via post della group entry
    urllib2.urlopen(url=url, data=json_data).read()


def add_group_entry(dpid, multicast_id, list_output_ports):
    __group_entry_api_call("add", dpid, multicast_id, list_output_ports)


def modify_group_entry(dpid, multicast_id, list_output_ports):
    __group_entry_api_call("modify", dpid, multicast_id, list_output_ports)


def add_flow_entry(dpid, source_mac_address, multicast_id):
    # Creazione e invio via POST della flow entry (in caso gia' presente la sovrascrive)
    url_add_entry = "/stats/flowentry/add"
    url = base_url + url_add_entry
    json_root = {"dpid": int(dpid)}
    match = {"eth_src": source_mac_address}
    json_root["match"] = match
    actions = []
    action_dictionary = {"type": "GROUP", "group_id": int(multicast_id)}
    actions.append(action_dictionary)

    json_root["actions"] = actions
    json_data = json.dumps(json_root, sort_keys=False, indent=4, separators=(",", ": "))
    print "FLOW ENTRY: \n" + json_data
    # Invio via POST della flow entry
    urllib2.urlopen(url=url, data=json_data).read()

#TODO Implementare rimozione group id non piu' usati
def install_rule(dpid, source_mac_address, multicast_id, list_output_ports):
    group_stats = get_group_stats(dpid)
    print group_stats

    print "Switch", dpid, "GROUP PRIMA:\n", json.dumps(group_stats, sort_keys=False, indent=4, separators=(",", ": "))
    # Se e' la prima configurazione dello switch, aggiungi, altrimenti modifica la regola gia' presente
    if not group_stats[dpid]:  # Questa istruzione verifica se la lista e' vuota
        # Inserimento group entry
        add_group_entry(dpid, multicast_id, list_output_ports)
    else:
        print "a"
        print group_stats[str(dpid)]
        groups_in_switch = []
        for group_stat in group_stats[str(dpid)]:
            print "b", group_stat["group_id"]
            groups_in_switch.append(group_stat["group_id"])
        if not groups_in_switch.__contains__(int(multicast_id)):
            print "c"
            # Inserimento group entry
            add_group_entry(dpid, multicast_id, list_output_ports)
        else:
            print "d"
            # Modifica group entry (l'inserimento non avrebbe sovrascritto corretamente)
            modify_group_entry(dpid, multicast_id, list_output_ports)

    # Inserimento flow entry
    add_flow_entry(dpid, source_mac_address, multicast_id)

    group_stats = get_group_stats(dpid)
    print "Switch", dpid, "GROUP DOPO:\n", json.dumps(group_stats, sort_keys=False, indent=4, separators=(",", ": "))
