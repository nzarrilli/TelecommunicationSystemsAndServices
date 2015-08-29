__author__ = 'telcolab'
import urllib2
import json

# dictionary = {}
# dictionary['chiave'] = 'valore'
# dictionary['chiave2'] = 'valore2'
# subdictionary = {}
# subdictionary['subchiave'] = 'subvalore'
# subdictionary['subchiave2'] = 'subvalore2'
# dictionary['chiaveComposta'] = subdictionary
# list = []
# listdictionary = {}
# listdictionary['elemento1'] = "elemento11"
# listdictionary['elemento2'] = "elemento12"
# listdictionary2 = {}
# listdictionary2['elemento1'] = "elemento21"
# listdictionary2['elemento2'] = "elemento22"
# list.append(listdictionary)
# list.append(listdictionary2)
# dictionary['chiaveList'] = list
# json_data = json.dumps(dictionary, sort_keys=True, indent=4, separators=(',', ': '))
#
# data=json.loads(json_data)
# print data['chiave']
# print data['chiave2']
# datiComposti= data['chiaveComposta']
# print datiComposti['subchiave']
# print datiComposti['subchiave2']
# for item in data['chiaveList']:
#     print item['elemento1']
#     print item['elemento2']

def install_rule(dpid, mac_sensore, multicast_ID, listOutputPorts):
    baseurl = 'localhost:8080'
    url_add_entry = '/stats/flowentry/add'
    url = baseurl + url_add_entry
    json_root = {}
    json_root['dpid'] = dpid
    match = {}
         # TODO aggiungere il match
    json_root['match'] = match
    actions = []
    actionDictionary = {}
        # TODO aggiungere le actions
    actions.append(actionDictionary)
    json_root['actions'] = actions
    json_data = json.dumps(json_root, sort_keys=True, indent=4, separators=(',', ': '))

    content = urllib2.urlopen(url=url, data=json_data).read()

    # TODO fare la stessa cosa con la group table