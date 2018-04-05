'''
Created on May 12, 2016

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
os.environ['krico_img_name'] = 'wrkld-webserving-apache'
os.environ['krico_generate_csv'] = 'True'
os.environ['krico_sleep_update_monitors_s'] = '600'

#user parameters:
main_page_iterations = ['1']
search_iterations = ['1']
comment_iterations = ['1']
            
for main_page_iteration, search_iteration, comment_iteration  in itertools.product(main_page_iterations, search_iterations, comment_iterations):
    
    os.environ['krico_webserving_num_slave_nodes'] = '2'
    os.environ['krico_webserving_clients_count'] = '128'
    os.environ['krico_webserving_main_page_iterations'] = str(main_page_iteration)
    os.environ['krico_webserving_search_iterations'] = str(search_iteration)
    os.environ['krico_webserving_comment_iterations'] = str(comment_iteration)

    subprocess.call("python smoketest.py", shell=True)
