'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

import paramiko
import time
import os

class WorkloadLauncher(object):
    
    '''
    classdocs
    '''

    def __init__(self, 
                 server, 
                 username = 'ubuntu', 
                 password = ''):
        
        KEYPAIR_FILE = None
        self.ssh_client = None
        
        try:
            env_var_name = 'krico_openstack_keypair_file'
            print 'Retrieving os env variable ' + env_var_name
            KEYPAIR_FILE = os.environ[env_var_name]
        except Exception as ex:
            print 'Exception caught, type Exception, value: '
            print ex
        
        if KEYPAIR_FILE == None:
            print 'Could not determine key file path.'
            return
            
        if os.path.isfile(KEYPAIR_FILE) == False:
            print 'Cloud not find key file: ' + str(KEYPAIR_FILE)
            return
            
        self.open_connection(server, username, password, KEYPAIR_FILE)
        
    def open_connection(self, server, username, password, key_filename):
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        max_try = 30
        
        for x in range(0, max_try):
            try:
                print 'Connecting to remote host=' + server + \
                      ', user=' + username + \
                      ', password=' + password + \
                      ', key_filename=' + key_filename
                      
                self.ssh_client.connect(server, username=username, password=password, key_filename=key_filename)
            except paramiko.ssh_exception.NoValidConnectionsError as ex:
                #wait and try again
                print ex
                print 'SSHException raised while establishing SSH '+ \
                      'connection to remote host. Waiting and trying one more time (' + str(x+1) + \
                      '/' + str(max_try+1) +')'
                
                time.sleep(10) #10 sec
                if x == 2:
                    print 'Max tries reached, aborting.'
                    #sys.exit(-1)
                continue
            except Exception as ex:
                print ex
                print 'Exception raised while connecting to remote host. Aborting.'
                #sys.exit(-1)
        
            break
  
        channel = self.ssh_client.invoke_shell()
        self.ssh_stdin = channel.makefile('wb')
        self.ssh_stdout = channel.makefile('rb')
        
    def execute_command(self, remote_command):
        
        if self.ssh_client == None:
            print 'There is no SSH connection established between testing machine and workload machine. Aborting.'
            return
        
        print 'Executing command on remote machine: '
        print remote_command
        
        self.ssh_stdin.write(remote_command)
            
        print self.ssh_stdout.read()
        
    def launch_science_HPCG(self, main_server_IP, list_hosts, params={}):
        
        '''
        user parameters:
        memory: 1, 21, 42, 62 [GB]
        processors: 4, 16, 32, 48 [VCPUs]
        
        HPCG parameters required:
        duration: 900 [s]
        hosts: 4 [VMs hosting benchmark]
        threads: 1, 2, 4 [per process]
        '''
        
        try:
            memory = int(params['memory'])
            processors = int(params['processors'])
            threads = int(params['threads'])
            hpcg_duration = int(params['hpcg_duration'])
            
        except (KeyError, ValueError) as ex:
            print ex
            print "No params found. Using default values."
            
            memory = 42
            processors = 48
            threads = 32
            hpcg_duration = 3000

        hosts = len(list_hosts) + 1
            
        print 'Launching Science (HPCG) workload with parameters: memory={0}, \
            processors={1}, threads={2}, hosts={3}'.format(memory, processors, threads, hosts)
                
        hpcg_processes_per_host = processors / threads
        hpcg_processes = hosts * hpcg_processes_per_host
        hpcg_memory_per_process = memory * (1024**3)
        
        hpcg_dimension_total = hpcg_memory_per_process / 1000
        hpcg_dimension_x = int(hpcg_dimension_total ** (1.0/3.0) / 8.0) * 8
        hpcg_dimension_y = int((hpcg_dimension_total / hpcg_dimension_x)**(1.0/2.0) / 8.0) * 8
        hpcg_dimension_z = int(hpcg_dimension_total / (hpcg_dimension_x * hpcg_dimension_y) / 8.0) * 8
        
        hosts_string = ""
        for host in list_hosts:
            hosts_string += '''{0}
            '''.format(str(host))
        
        remote_command = '''
            cd /home/ubuntu/krico/science/hpcg-2.4/build/bin
            echo 'HPCG benchmark input file
            Sandia National Laboratories; University of Tennessee, Knoxville
            {0} {1} {2}
            {3}
            ' > hpcg.dat
            export OMP_NUM_THREADS={4}
            echo '{5}
            {6}
            ' > hosts.txt
            mpiexec -d -machinefile hosts.txt -np {7} /home/ubuntu/krico/science/hpcg-2.4/build/bin/xhpcg & disown -a
            sleep 5
            exit
            '''.format(hpcg_dimension_x, hpcg_dimension_y, hpcg_dimension_z, 
                       hpcg_duration, threads, main_server_IP, hosts_string, hpcg_processes)
        
        self.execute_command(remote_command)
    
    def launch_streaming_VLC(self, params={}):
        
        '''
        Available commands on streaming workload:

        # send video stream to multicast address in a loop (this does not require any clients):
        cvlc -vvv /home/ubuntu/krico/videos/Intel-HPC.mp4 --sout udp:234.5.6.7 --ttl 0 --sout-keep --loop

        # reserve some virtual memory in RAM
        stress --vm 2 --vm-bytes 512M --vm-hang 0

        # set up a RTSP server to be ready to send some RTP data after DESCRIBE, SETUP and PLAY RTSP requests
        cvlc -vvv /home/ubuntu/videos/Intel-HPC.mp4 --sout '#rtp{sdp=rtsp://:8554/intelHPC}' --sout-keep --loop &

        '''
        
        try:
            clients = int(params['clients'])
            
        except (KeyError, ValueError) as ex:
            print ex
            print "No params found. Using default values."
            
            clients = 100
        
        remote_command = '''
            for i in $(seq 0 1 {0})
            do
            j=$(($i/255))
            k=$(($i-j*255))
            echo "cvlc -vvv /home/ubuntu/krico/videos/Intel-HPC.mp4 --sout udp:234.5.$j.$k --ttl 0 --sout-keep --loop & " >> runVlcWorkload.sh
            done
            sh runVlcWorkload.sh & disown -a
            sleep 5
            exit
            '''.format(clients)

        self.execute_command(remote_command)
        
    def launch_caching_redis(self):
        
        remote_command = '''
            /home/ubuntu/redis/redis-3.0.7/src/redis-server &
            exit
            '''
        
        self.execute_command(remote_command)
        
    def launch_caching_redis_client(self, redis_server, params={}):
        
        try:
            clients = int(params['clients'])
            ratio = params['ratio']
            test_time = int(params['test_time'])
            
        except (KeyError, ValueError) as ex:
            print ex
            print "No params found. Using default values."
            
            clients = 384
            ratio = '8:10'
            test_time = 6000
        
        remote_command = '''
            memtier_benchmark --clients={0} --ratio="{1}" --test-time={2} --server={3} & disown -a
            sleep 5
            exit
            '''.format(clients, ratio, test_time, str(redis_server))
        
        self.execute_command(remote_command)
        
    def launch_streaming_darwin(self):
        
        '''
        video files are stored in:
        /usr/local/movies/streamingVideos_1X, where X is in a range(0,9)
        '''
        
        src_video_path = "/usr/local/movies/streamingVideos_11/"
        dst_video_path = "/usr/local/movies/streamingVideos_10/"
        bulk_copies = 2
        
        remote_command = '''
            sh /usr/local/movies/copy_video_files.sh ''' \
            + src_video_path \
            + ' ' + dst_video_path \
            + ' ' + str(bulk_copies) \
            + '''
            /usr/local/sbin/DarwinStreamingServer -dDS 1 &
            exit
            '''
        
        self.execute_command(remote_command)
          
    def launch_streaming_darwin_client(self, darwin_server, params={}):
        
        try:
            num_clients = int(params['clients'])
            quality = params['quality']
            
        except (KeyError, ValueError) as ex:
            print ex
            print "No params found. Using default values."
            
            num_clients = 100
            quality = 'longhi'
        
        remote_command = '''
            echo 'for i in $(seq 0 1 100)
            do
            sh /home/ubuntu/faban_streaming/streaming-release/streaming/scripts/start-run.sh ''' \
            + str(num_clients) + ' ' \
            + quality + ' ' \
            + str(darwin_server) \
            + ''' 2
            done
            ' > runDarwinClient.sh 
            sh runDarwinClient.sh & disown -a &
            exit
            '''
        
        self.execute_command(remote_command)
        
    def launch_bigdata_hadoop(self, params={}):
        
        try:
            dataset = params['dataset']
            benchmark = params['benchmark']
            
        except KeyError as ex:
            print ex
            print "No params found. Using default values."
            
            dataset = 'wikipedia_50GB'
            benchmark = 'wordcount'
        
        remote_command = '''
            echo '
            . /usr/local/hadoop/sbin/start-all.sh
            sshpass -p 'Sam@Clouds' scp -r -o StrictHostKeyChecking=no ubuntu@172.16.0.1:/home/ubuntu/krico/NFS/bigdata-sets/{0}.tar.bz2 /home/ubuntu
            /usr/local/hadoop/bin/hadoop fs -mkdir /{0}
            /usr/local/hadoop/bin/hadoop fs -rm -r /out
            tar xvjf /home/ubuntu/{0}.tar.bz2
            /usr/local/hadoop/bin/hadoop fs -put {0}/* /{0}
            /usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.6.0.jar {1} /{0} /out & disown -a & exit
            sleep 5 & exit
            ' > bigdata.sh
            . bigdata.sh
            '''.format(dataset, benchmark)

        self.execute_command(remote_command)

    def launch_oltp_ycsb(self, params={}):
        
        #user parameter data in a range 10 to 100
        #user parameter clients in a range 500 - 2000
        
        try:
            clients = int(params['clients'])
            data = int(params['data'])
            
        except (KeyError, ValueError) as ex:
            print ex
            print "No params found. Using default values."
            
            clients = 800
            data = 50
        
        target_ops = 20000
        fieldcount = 10
        fieldlength = 100
        recordcount = 10000000 #PG uses 1000
        operationcount = 25000000
        readallfields = 'true'
        readproportion = 0.5
        updateproportion = 0.05
        scanproportion = 0
        insertproportion = 0
        requestdistribution = 'zipfian'
        readmodifywriteproportion = 0
        
        '''
        This workload consists of 2 stages: load and run.
        PG does not monitor workload while in 'loading' stage.
        '''
        
        remote_command = '''
            cd /home/ubuntu/ycsb-0.8.0
            #./bin/ycsb load basic -P workloads/workloada -p recordcount={4} -s > load.dat
            echo '
            ./bin/ycsb run basic -P workloads/workloada -P large.dat \
            -s -threads {0} -target {1} -p fieldcount={2} -p fieldlength={3} -p recordcount={4} -p operationcount={5} \
            -p readallfields={6} -p readproportion={7} -p updateproportion={8} -p scanproportion={9} -p insertproportion={10} \
            -p requestdistribution={11} -p readmodifywriteproportion={12}
             > transactions.dat
            ' >> executeOltp.sh
            
            echo 'for i in $(seq 0 1 100)
            do
            sh executeOltp.sh & sh executeOltp.sh & sh executeOltp.sh & sh executeOltp.sh \
            sh executeOltp.sh & sh executeOltp.sh & sh executeOltp.sh & sh executeOltp.sh \
            sh executeOltp.sh & sh executeOltp.sh & sh executeOltp.sh & sh executeOltp.sh & disown -a
            sleep 30
            done
            ' > runOltpMultipleInstances.sh 
            
            sh runOltpMultipleInstances.sh & disown -a
            
            sleep 5
            exit
            '''.format(clients, target_ops, fieldcount, fieldlength, recordcount*data, operationcount,
                       readallfields, readproportion, updateproportion, scanproportion, insertproportion,
                       requestdistribution, readmodifywriteproportion)
        
        self.execute_command(remote_command)

    def launch_storage_postmark(self):

        remote_command = '''
            cd /home/ubuntu/krico/postmark-intc
            . /home/ubuntu/krico/postmark-intc/postmark-intc-loop.sh & disown -a
            sleep 5
            exit
            '''

        self.execute_command(remote_command)

    def launch_apache_jmeter_client(self, srv_ip, clients, params):
        try:
            main_page_iterations = int(params['main_page_interations'])
            search_iterations = int(params['search_iterations'])
            comment_iterations = int(params['comment_iterations'])
        except (KeyError, ValueError) as ex:
            print ex
            print "No params found"
            main_page_iterations = 0
            search_iterations = 0
            comment_iterations = 0
            
        command_clients = int(clients/8)
        remote_command = '''
        cd /home/ubuntu/apache-jmeter-2.13
        echo 'nohup ./bin/jmeter -n -t WPMark.jmx -Jserver_name {0} -Jserver_port 80 -Jthreads {1} -Jiterations 10000 -Jmain_page_iterations {2} \
        -Jsearch_iterations {3} -Jcomment_iterations {4} > /dev/null 2>&1 &
        nohup ./bin/jmeter -n -t WPMark.jmx -Jserver_name {0} -Jserver_port 80 -Jthreads {1} -Jiterations 10000 -Jmain_page_iterations {2} \
        -Jsearch_iterations {3} -Jcomment_iterations {4} > /dev/null 2>&1 &
        nohup ./bin/jmeter -n -t WPMark.jmx -Jserver_name {0} -Jserver_port 80 -Jthreads {1} -Jiterations 10000 -Jmain_page_iterations {2} \
        -Jsearch_iterations {3} -Jcomment_iterations {4} > /dev/null 2>&1 &
        nohup ./bin/jmeter -n -t WPMark.jmx -Jserver_name {0} -Jserver_port 80 -Jthreads {1} -Jiterations 10000 -Jmain_page_iterations {2} \
        -Jsearch_iterations {3} -Jcomment_iterations {4} > /dev/null 2>&1 &' > script.sh
        chmod +x script.sh
        ./script.sh & disown -a
        exit
        '''.format(srv_ip, command_clients, main_page_iterations, search_iterations, comment_iterations)

        self.execute_command(remote_command)

    def close_connection(self):
        
        self.ssh_stdout.close()
        self.ssh_stdin.close()    
        self.ssh_client.close()
