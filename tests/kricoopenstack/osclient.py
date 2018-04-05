'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

import keystoneclient.auth.identity.v3
import keystoneclient.session
import novaclient.client
import json


class KricoOpenstackClient(object):
    
    def __init__(self, 
                 auth_url="https://public.fuel.local:5000/v3",
                 username="admin", 
                 password="admin", 
                 project_name="admin", 
                 user_domain_name="default", 
                 project_domain_name="default"):
        
        print 'Creating OpenStack auth session with parameters: \n'
        print 'auth_url = ' + auth_url
        print 'username = ' + username
        print 'password = ' + password
        print 'project name = ' + project_name
        print 'user_domain_name = ' + user_domain_name
        print 'project domain name = ' + project_domain_name + '\n'
        
        authorization = keystoneclient.auth.identity.v3.Password(auth_url=auth_url,
                                                                 username=username, 
                                                                 password=password, 
                                                                 project_name=project_name, 
                                                                 user_domain_name=user_domain_name, 
                                                                 project_domain_name=project_domain_name)
        
        sess = keystoneclient.session.Session(auth=authorization,verify=False)

        nova_api_version = '2'
        print 'Creating nova client with API version ' + nova_api_version
        
        self.nova_client = novaclient.client.Client(nova_api_version, session=sess)

    def terminate_instance(self, instance_id):
        
        print 'Finding OpenStack instance ' + instance_id
        server = self.nova_client.servers.find(id=instance_id)
        
        print 'Terminating OpenStack instance ' + instance_id
        server.delete()
        
    def terminate_error_state_instances(self):
        
        for server in self.nova_client.servers.list():
            
            if server.status.lower() == 'error':
                print 'Terminating server {0}, id {1}, state {2}'.format(server.name, server.id, server.status)
                server.delete()
        
    def get_hypervisor_details(self, hypervisor_name):
        
        print 'Getting hypervisor details for host ' + str(hypervisor_name)
        found_hypervisor = self.nova_client.hypervisors.find(hypervisor_hostname=hypervisor_name)
        hypervisors_dict = found_hypervisor.to_dict()
        
        print 'Hypervisor details found: '
        print json.dumps(hypervisors_dict, sort_keys=True, indent=4, separators=(',', ': '))
        
        return hypervisors_dict
