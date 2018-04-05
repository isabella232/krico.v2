'''
Created on Mar 17, 2016

@author: lfiliks-dev
'''

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from filegenerators import predict
from kricoclient import kricoclient

krico_predict_file = predict.PredictFile()
krico_client = kricoclient.KricoClient()

krico_client.predict_load(krico_predict_file.get_json())
