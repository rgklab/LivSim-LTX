from config import SIMULATOR_START_TIME, SIMULATOR_END_TIME, INPUT_DIRECTORY, \
    OUTPUT_DIRECTORY, DATA_DIRECTORY, MELD_POLICY
import pandas as pd

dynamic_file = pd.read_pickle(f'{INPUT_DIRECTORY}/yingke_stathist_liin_livsim_2023.pkl')

print(dynamic_file)