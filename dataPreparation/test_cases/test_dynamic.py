import pandas as pd

from conftest import load_origin_files, load_removal_files
from dateutil import parser
from livsim_file_util import calculate_MELD
from main import SIMULATOR_START_TIME
import random
import numpy as np


def calculate_time(now_time):
    return round((now_time - SIMULATOR_START_TIME) / np.timedelta64(1, 'Y'), 5)


def contain_check(row, result_df):
    df = pd.merge(row, result_df, on=list(row.columns), how='left', indicator='Exist')
    df['Exist'] = np.where(df.Exist == 'both', True, False)
    return df['Exist'].all()


def test_random_person(load_removal_files, patient, waitlist_matchmeld, status):
    static_removal, dynamic_removal = load_removal_files
    rand_idx = random.randint(0, static_removal.shape[0])
    static_row = static_removal.iloc[rand_idx]
    patient_id = static_row['PX_ID']
    # get corresponding rows in dynamic file
    dynamic_record = dynamic_removal[dynamic_removal['PX_ID'] == patient_id]
    if pd.isnull(static_row['CAN_REM_DT']):
        if pd.isnull(static_row['CAN_DEATH_DT']):
            row_df = pd.DataFrame({'Replication#': [1], 'Patient ID': [patient_id], 'Status Event Time': [calculate_time(static_row['CAN_DEATH_DT'])], 'Dies': [1], 'Removed from Waitlist': [0]})
        else:
            row_df = pd.DataFrame({'Replication#': [1], 'Patient ID': [patient_id], 'Status Event Time': [calculate_time(static_row['CAN_REM_DT'])], 'Dies': [1], 'Removed from Waitlist': [0]})
        assert contain_check(row_df, status)
    else:
        for id, row in dynamic_record.iterrows():
            meld_score = calculate_MELD(row)
            sodium = row['CANHX_SERUM_SODIUM']
            if row['CANHX_STAT_CD'] == 6999 or row['CANHX_STAT_CD'] == 3999:
                inactive_status = 1
            else:
                inactive_status = 0
            row_df = pd.DataFrame({'Replication#': [1], 'Patient ID': [patient_id], 'Status Event Time': [calculate_time(row['CANHX_BEGIN_DT'])], 'Updated Allocation MELD': [meld_score], 'Updated Lab MELD': [meld_score], 'Updated Sodium': [sodium], 'Updated Inactive Status': [inactive_status]})
            assert contain_check(row_df, status)