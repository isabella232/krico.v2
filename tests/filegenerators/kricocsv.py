'''
Created on Mar 8, 2016

@author: lfiliks-dev
'''

import csv
import os.path

DEFAULT_LOAD_MEASURED_HEADER = ["cpu:cache:misses",
                                "cpu:cache:references",
                                "cpu:time",
                                "network:bandwidth:receive",
                                "network:bandwidth:send",
                                "network:packets:receive",
                                "network:packets:send",
                                "ram:used",
                                "disk:bandwidth:read",
                                "disk:bandwidth:write",
                                "disk:operations:read",
                                "disk:operations:write"]

DEFAULT_LIST_HEADER = ['timestamp',
                       'launched_as',
                       'category_expected',
                       'classified_as',
                       'image_name',
                       'param1',
                       'param2',
                       'param3',
                       'param4',
                       'flavor',
                       'predicted_disk_io',
                       'predicted_net_io',
                       'predicted_ram',
                       'predicted_vcpus',
                       'host_name',
                       'host_cpu_model',
                       'host_vcpus']


class CsvFile(object):
    def __init__(self,
                 new_file=False,
                 list_header_extension=DEFAULT_LOAD_MEASURED_HEADER,
                 list_header_main=DEFAULT_LIST_HEADER,
                 krico_csv_filename="KRICO-autogen-output.csv"):

        '''
        Constructor
        '''

        self.list_header_extension = list_header_extension

        self.list_header = list_header_main

        open_mode = 'a'
        write_header = False

        print 'Creating output file ' + krico_csv_filename

        if not os.path.isfile(krico_csv_filename):
            open_mode = 'wb'
            write_header = True
            print 'Will write header, file does not exist yet'
        elif new_file:

            try:
                os.remove(krico_csv_filename)
            except OSError as ex:
                print 'Could not remove CSV file. ex = ' + str(ex)

            open_mode = 'wb'
            write_header = True
            print 'Will write header, force new file flag set'

        self.csv_file = open(krico_csv_filename, open_mode)
        self.csv_writer = csv.writer(self.csv_file, delimiter=',')

        if write_header:
            self.write_header()

    def write_header(self, list_header=None, list_load_measured=None):

        print 'Writing header to CSV file'

        if list_load_measured is not None:
            self.list_header_extension = list_load_measured

        print self.list_header_extension

        if list_header is not None:
            self.list_header = list_header

        print self.list_header

        self.list_header.extend(self.list_header_extension)

        self.csv_writer.writerow(self.list_header)

    def write_entry(self, list_params, dict_load_measured, dict_wrkld_params=None):
        if (len(self.list_header) != len(list_params) + len(dict_load_measured) + 
            len(dict_wrkld_params) if dict_wrkld_params else 0):
            print 'Error: CSV header items count differs from values count'

        print 'Writing row to CSV file'
        list_load_measured = []
        list_wrkld_params = []

        for element in self.list_header_extension:
            if element in dict_load_measured:
                list_load_measured.append(dict_load_measured[element])
                print 'Appending dict_load_measured[' + str(element) + '] = ' + str(dict_load_measured[element])
            elif element in dict_wrkld_params:
                list_wrkld_params.append(dict_wrkld_params[element])
                print 'Appending dict_wrkld_params[' + str(element) + '] = ' + str(dict_wrkld_params[element])
            else:
                print 'Error: CSV header items does not match with initialized parameters ({}).'.format(element)

        self.csv_writer.writerow(list_params + list_load_measured + list_wrkld_params)

    def close_file(self):

        print 'Closing CSV file'
        self.csv_file.close()
