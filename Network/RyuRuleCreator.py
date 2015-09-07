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
    url_add_entry = "/stats/groupentry/modify"
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
    url_add_entry = "/stats/flowentry/modify"
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
# get_flow_stats(4)

# RyuRuleCreator.get_flow_stats(6)
# '{"6": [{"actions": ["GROUP:1"], "idle_timeout": 0, "cookie": 0, "packet_count": 0, "hard_timeout": 0, "byte_count": 0, "length": 80, "duration_nsec": 968000000, "priority": 0, "duration_sec": 246, "table_id": 0, "flags": 0, "match": {"dl_src": "00:00:00:00:00:01"}}]}'
# >>> res = RyuRuleCreator.get_flow_stats(6)
# >>> obj_res = json.loads(res)
# Traceback (most recent call last):
#   File "<input>", line 1, in <module>
# NameError: name 'json' is not defined
# >>> import json
# >>> obj_res = json.loads(res)
# >>> obj_res
# {u'6': [{u'priority': 0, u'duration_sec': 268, u'hard_timeout': 0, u'byte_count': 0, u'length': 80, u'actions': [u'GROUP:1'], u'duration_nsec': 263000000, u'packet_count': 0, u'idle_timeout': 0, u'cookie': 0, u'flags': 0, u'table_id': 0, u'match': {u'dl_src': u'00:00:00:00:00:01'}}]}
# >>> obj_res.keys()
# [u'6']
# >>> obj_res[6]
# Traceback (most recent call last):
#   File "<input>", line 1, in <module>
# KeyError: 6
# >>> obj_res["6"]
# [{u'priority': 0, u'duration_sec': 268, u'hard_timeout': 0, u'byte_count': 0, u'length': 80, u'actions': [u'GROUP:1'], u'duration_nsec': 263000000, u'packet_count': 0, u'idle_timeout': 0, u'cookie': 0, u'flags': 0, u'table_id': 0, u'match': {u'dl_src': u'00:00:00:00:00:01'}}]
# >>> obj_res_6 = obj_res["6"]
# >>> obj_res_6[0].keys()
# [u'priority', u'duration_sec', u'hard_timeout', u'byte_count', u'length', u'actions', u'duration_nsec', u'packet_count', u'idle_timeout', u'cookie', u'flags', u'table_id', u'match']
# >>> obj_res_6[0]["actions"]
# [u'GROUP:1']
# >>> obj_res_6[0]["actions"][0]
# u'GROUP:1'
# >>> str(obj_res_6[0]["actions"][0])
# 'GROUP:1'
# >>> obj_res_6[0]["actions"][0].keys()
# Traceback (most recent call last):
#   File "<input>", line 1, in <module>
# AttributeError: 'unicode' object has no attribute 'keys'
# >>> obj_res_6[0]["actions"][0].values()
# Traceback (most recent call last):
#   File "<input>", line 1, in <module>
# AttributeError: 'unicode' object has no attribute 'values'
# >>> obj_res_6[0]["actions"][0][0]
# u'G'
# >>> str(obj_res_6[0]["actions"][0])
# 'GROUP:1'
# >>> import re
# >>> re.split("[:]+", str(obj_res_6[0]["actions"][0]))[1]
# '1'
