'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

import generic


class PredictFile(generic.KricoFile):
    
    '''
    classdocs
    '''

    def __init__(self, 
                 workload_class='streaming', 
                 image_name='use-default', 
                 param1='10', 
                 param2='1000', 
                 param3='2048', 
                 param4=''):
        
        '''
        Constructor
        '''
        
        self.update_workload_params(workload_class, image_name, param1, param2, param3, param4)
    
    def generate_json(self):

        self.dict_output_file = {
         "image": self.str_image_name,
         "category": self.str_workload_class,
         "parameters": self.dict_workload_params
         }
