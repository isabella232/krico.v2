'''
Created on Mar 10, 2016

@author: lfiliks-dev
'''

import subprocess
import os

os.environ['krico_openstack_keypair'] = 'krico-03-keypair'
os.environ['krico_openstack_keypair_file'] = '/home/ubuntu/ssh-keys/'+os.environ['krico_openstack_keypair']+'.pem'

#os.environ['krico_workload_class'] = 'streaming'
#os.environ['krico_img_name'] = 'wrkld_streaming'
#os.environ['krico_param1'] = '10'
#os.environ['krico_param2'] = '100'
#os.environ['krico_param3'] = '2048'
#os.environ['krico_param4'] = '0'

subprocess.call("python smoketest.py", shell=True)
