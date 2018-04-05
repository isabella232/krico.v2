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
os.environ['krico_img_name'] = 'wrkld-caching-redis'
os.environ['krico_generate_csv'] = 'True'
os.environ['krico_sleep_update_monitors_s'] = '300'

#user parameters:
clients = list(numpy.arange(200, 1000, 200))
ratios = ['0:10', '2:10', '4:10', '6:10', '8:10', '10:10']
test_time = 6000

for ratio, no_clients in itertools.product(ratios, clients):
           
    os.environ['krico_caching_redis_clients'] = str(no_clients)
    os.environ['krico_caching_redis_ratio'] = str(ratio)
    os.environ['krico_caching_redis_test_time'] = str(test_time)

    subprocess.call("python smoketest.py", shell=True)
