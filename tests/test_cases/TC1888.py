'''
Created on Mar 31, 2016

@author: lfiliks-dev
'''
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from filegenerators import predict
from filegenerators import kricocsv
from kricoclient import kricoclient
import numpy
import itertools

PREDICT_LOAD_TEST_CSV_HEADER = ["category",
                                "processors",
                                "memory"]

LOAD_PREDICTED_CSV_HEADER = ["disk_iops",
                             "network_bandwidth",
                             "ram_size",
                             "cpu_threads"]

# processors
PARAM1 = list(numpy.arange(4, 48, 12))

# memory
PARAM2 = list(numpy.arange(4, 62, 20))

# prepare launch file with default parameters / or os.env parameters
krico_predict_file = predict.PredictFile()
krico_client = kricoclient.KricoClient()
krico_csv_file = kricocsv.CsvFile(new_file=True,
                                  list_header_main=PREDICT_LOAD_TEST_CSV_HEADER,
                                  list_header_extension=LOAD_PREDICTED_CSV_HEADER,
                                  krico_csv_filename="KRICO-predict-load-test-science.csv")

for p1, p2 in itertools.product(PARAM1, PARAM2):
    krico_predict_file.update_workload_params(workload_class="science",
                                              image_name="wrkld-science-hpcg",
                                              param1=p1,
                                              param2=p2,
                                              param3=20,
                                              param4=0)

    krico_client.predict_load(krico_predict_file.get_json())
    
    load_predicted = krico_client.get_last_response_entry("predictions")

    if load_predicted:
        for prediction in load_predicted:
            csv_row_data = ["science", p1, p2]

            krico_csv_file.write_entry(csv_row_data, prediction["requirements"])
    else:
        break