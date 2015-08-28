__author__ = 'telcolab'
import json

dictionary = {}
dictionary['chiave'] = 'valore'
dictionary['chiave2'] = 'valore2'
subdictionary = {}
subdictionary['subchiave'] = 'subchiave'
subdictionary['subchiave2'] = 'subchiave2'
dictionary['chiaveComposta'] = subdictionary
list = []
listdictionary = {}
listdictionary['elemento1'] = "elemento11"
listdictionary['elemento2'] = "elemento12"
listdictionary2 = {}
listdictionary2['elemento1'] = "elemento21"
listdictionary2['elemento2'] = "elemento22"
list.append(listdictionary)
list.append(listdictionary2)
dictionary['chiaveList'] = list
json_data = json.dumps(dictionary, sort_keys=True, indent=4, separators=(',', ': '));
print json_data

