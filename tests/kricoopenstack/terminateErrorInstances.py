'''
Created on Jun 27, 2016

@author: lfiliks-dev
'''

import osclient

openstack_client = osclient.KricoOpenstackClient()

openstack_client.terminate_error_state_instances()
