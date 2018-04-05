'''
Created on May 12, 2016

@author: lfiliks-dev
'''

import sys
import client

wrkld_category='unknown'

if len(sys.argv) >= 1:
    wrkld_category=sys.argv[1]

mongo_client = client.KricoMongoClient()
entries = mongo_client.get_analysis_entries(category=wrkld_category)

list_user_params_science = ["processors", "memory"]
list_user_params_streaming = ["length", "clients", "bitrate"]
list_user_params_oltp = ["clients", "data"]
list_user_params_bigdata = ["data", "processors", "memory"]
list_user_params_webserving = ["clients"]
list_user_params_caching = ["instances", "clients", "ratio", "memory"]
list_user_params_unknown = ["cpu::time", "ram::used", "storage::io", "network::io"]

map_workloads={"science":list_user_params_science,
               "streaming":list_user_params_streaming,
               "oltp":list_user_params_oltp,
               "bigdata":list_user_params_bigdata,
               "webserving":list_user_params_webserving,
               "caching":list_user_params_caching,
               "unknown":list_user_params_unknown}

user_params_keys = map_workloads[wrkld_category]

pattern_prefix="%-10s%-30s"
pattern_suffix="%-20s%-20s%-20s%-20s%-20s"

print pattern_prefix % (
                 'category',
                 'image'),

for user_params_key in user_params_keys:
    print "%-10s" % (user_params_key),
        
print pattern_suffix % ('cpu:time',
                 'ram:used',
                 'network:pkts:send',
                 'storage:ops:read',
                 'storage:ops:write')
        
for entry in entries:
    
    print pattern_prefix % (entry['category'], entry['image']),
    
    for user_params_key in user_params_keys:
        try:
            print "%-10s" % (entry['parameters'][user_params_key]),
        except KeyError:
            print "%-10s" % ("?"),
        
    print pattern_suffix % (
                     str(entry['load_measured']['cpu:time']),
                     str(entry['load_measured']['ram:used']),
                     str(entry['load_measured']['network:packets:send']),
                     str(entry['load_measured']['storage:operations:read']),
                     str(entry['load_measured']['storage:operations:write']))
