__author__ = 'telcolab'
import urllib2
import json

def getFlowStats(switchDpid):
    baseurl = "localhost:8080"
    url_get_flow_stats = '/stats/flow/' + switchDpid
    url = baseurl + url_get_flow_stats
    return urllib2.urlopen(url=url).read()

def install_rule(dpid, mac_sensore, multicast_ID, listOutputPorts):
    baseurl = 'localhost:8080'

    # creazione e invio via POST della group entry
    url_add_entry = '/stats/groupentry/add'
    url = baseurl + url_add_entry
    json_root = {}
    json_root['dpid'] = dpid # TODO controllare se nel dpid vanno aggiunti gli 0 davanti
    json_root['group_id'] = multicast_ID
    buckets = []
    bucketsDict = {}
    actionsList = []
    for port in listOutputPorts:
        actionsDict = {}
        actionsDict['type'] = "OUTPUT"
        actionsDict['port'] = port
        actionsList.append(actionsDict)
    bucketsDict['actions'] = actionsList
    buckets.append(bucketsDict)
    json_root['buckets'] = buckets

    json_data = json.dumps(json_root,sort_keys=False, indent=4, separators=(',', ': '))
    print "GROUP ENTRY CREATA: \n" + json_data
#  TODO  content = urllib2.urlopen(url=url, data=json_data).read()

    # creazione e invio via POST della flow entry
    url_add_entry = '/stats/flowentry/add'
    url = baseurl + url_add_entry
    json_root = {}
    json_root['dpid'] = dpid
    match = {}
    match['eth_src'] = mac_sensore
    json_root['match'] = match
    actions = []
    actionDictionary = {}
    actionDictionary['type'] = "GROUP"
    actionDictionary['group_id'] = multicast_ID
    actions.append(actionDictionary)
    json_root['actions'] = actions
    json_data = json.dumps(json_root,sort_keys=False, indent=4, separators=(',', ': '))
    print "FLOW ENTRY CREATA: \n" + json_data

    #  TODO content = urllib2.urlopen(url=url, data=json_data).read()


# TESTS

# print "Esecuzione di 'install_rule(1, '20:40:8f:boh:prova:LOL', 2, [3,4])'"
# install_rule(1, '20:40:8f:boh:prova:LOL', 2, [3,4])
print getFlowStats(1)
