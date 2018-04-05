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
os.environ['krico_img_name'] = 'wrkld-science-hpcg'
os.environ['krico_generate_csv'] = 'True'
os.environ['krico_sleep_update_monitors_s'] = '900'

#user parameters:
processors = list(numpy.arange(4, 48, 12))
memory = list(numpy.arange(4, 62, 20))
threads = list(numpy.arange(1, 128, 20))
slaves = list(numpy.arange(1, 4, 1))

os.environ['krico_science_hpcg_duration'] = '900'

for proc, mem, thrd, slave in itertools.product(processors, memory, threads, slaves):
    
    #set env vars to conduct the test
    os.environ['krico_science_hpcg_memory'] = str(mem)
    os.environ['krico_science_hpcg_processors'] = str(proc)
    os.environ['krico_science_hpcg_threads'] = str(thrd)
    os.environ['krico_science_hpcg_slave_nodes'] = '4'
    
    #execute the process
    subprocess.call("python smoketest.py", shell=True)
