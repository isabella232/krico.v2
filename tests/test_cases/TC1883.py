'''
Created on Apr 29, 2016

@author: lfiliks-dev
'''

import subprocess
import os
import numpy
import itertools

#OpenStack access parameters
os.environ['krico_openstack_keypair'] = 'krico-03-keypair'
os.environ['krico_openstack_keypair_file'] = '/home/ubuntu/ssh-keys/'+os.environ['krico_openstack_keypair']+'.pem'

#KRICO instructions on how to run the workload
os.environ['krico_workload_class'] = 'unknown'
os.environ['krico_img_name'] = 'wrkld-oltp-ycsb'
os.environ['krico_generate_csv'] = 'True'
os.environ['krico_sleep_update_monitors_s'] = '900'

#user parameters:
clients = list(numpy.arange(500, 2000, 300))
data_list = list(numpy.arange(10, 100, 30))

for no_clients, data in itertools.product(clients, data_list):
    
    os.environ['krico_oltp_clients'] = str(no_clients)
    os.environ['krico_oltp_data'] = str(data)

    subprocess.call("python smoketest.py", shell=True)
