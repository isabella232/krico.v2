'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

import os
import generic


class LaunchFile(generic.KricoFile):
    '''
    classdocs
    '''

    def __init__(self,
                 try_env=True,
                 workload_class='unknown',
                 image_name='use-default',
                 param1=4.0,
                 param2=16384.0,
                 param3=160.0,
                 param4=10.0):

        '''
        Constructor
        '''

        if try_env:
            try:
                WORKLOAD_CLASS = os.environ['krico_workload_class']
            except KeyError:
                WORKLOAD_CLASS = workload_class
            try:
                IMG_NAME = os.environ['krico_img_name']
            except KeyError:
                IMG_NAME = image_name
            try:
                PARAM1 = os.environ['krico_param1']
            except KeyError:
                PARAM1 = param1
            try:
                PARAM2 = os.environ['krico_param2']
            except KeyError:
                PARAM2 = param2
            try:
                PARAM3 = os.environ['krico_param3']
            except KeyError:
                PARAM3 = param3
            try:
                PARAM4 = os.environ['krico_param4']
            except KeyError:
                PARAM4 = param4

        self.update_workload_params(WORKLOAD_CLASS, IMG_NAME, PARAM1, PARAM2, PARAM3, PARAM4)

    def generate_json(self):

        try:
            env_var_name = 'AUTOMATION_NAME'
            print 'Retrieving os env variable ' + env_var_name
            AUTOMATION_NAME = os.environ[env_var_name]
        except Exception as ex:
            print 'Exception caught, type Exception, value: '
            print ex
            AUTOMATION_NAME = 'AUTOMATED-IMAGE-NAME'

        KEYPAIR_NAME = None

        try:
            env_var_name = 'krico_openstack_keypair'
            print 'Retrieving os env variable ' + env_var_name
            KEYPAIR_NAME = os.environ[env_var_name]
        except Exception as ex:
            print 'Exception caught, type Exception, value: '
            print ex

        if KEYPAIR_NAME is None:
            print 'Could not determine keypair name for OpenStack nova. Aborting.'
            return

        self.dict_output_file = {
            "image": self.str_image_name,
            "name": AUTOMATION_NAME,
            "host_aggregate": "krico-cpu-48-10-ram-64-40-disk-1800-400",  #TODO: needs to be changed
            "network": "net04",
            "floating_ip_network": "net04_ext",
            "key_pair": KEYPAIR_NAME,
            "user": "admin",
            "password": "admin",
            "project": "admin",
            "category": self.str_workload_class,
            "parameters": self.dict_workload_params}
