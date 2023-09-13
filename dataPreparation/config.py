from dateutil import parser

SIMULATOR_START_TIME = parser.parse('2016-01-01')
SIMULATOR_END_TIME = parser.parse('2020-01-01')
DATA_DIRECTORY = '/voyager/datasets/liver_transplant/SRTR_2023/pubsaf2303'
# made a change to yaml list of output dirs
MELD_POLICY = 'DynaMELD-Common' # "MELD-Na", "MELD3.0", "DynaMELD_features_delta"
OUTPUT_DIRECTORY = f'../LivSim_Input/postprocessed/postprocess_result_{MELD_POLICY}'
INPUT_DIRECTORY = f'../LivSim_Input/preprocessed/'
COHORT_DIR = f"../LivSim_Input/dataset/"
