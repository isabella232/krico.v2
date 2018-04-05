'''
Created on Mar 11, 2016

@author: lfiliks-dev
'''

import subprocess
import os
import itertools

#OpenStack access parameters
os.environ['krico_openstack_keypair'] = 'krico-03-keypair'
os.environ['krico_openstack_keypair_file'] = '/home/ubuntu/ssh-keys/'+os.environ['krico_openstack_keypair']+'.pem'

#KRICO instructions on how to run the workload
os.environ['krico_workload_class'] = 'unknown'
os.environ['krico_img_name'] = 'wrkld-bigdata-hadoop'
os.environ['krico_generate_csv'] = 'True'
os.environ['krico_sleep_update_monitors_s'] = '600'

#user parameters:
'''
downloaded and available datasets:

wikipedia_50GB


available datasets (KRICO NFS):

wikipedia_140GB
sort_30GB
sort_150GB
selfjoin_30GB
selfjoin_80GB
kmeans_30GB
kmeans_100GB
adjlist_30GB
rankedinvindex_40GB
rankedinvindex_110GB
'''
datasets = ['wikipedia_50GB']


'''
available benchmarks:

termvectorperhost
invertedindex
adjlist
kmeans
histogram_movies
histogram_ratings
sequencecount
terasort
grep
wordcount
'''
benchmarks = ['wordcount', 'invertedindex']

for dataset, benchmark in itertools.product(datasets, benchmarks):
    
    os.environ['krico_bigdata_dataset'] = dataset
    os.environ['krico_bigdata_benchmark'] = benchmark

    subprocess.call("python smoketest.py", shell=True)
