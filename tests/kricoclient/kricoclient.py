'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

import httplib
import json
import socket


class KricoClient(object):
    
    def __init__(self, server='krico-api', port=5000, api_version='v0.2'):
        
        print 'Resolving host name: ' + server
        print socket.gethostbyname(server)
        
        print 'Establishing connection to KRICO API: ' + server + ':' + str(port)
        self.http_connection = httplib.HTTPConnection(server + ':' + str(port))
        self.krico_http_header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.api_ver = api_version
        
    def launch_instance(self, parameters):
        self.last_response = self.send_data('/krico/' + self.api_ver + '/launch', parameters)
        self.check_response(self.last_response)
        
    def classify_instance(self, parameters):
        self.last_response = self.send_data('/krico/' + self.api_ver + '/classify', parameters)
        self.check_response(self.last_response)
        
    def predict_load(self, parameters):
        self.last_response = self.send_data('/krico/' + self.api_ver + '/predict-load', parameters)
        self.check_response(self.last_response)
        
    def refresh_classifier(self):
        self.last_response = self.send_data('/krico/' + self.api_ver + '/refresh-classifier', '')
        self.check_response(self.last_response)

    def refresh_predictor(self):
        self.last_response = self.send_data('/krico/' + self.api_ver + '/refresh-predictor', '')
        self.check_response(self.last_response)

    def refresh_instances(self):
        self.last_response = self.send_data('/krico/' + self.api_ver + '/refresh-instances', '')
        self.check_response(self.last_response)
    
    def get_last_response_entry(self, key_name):
        try:
            print 'Searching for key = ' + key_name + ' in last response received by KRICO client...'
            return self.last_response[key_name]
        except KeyError:
            print 'Key not found, iterating through nested structures...'
            
            for i in self.last_response.keys():
                if isinstance(i, dict):
                    value = self.last_response[i].get(key_name)
                    if value is not None:
                        print 'Key ' + key_name + ' found. Value = ' + value
                        return value
            
            print 'Nothing interesting found in server\'s response.'
            return None
        
    def check_response(self, response):
        
        if 'error' in response:
            print 'Error received from server: ' + response['error']
            return -1
        
        print 'No error received from server'
        return 0
    
    def send_data(self, request_uri, parameters):
        print 'Sending POST request to ' + request_uri
        print 'Request details: '
        print 'HTTP header:'
        print json.dumps(self.krico_http_header,sort_keys=True, indent=4, separators=(',', ': '))
        print 'parameters:'
        print parameters
        
        self.http_connection.request('POST', request_uri, parameters, self.krico_http_header)
        
        server_response = self.http_connection.getresponse().read()
        response_json = None
        
        try:
            print 'Parsing server response as JSON structure...'
            response_json = json.loads(server_response)
        except ValueError as ex:
            print 'Exception caught: ' + str(ex)
            print 'Server response that could not be parsed by JSON: ' + server_response
            response_json = server_response
            
        print 'Response received from server: '
        print json.dumps(response_json,sort_keys=True, indent=4, separators=(',', ': '))
        return response_json
