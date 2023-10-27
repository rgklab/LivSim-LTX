from dateutil import parser

SIMULATOR_START_TIME = parser.parse('2016-01-01')
SIMULATOR_END_TIME = parser.parse('2020-01-01')
DATA_DIRECTORY = '/voyager/datasets/liver_transplant/SRTR_2023/pubsaf2303'
# made a change to yaml list of output dirs

# 'DynaMELD_MELD3.0_None',
# 'DynaMELD_MELD3.0_First',
# 'DynaMELD_MELD3.0_First_Second',
# 'DynaMELD_Biological_None',
# 'DynaMELD_Biological_First',
# 'DynaMELD_Biological_First_Second',
# 'DynaMELD_Common_None',
# 'DynaMELD_Common_First',
# 'DynaMELD_Common_First_Second',
# 'MELD', 'MELDNa', 'MELD3.0'
# MELD_POLICY = 'MELD' This option has been
# OUTPUT_DIRECTORY = f'../LivSim_Input/postprocessed/postprocess_result_{MELD_POLICY}'
OUTPUT_DIRECTORY = f'../LivSim_Input/postprocessed/'
INPUT_DIRECTORY = f'../LivSim_Input/preprocessed/'
COHORT_DIR = f"../LivSim_Input/dataset/"
