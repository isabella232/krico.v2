'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

from filegenerators import kricocsv
from pymongo import MongoClient
import numpy
import socket
import json
import time


class KricoMongoClient(object):
    
    def __init__(self, server='krico-database', port=27017):
        
        print 'Resolving host name: ' + server
        print socket.gethostbyname(server)
        
        print 'Creating connection to mongoDB @ ' + server + ':' + str(port)
        self.mongo_client = MongoClient(server, port)
        self.mongo_service_db = self.mongo_client['service']
        self.mongo_monitor_db = self.mongo_client['monitor']

    def _compute_load(self, monitor_samples):
        metrics_names = kricocsv.DEFAULT_LOAD_MEASURED_HEADER
        metrics_raw = {}
        
        for sample in monitor_samples:
            for metric in metrics_names:
                if not metric in metrics_raw.keys():
                    metrics_raw[metric] = []
                metrics_raw[metric].append(sample['metrics'][metric])
               
        metrics_filtered = self._filter_peaks(metrics_raw)
       
        metrics = {
            metric: float(numpy.mean(metrics_filtered[metric]))
            for metric in metrics_names
            }

        return metrics

    def _filter_peaks(self, metrics):
        threshold = 3.0

        metrics_filtered = {}

        for metric, metric_samples in metrics.items():
            threshold_low = numpy.percentile(metric_samples, 3) / threshold
            threshold_high = numpy.percentile(metric_samples, 97) * threshold

            metrics_filtered[metric] = filter(lambda value: threshold_low <= value <= threshold_high, metric_samples)

        return metrics_filtered
    
    def get_db_data(self, collection, query, all, max_tries=1, sleep_time_s=30):
        self.last_response = None
        
        for i in range(0, max_tries):
            print 'Sending request to mongoDB...'
            if all:
                self.last_response = collection.find(query)
            else:
                self.last_response = collection.find_one(query)
        
            if self.last_response == None:
                
                if i == max_tries-1:
                    print 'mongoDB get_db_data - max tries reached, leaving with None...'
                    return self.last_response
                
                print 'Could not get data from mongoDB, sleeping and trying one more time... (step ' + str(i+1) + \
                      '/'+str(max_tries) + ' , sleep ' + str(sleep_time_s) + 's)'
                      
                time.sleep(sleep_time_s)
                continue
            else:
                print 'Record found'
                break
        return self.last_response

    def format_response(self, response):
        print 'Formatting response to JSON convertible dict'
        try:
            print 'Exception caught on serializing JSON object. Details: ' + str(ex)
            print 'Replacing known non-JSONable objects with their string representation...'
            print 'BEFORE:'
            print response

            convert_to_str = ['_id', 'start_time', 'stop_time', 'timestamp']

            for key in convert_to_str:
                if key in response.keys():
                    response[key] = str(response[key])
        
            print 'AFTER:'
            print response

            print json.dumps(response,sort_keys=True, indent=4, separators=(',',': '))
            
        except Exception as ex:
            print 'Another exception found while parsing response from mongoDB, giving up...'
            print ex
        return response

    def remove_db_data(self, collection, query):
        self.last_response = self.get_db_data(collection, query, False)

        if self.last_response == None:
            print 'No desired record found in MongoDB! Aborting.'
            return -1
    
        print 'Sending remove request to mongoDB...'
        dict_mongo_reply = collection.remove(query)

        print 'Removal reply message: '
        print json.dumps(dict_mongo_reply,sort_keys=True, indent=4, separators=(',',': '))

        #expected reply {u'ok': 1, u'n': 0}

        if dict_mongo_reply["ok"] == 1:
            print "Removed 1 record from DB. All OK."
        else:
            print "Removed " + dict_mongo_reply["ok"] + " entries from mongoDB, which is WRONG. Aborting."
            return -1
        
        return 0
        
    def get_service_entry(self, instance_id, max_tries=1, sleep_time_s=30):
        print "Getting service entry from mongoDB (get_service_entry)... instance_id = " + instance_id
        return self.get_db_data(self.mongo_service_db.instances, {"instance_id": instance_id}, False, max_tries, sleep_time_s)
    
    def get_service_entries(self, category='unknown'):
        print "Getting service entries from mongoDB (get_service_entries)..."
        return self.get_db_data(self.mongo_service_db.instances, {"category": category}, True)

    def get_load_measured(self, instance_id, max_tries=1, sleep_time_s=30):
        print "Getting measured load entries from mongoDB (get_load_measured)... instance_id = " + instance_id
        samples = self.get_db_data(self.mongo_monitor_db.samples, {"instance_id": instance_id}, True, max_tries, sleep_time_s)
        return self._compute_load(samples)
    
    def remove_service_entry(self, instance_id):
        print 'Removing service entries with instance_id = ' + instance_id
        self.remove_db_data(self.mongo_service_db.instances, {"instance_id": instance_id})

    def remove_monitor_entry(self, instance_id):
        print 'Removing monitor entries with instance_id = ' + instance_id
        self.remove_db_data(self.mongo_monitor_db.samples, {"instance_id": instance_id})
    
    def validate_entry(self, validation_dict):
        '''
        Input arguments as a key=value pairs must exist in last entry from mongoDB
        '''

        for key_name in validation_dict.keys():
            try:
                print 'Searching for key = ' + key_name + ' in last response received by KRICO client...'
                if self.last_response[key_name] == validation_dict[key_name]:
                    print 'Key ' + key_name + ' found. Value = ' + str(validation_dict[key_name])
                    continue
        
            except KeyError:
                print 'Key not found, iterating through nested structures...'
            
                for i in self.last_response.keys():
                    value = self.last_response[i].get(key_name)
                    if value != None:
                        print 'Key ' + key_name + ' found. Value = ' + value
                        if value == validation_dict[key_name]:
                            continue
                        else:
                            print 'Values do not match! Value in DB = ' + value +\
                                  ', value in validation_dict = ' + validation_dict[key_name]
                                  
                            return -1
                        
            print 'Key ' + key_name + ' not found in mongoDB entry. Aborting.'
            return -1
        
        print 'All keys found. All values match.'
        return 0
