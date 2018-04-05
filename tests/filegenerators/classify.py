'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

import generic

class ClassifyFile(generic.KricoFile):
    
    '''
    classdocs
    '''

    def __init__(self, 
                 instance_id, 
                 workload_class='unknown', 
                 image_name='use-default', 
                 param1='', 
                 param2='', 
                 param3='', 
                 param4=''):
        
        '''
        Constructor
        '''
        self.str_instance_id = str(instance_id)
        
    def generate_json(self):

        self.dict_output_file = {
         "instance_id" : self.str_instance_id
         }
