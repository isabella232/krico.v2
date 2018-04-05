'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

import json


class KricoFile(object):
    
    def __init__(self, 
                 workload_class='unknown', 
                 image_name='use-default', 
                 param1='', 
                 param2='', 
                 param3='', 
                 param4=''):
        
        '''
        Constructor
        '''
        
    def get_json(self):
        print 'Generating KRICO JSON file ...'
        self.generate_json()
        output_json = json.dumps(self.dict_output_file, sort_keys=True, indent=4, separators=(',',': '))
        print 'Generated file: '
        print output_json
        return output_json
    
    def get_dict(self):
        print 'Generating KRICO JSON file ...'
        self.generate_json()
        print 'Generated DICT:'
        print self.dict_output_file
        return self.dict_output_file
    
    def update_workload_params(self, workload_class, image_name, param1, param2, param3, param4):
    
        print 'Updating KRICO JSON workload parameters: '
        print 'workload_class = ' + workload_class
        print 'img_name = ' + image_name
        print 'param1 = ' + str(param1)
        print 'param2 = ' + str(param2)
        print 'param3 = ' + str(param3)
        print 'param4 = ' + str(param4)
    
        if workload_class == 'unknown':
        
            self.dict_workload_params = {
                  "vcpus": param1,
                  "ram": param2,
                  "disk": param3
            }
            
            self.str_image_name = "wrkld-streaming"
            
        elif workload_class == 'streaming':
          
            self.dict_workload_params = {
                "clients": param1,
                "bitrate": param2,
                "disk": param3
            }
            
            self.str_image_name = "wrkld-streaming"
            
        elif workload_class == 'science':
          
            self.dict_workload_params = {
                "processors": param1,
                "memory": param2,
                "disk": param3
            }
            
            self.str_image_name = "wrkld-science-hpcg"
            
        elif workload_class == 'oltp':
          
            self.dict_workload_params = {
                "clients": param1,
                "data": param2,
                "disk": param3
            }
            
            self.str_image_name = "wrkld-oltp"
            
        elif workload_class == 'caching':
          
            self.dict_workload_params = {
                "clients": param1,
                "ratio": param2,
                "memory": param3,
                "disk": param4
            }
            
            self.str_image_name = "wrkld-caching"
            
        elif workload_class == 'webserving':
          
            self.dict_workload_params = {
                "clients": float(param1),
                "disk": float(param2)
            }
            
            self.str_image_name = "wrkld-webserving"
            
        elif workload_class == 'bigdata':
          
            self.dict_workload_params = {
                "data": param1,
                "processors": param2,
                "memory": param3,
                "disk": param4
            }
            
            self.str_image_name = "wrkld-bigdata"
    
        if image_name != 'use-default':
            self.str_image_name = image_name
            
        self.str_workload_class = workload_class
        
    def generate_json(self):
        
        self.dict_output_file = {"error": "no overloaded method found"}
