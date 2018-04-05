'''
Created on Mar 11, 2016

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
os.environ['krico_img_name'] = 'wrkld-streaming-darwin'
os.environ['krico_generate_csv'] = 'True'
os.environ['krico_sleep_update_monitors_s'] = '18000'

#user parameters:
clients = list(numpy.arange(10, 200, 20))
qualities = ['longhi']

for no_clients, quality in itertools.product(clients, qualities):
    
    os.environ['krico_streaming_darwin_clients'] = str(no_clients)
    os.environ['krico_streaming_darwin_quality'] = quality

    subprocess.call("python smoketest.py", shell=True)
