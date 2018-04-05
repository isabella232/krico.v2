'''
Created on Mar 10, 2016

@author: lfiliks-dev
'''

import subprocess
import os

#OpenStack access parameters
os.environ['krico_openstack_keypair'] = 'krico-03-keypair'
os.environ['krico_openstack_keypair_file'] = '/home/ubuntu/ssh-keys/'+os.environ['krico_openstack_keypair']+'.pem'

#KRICO instructions on how to run the workload
os.environ['krico_workload_class'] = 'unknown'
os.environ['krico_img_name'] = 'wrkld-caching-redis'
os.environ['krico_generate_csv'] = 'False'
os.environ['krico_sleep_update_monitors_s'] = '900'

#execute the process
subprocess.call("python smoketest.py", shell=True)
