__author__ = 'pmatyjas'

import pymongo
import uuid
import datetime
import random


def insert_vm_stub(mongo_client):
    wrkld_type = raw_input("Provide workload type\n")
    params = {}
    load_predicted = {
                         "cpu::time": str(float(random.randint(0, 10))),
                         "network::io": str(float(random.randint(0, 10))),
                         "ram::used": str(float(random.randint(0, 10))),
                         "storage::io": str(float(random.randint(0, 10)))
                     },
    if str(wrkld_type) == "Unknown":
        cpu_time = raw_input("Provide cputime\n")
        ram_used = raw_input("Provide ram\n")
        network_io = raw_input("Provide network I/O\n")
        storage_io = raw_input("Provide Storage I/O\n")
        try:
            params['cpu::time'] = str(int(cpu_time))
            params['ram::used'] = str(int(ram_used))
            params['network::io'] = str(int(network_io))
            params['storage::io'] = str(int(storage_io))
        except Exception as ex:
            print "Invalid input " + str(ex)
    else:
        raise NotImplementedError
    vm_uuid = uuid.uuid4()
    now = datetime.datetime.now()
    vm_entry = {
        str(vm_uuid): {
            "category": "unknown",
            "flavor": {
                "disk": 80,
                "name": "krico.default",
                "ram": 61440,
                "vcpus": 2
            },
            "host": "node-45.domain.tld",
            "image": "wrkld-caching-redis",
            "load_predicted": load_predicted,
            "name": "AUTOMATED-IMAGE-NAME",
            "parameters": params,
            "start_time": str(now)
        }
    }
    mongo_client['service']['instances-alive'].insert_one(vm_entry)


client = pymongo.MongoClient('localhost', 27017)

try:
    insert_vm_stub(client)
except NotImplementedError as ex:
    print "Not yet implemented workload type: " + str(ex)
