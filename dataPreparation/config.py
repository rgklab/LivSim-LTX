from dateutil import parser

SIMULATOR_START_TIME = parser.parse('2016-01-01')
SIMULATOR_END_TIME = parser.parse('2020-01-01')
DATA_DIRECTORY = '/voyager/datasets/liver_transplant/SRTR_2023/pubsaf2303'
OUTPUT_DIRECTORY = './preprocess_result_30'
INPUT_DIRECTORY = './experiment2'
MELD_POLICY = '30'
