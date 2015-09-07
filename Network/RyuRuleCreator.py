__author__ = "telcolab"

import urllib2
import json

base_url = "http://localhost:8080"


def get_flow_stats(dpid_switch):
    url_get_flow_stats = "/stats/flow/"
    url = base_url + url_get_flow_stats + str(dpid_switch)

    return urllib2.urlopen(url=url).read()


def get_group_stats(dpid_switch):
    url_get_group_stats = "/stats/groupdesc/"
    url = base_url + url_get_group_stats + str(dpid_switch)

    return urllib2.urlopen(url=url).read()


def clean_flow_stats(dpid_switch):
    url_clean_switch = "/stats/flowentry/delete"

    url = base_url + url_clean_switch

    json_root = {"dpid": dpid_switch}
    json_data = json.dumps(json_root, sort_keys=False, indent=4, separators=(",", ": "))

    return urllib2.urlopen(url=url, data=json_data).read()


def clean_group_stats(dpid_switch):
    url_clean_switch = "/stats/groupentry/delete"

    url = base_url + url_clean_switch

    json_root = {"dpid": dpid_switch}
    json_data = json.dumps(json_root, sort_keys=False, indent=4, separators=(",", ": "))

    return urllib2.urlopen(url=url, data=json_data).read()


def install_rule(dpid, source_mac_address, multicast_id, list_output_ports):

    # Creazione e invio via POST della group entry
    url_add_entry = "/stats/groupentry/add"
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
    print "GROUP ENTRY CREATA: \n" + json_data
    # Invio via post della group entry
    urllib2.urlopen(url=url, data=json_data).read()

    # Creazione e invio via POST della flow entry
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
    print "FLOW ENTRY CREATA: \n" + json_data
    # Invio via POST della flow entry
    urllib2.urlopen(url=url, data=json_data).read()

# TESTS
#print "Esecuzione di install_rule(1, '20:40:8f:boh:prova:LOL', 2, [3,4])"
#install_rule(1, "20:40:8f:boh:prova:LOL", 2, [3, 4, 5, 6, 7])

# json_response = get_flow_stats(1)
# print json.dumps(json.loads(json_response), sort_keys=False, indent=4, separators=(",", ": "))

# json_response = get_group_stats(1)
# print json.dumps(json.loads(json_response), sort_keys=False, indent=4, separators=(",", ": "))
