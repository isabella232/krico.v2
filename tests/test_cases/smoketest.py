'''
Created on Mar 9, 2016

@author: lfiliks-dev
'''

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from filegenerators import launch
from filegenerators import classify
from kricoclient import kricoclient
from kricoopenstack import osclient
from kricoopenstack import workloadlauncher
from mongo import client
from filegenerators import kricocsv
from os import environ
import os
import json
import time

print '''

KRICO testing framework

This script will:

    - Generate KRICO launch.json file
    - Call 'launch' KRICO API method to launch an OpenStack instance
    - Run workload commands on created VM
    - Use OpenStack API to terminate created instance
    - Classify terminated instance using KRICO API
    - Remove entry from mongoDB
    - If instructed, will generate CSV entry (and file with header, if necessary)

'''

# prepare launch file with default parameters / or os.env parameters
krico_launch_file = launch.LaunchFile()

# create KRICO client object
krico_client = kricoclient.KricoClient()

# Count of VM launches between classifier updates
try:
    launch_count = int(os.environ['krico_launch_count'])
except KeyError:
    launch_count = 1

# Count of whole test runs
try:
    test_count = int(os.environ['krico_test_count'])
except KeyError:
    test_count = 1

for test_num in range(test_count):
    print 'TEST #{} OF {}'.format(test_num + 1, test_count)

    # Create lists for classifier summary after each test
    krico_expected_classified_category_list = []
    krico_classified_as_list = []

    for launch_num in range(launch_count):
        print 'LAUNCH #{} OF {}'.format(launch_num + 1, launch_count)

        # launch instance using KRICO
        krico_client.launch_instance(krico_launch_file.get_json())

        krico_instance_id = krico_client.get_last_response_entry('instance_id')
        krico_floating_ip = krico_client.get_last_response_entry('ip_floating')
        krico_instance_ids = []
        krico_instance_ips = []

        krico_instance_id_client = None
        krico_floating_ip_client = None

        # execute commands to start workload tasks
        krico_workload_launcher = workloadlauncher.WorkloadLauncher(server=krico_floating_ip)

        krico_launch_image_name = krico_launch_file.get_dict()['image']
        krico_expected_classified_category = 'unknown'

        if krico_launch_image_name == 'wrkld-streaming-vlc':

            params = {}
            try:
                params['clients'] = environ['krico_streaming_vlc_clients']
            except KeyError:
                params = {}

            krico_workload_launcher.launch_streaming_VLC(params)
            krico_expected_classified_category = 'streaming'

        elif krico_launch_image_name == 'wrkld-streaming-darwin':
            krico_workload_launcher = workloadlauncher.WorkloadLauncher(server=krico_floating_ip, username="root")
            krico_workload_launcher.launch_streaming_darwin()

            print ('Streaming workload needs client. Creating one.')
            environ['krico_workload_class'] = 'unknown'
            environ['krico_img_name'] = 'wrkld-streaming-darwin'
            environ['krico_param1'] = '4.0'
            environ['krico_param1'] = '16384.0'
            environ['krico_param1'] = '20.0'
            environ['krico_param1'] = '10.0'

            krico_launch_client_file = launch.LaunchFile()
            krico_client.launch_instance(krico_launch_client_file.get_json())
            krico_instance_id_client = krico_client.get_last_response_entry('instance_id')
            krico_floating_ip_client = krico_client.get_last_response_entry('ip_floating')
            krico_workload_launcher_client = workloadlauncher.WorkloadLauncher(server=krico_floating_ip_client, username="root")

            params = {}
            try:
                params['clients'] = environ['krico_streaming_darwin_clients']
                params['quality'] = environ['krico_streaming_darwin_quality']
            except KeyError:
                params = {}

            krico_workload_launcher_client.launch_streaming_darwin_client(darwin_server=krico_floating_ip, params=params)

            krico_expected_classified_category = 'streaming'

        elif krico_launch_image_name == 'wrkld-science-hpcg':
            krico_workload_launcher = workloadlauncher.WorkloadLauncher(server=krico_floating_ip, username="root")
            environ['krico_workload_class'] = 'unknown'
            environ['krico_img_name'] = 'wrkld-science-hpcg'
            environ['krico_param1'] = '4.0'
            environ['krico_param1'] = '16384.0'
            environ['krico_param1'] = '20.0'
            environ['krico_param1'] = '10.0'

            try:
                num_slave_nodes = int(environ['krico_science_hpcg_slave_nodes'])
            except (KeyError, ValueError) as ex:
                print ex
                num_slave_nodes = 3

            # create more clients for science workload tests
            for i in range(0, num_slave_nodes):
                krico_client.launch_instance(krico_launch_file.get_json())
                krico_instance_ids.append(krico_client.get_last_response_entry('instance_id'))
                krico_instance_ips.append(krico_client.get_last_response_entry('ip_floating'))

            time.sleep(20)

            # retrieve OS environ for workload parameters
            params = {}
            try:
                params['memory'] = environ['krico_science_hpcg_memory']
                params['processors'] = environ['krico_science_hpcg_processors']
                params['threads'] = environ['krico_science_hpcg_threads']
                params['hpcg_duration'] = environ['krico_science_hpcg_duration']
            except KeyError:
                params = {}
            # run main server benchmark
            krico_workload_launcher.launch_science_HPCG(krico_floating_ip, krico_instance_ips, params)

            krico_expected_classified_category = 'science'
        elif krico_launch_image_name == 'wrkld-storage-postmark':
            krico_workload_launcher.launch_storage_postmark()
            krico_expected_classified_category = 'unknown'
        elif krico_launch_image_name == 'wrkld-webserving-jmeter':
            environ['krico_workload_class'] = 'unknown'
            environ['krico_img_name'] = 'wrkld-webserving-jmeter'
            environ['krico_param1'] = '4.0'
            environ['krico_param1'] = '16384.0'
            environ['krico_param1'] = '20.0'
            environ['krico_param1'] = '10.0'

            krico_launch_client_file = launch.LaunchFile()

            params = {}
            try:
                num_slave_nodes = int(environ['krico_webserving_num_slave_nodes'])
                clients_count = int(environ['krico_webserving_clients_count'])
                params['main_page_interations'] = environ['krico_webserving_main_page_iterations']
                params['search_iterations'] = environ['krico_webserving_search_iterations']
                params['comment_iterations'] = environ['krico_webserving_comment_iterations']
            except (KeyError, ValueError) as ex:
                print ex
                num_slave_nodes = 2
                clients_count = 128
                params = {'main_page_interations': 1, 'search_iterations': 1, 'comment_iterations': 1}

            # create clients for webserving workload tests
            for i in range(0, num_slave_nodes):
                krico_client.launch_instance(krico_launch_client_file.get_json())

                krico_instance_ids.append(krico_client.get_last_response_entry('instance_id'))
                krico_instance_ips.append(krico_client.get_last_response_entry('ip_floating'))
                krico_workload_launcher = workloadlauncher.WorkloadLauncher(
                    server=krico_client.get_last_response_entry('ip_floating'), username="root")
                krico_workload_launcher.launch_apache_jmeter_client(krico_floating_ip, clients_count, params)

            krico_expected_classified_category = 'webserving'
        elif krico_launch_image_name == 'wrkld-caching-redis':

            krico_workload_launcher.launch_caching_redis()

            print ('Caching workload needs client. Creating one.')
            environ['krico_workload_class'] = 'unknown'
            environ['krico_img_name'] = 'wrkld-caching-redis'
            environ['krico_param1'] = '4.0'
            environ['krico_param1'] = '16384.0'
            environ['krico_param1'] = '20.0'
            environ['krico_param1'] = '10.0'
            krico_launch_client_file = launch.LaunchFile()
            krico_client.launch_instance(krico_launch_client_file.get_json())
            krico_instance_id_client = krico_client.get_last_response_entry('instance_id')
            krico_floating_ip_client = krico_client.get_last_response_entry('ip_floating')
            krico_workload_launcher_client = workloadlauncher.WorkloadLauncher(server=krico_floating_ip_client)

            params = {}
            try:
                params['clients'] = os.environ['krico_caching_redis_clients']
                params['ratio'] = os.environ['krico_caching_redis_ratio']
                params['test_time'] = os.environ['krico_caching_redis_test_time']
            except KeyError:
                params = {}

            krico_workload_launcher_client.launch_caching_redis_client(redis_server=krico_floating_ip, params=params)

            krico_expected_classified_category = 'caching'
        elif krico_launch_image_name == 'wrkld-storage-postmark':
            krico_workload_launcher.launch_storage_postmark()
            krico_expected_classified_category = 'storage'
        elif krico_launch_image_name == 'wrkld-oltp-ycsb':
            # retrieve OS environ for workload parameters
            params = {}
            try:
                params['clients'] = os.environ['krico_oltp_clients']
                params['data'] = os.environ['krico_oltp_data']
            except KeyError:
                params = {}

            krico_workload_launcher = workloadlauncher.WorkloadLauncher(server=krico_floating_ip, username="root")
            krico_workload_launcher.launch_oltp_ycsb(params)
            krico_expected_classified_category = 'oltp'
        elif krico_launch_image_name == 'wrkld-bigdata-hadoop':
            # retrieve OS environ for workload parameters
            params = {}
            try:
                params['dataset'] = os.environ['krico_bigdata_dataset']
                params['benchmark'] = os.environ['krico_bigdata_benchmark']
            except KeyError:
                params = {}

            krico_workload_launcher = workloadlauncher.WorkloadLauncher(server=krico_floating_ip, username="root")
            krico_workload_launcher.launch_bigdata_hadoop(params)
            krico_expected_classified_category = 'bigdata'
        else:
            print 'Could not launch workload apps due to unknown category'

        SLEEP_TIME = 30
        try:
            SLEEP_TIME = int(environ['krico_sleep_update_monitors_s'])
        except KeyError:
            SLEEP_TIME = 30

        print 'Sleeping to update monitors... (' + str(SLEEP_TIME) + 's)'
        time.sleep(SLEEP_TIME)

        # classify running instance
        print 'Classify running VM'
        krico_classify_file = classify.ClassifyFile(krico_instance_id)
        krico_client.classify_instance(krico_classify_file.get_json())
        krico_classified_as = krico_client.get_last_response_entry('predicted_category')
        print 'VM classified as: ' + str(krico_classified_as)

        print 'Terminate instance'
        # terminate created instance
        openstack_client = osclient.KricoOpenstackClient()

        openstack_client.terminate_instance(krico_instance_id)

        for instance_id in krico_instance_ids:
            openstack_client.terminate_instance(instance_id)

        if krico_instance_id_client is not None:
            openstack_client.terminate_instance(krico_instance_id_client)

        # create MongoDB client
        mongo_client = client.KricoMongoClient()
        mongo_entry = mongo_client.format_response(mongo_client.get_service_entry(krico_instance_id, max_tries=16, sleep_time_s=30))
        load_measured = mongo_client.get_load_measured(krico_instance_id, max_tries=16, sleep_time_s=30)
        if (mongo_entry is None) or (load_measured is None):
            print 'MongoDB not populated with measured data from KRICO monitors, aborting...'
            sys.exit(-1)

        try:
            if os.environ['krico_remove_db_entry'] == 'False':
                REMOVE_MONGO_ENTRY = False
            else:
                REMOVE_MONGO_ENTRY = True
        except KeyError:
            REMOVE_MONGO_ENTRY = True

        # remove entry from mongoDB

        if REMOVE_MONGO_ENTRY:
            mongo_client.remove_service_entry(krico_instance_id)
            mongo_client.remove_monitor_entry(krico_instance_id)

            if krico_instance_id_client is not None:
                mongo_client.remove_service_entry(krico_instance_id_client)
                mongo_client.remove_monitor_entry(krico_instance_id_client)

        GENERATE_CSV = False
        try:
            GENERATE_CSV = environ['krico_generate_csv']

            if GENERATE_CSV == 'False':
                GENERATE_CSV = False
            if GENERATE_CSV == 'True':
                GENERATE_CSV = True
            elif GENERATE_CSV == 0:
                GENERATE_CSV = False
            elif GENERATE_CSV == 1:
                GENERATE_CSV = True

        except KeyError:
            GENERATE_CSV = False

        if GENERATE_CSV:

            print 'Downloading hypervisor data...'
            hypervisor_details = openstack_client.get_hypervisor_details(mongo_entry['host'])
            hypervisor_cpu_info = json.loads(hypervisor_details['cpu_info'])

            print 'Generating CSV entry...'
            workload_params_list = {'params_' + key: params[key] for key in params.keys()} 
            krico_csv_file = kricocsv.CsvFile(False, kricocsv.DEFAULT_LOAD_MEASURED_HEADER + workload_params_list.keys())
            krico_launch_parameters = mongo_entry['parameters'].values()

            initial_size = len(krico_launch_parameters) - 1

            for i in range(initial_size, 4):
                krico_launch_parameters.append('0')

            try:
                list_params = [mongo_entry['start_time'],
                            mongo_entry['category'],
                            krico_expected_classified_category,
                            krico_classified_as,
                            mongo_entry['image'],
                            krico_launch_parameters[0],
                            krico_launch_parameters[1],
                            krico_launch_parameters[2],
                            krico_launch_parameters[3],
                            mongo_entry['flavor']['name'],
                            mongo_entry['availability_zone']['disk']['iops'],
                            '', # predicted_net_io,
                            mongo_entry['flavor']['ram'],
                            mongo_entry['flavor']['vcpus'],
                            mongo_entry['host'],
                            hypervisor_cpu_info['model'],
                            hypervisor_details['vcpus']]

                krico_csv_file.write_entry(list_params, load_measured, workload_params_list)

            except KeyError as ex:
                print 'Exception KeyError raised while generating CSV entry... details = ' + str(ex)
                print 'Mongo entry: '
                print mongo_entry
                print 'hypervisor_cpu_info = ' + str(hypervisor_cpu_info)
                print 'hypervisor_details = ' + str(hypervisor_details)
                print 'krico_launch_parameters = ' + str(krico_launch_parameters)
            except Exception as ex:
                print 'Exception found but not handled... details = ' + str(ex)

            krico_csv_file.close_file()

        krico_expected_classified_category_list.append(krico_expected_classified_category)
        krico_classified_as_list.append(krico_classified_as)
    
    f = open('calibration_test_summary.log', 'a')
    print >> f, '======== TEST #{} SUMMARY ========'.format(test_num + 1)
    print >> f, 'EXPECTED CATEGORY    CLASSIFIED AS'
    results = zip(krico_expected_classified_category_list, krico_classified_as_list)
    failed = 0
    err_ratio = 0.0
    for result in results:
        separator = ' ' * (21 - len(result[0]))
        print >> f, '{}{}{}'.format(result[0], separator, result[1])

        if result[0] != result[1]:
            failed += 1
    
    if failed != 0:
        err_ratio = len(results) / failed
    print >> f, 'TEST ERROR RATIO: {}'.format(err_ratio)

    # Refresh classifier if there is next test to start - classifier is refreshed between each launch & classify test series
    if test_num < test_count - 1:
        print >> f, '\nRefreshing classifier...'
        for i in range(3):
            if krico_client.refresh_classifier() != -1:
                print >> f, 'Classifier refreshed.'
                break
            else:
                print >> f, 'Classifier refresh error (' + str(i + 1) + '/3)'
        print >> f, 'Refreshing predictor...'
        for i in range(3):
            if krico_client.refresh_predictor() != -1:
                print >> f, 'Predictor refreshed.'
                break
            else:
                print >> f, 'Predictor refresh error (' + str(i + 1) + '/3)'
        
        print >> f, 'Refreshing instances...'
        for i in range(3):
            if krico_client.refresh_instances() != -1:
                print >> f, 'Instances refreshed.'
                break
            else:
                print >> f, 'Instances refresh error (' + str(i + 1) + '/3)'
        print >> f, 'Starting next test.\n'

    f.close()
