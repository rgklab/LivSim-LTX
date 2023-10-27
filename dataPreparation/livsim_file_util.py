import pandas as pd
import numpy as np
import csv
from dateutil import parser

# from config import MELD_POLICY, SIMULATOR_START_TIME
from config import SIMULATOR_START_TIME
import random


def calculate_MELD(row, score: str = 'MELD'):
    """
    calculate based on policy selected
    """
    # if MELD_POLICY.lower() == 'regular':
    #     return calculate_MELD_regular(row)
    # elif MELD_POLICY.lower() == 'sodium':
    #     return calculate_MELD_na(row)
    # elif MELD_POLICY.lower() == '30':
    #     return calculate_MELD_30(row)
    # elif MELD_POLICY.lower() == 'random':
    #     return calculate_MELD_random()
    # elif MELD_POLICY.lower() == 'deepsurv':
    #     return row['risk']
    # else:
    #     raise Exception('no policy set')

    try:
        return row[score]
    except:
        print(row.columns)
        raise Exception('Set policy does not exist in stathist_liin_with_risk_score!')


def calculate_MELD_random():
    return random.randint(0, 41)


def calculate_MELD_regular(row):
    bilirubin = row["CANHX_BILI"]
    INR = row["CANHX_INR"]
    creatinine = row["CANHX_SERUM_CREAT"]
    meld_calculated = np.round(
        3.78 * np.log(np.clip(bilirubin, 1, None)) +
        11.2 * np.log(np.clip(INR, 1, None)) +
        9.57 * np.log(np.clip(creatinine, 1, 4)) +
        6.43
    )
    return np.round(np.clip(meld_calculated, 6, 40))


def calculate_MELD_na(row):
    # MELD + 1.32 x (137 - Na) - [0.033 x MELD*(137 - Na)]
    sodium = row["CANHX_SERUM_SODIUM"]
    meldna_calculated = calculate_MELD_regular(row) + 1.32 * (137 - sodium) - (
                0.033 * calculate_MELD_regular(row) * (137 - sodium))
    return np.round(np.clip(meldna_calculated, 6, 40))


def calculate_MELD_30(row):
    bilirubin = np.clip(row["CANHX_BILI"], 1, 3)
    female = 1 if row["CAN_GENDER"] == b'F' else 0
    INR = np.clip(row["CANHX_INR"], 1, None)
    creatinine = np.clip(row["CANHX_SERUM_CREAT"], 1, None)
    sodium = np.clip(row["CANHX_SERUM_SODIUM"], 125, 137)
    albumin = row["CANHX_ALBUMIN"]

    return np.round(
        1.33 * female + \
        (4.56 * np.log(bilirubin)) + \
        (0.82 * (137 - sodium)) - \
        (0.24 * (137 - sodium) * np.log(bilirubin)) + \
        (9.09 * np.log(INR)) + \
        (11.14 * np.log(creatinine)) + \
        (1.85 * (3.5 - albumin)) - \
        (1.83 * (3.5 - albumin) * np.log(creatinine)) + \
        6
    )


def get_dynamic_removal_features(row, is_death):
    patient_id = row['PX_ID']
    dsa = np.nan
    if is_death:
        dies = 1
        removed = 0
        status_event_time = row['CAN_DEATH_DT']
    else:
        dies = 0
        removed = 1
        status_event_time = row['CAN_REM_DT']
    return 1, patient_id, status_event_time, dies, removed, np.nan, np.nan, np.nan, dsa, dsa, np.nan


def get_blood_type(raw_blood_type):
    """get the integer blood type in Livsim Format"""
    if raw_blood_type in ('A1', 'A', 'A2'):
        blood_type = 0
    elif raw_blood_type in ('A1B', 'A2B', 'AB'):
        blood_type = 1
    elif raw_blood_type in 'B':
        blood_type = 2
    elif raw_blood_type in 'O':
        blood_type = 3
    else:
        blood_type = np.nan
    return blood_type


def get_static_features(row):
    # blood type
    raw_blood_type = row['CAN_ABO']
    blood_type = get_blood_type(raw_blood_type)
    # hcc status
    hcc_status = 0
    # status1
    status1 = 0
    # Inactive
    meld_score = np.nan
    if row['CAN_INIT_STAT'] == 6999 or row['CAN_INIT_STAT'] == 1999 or row['CAN_INIT_STAT'] == 2999 or row[
        'CAN_INIT_STAT'] == 3999 or row['CAN_INIT_STAT'] == 4999 or row['CAN_INIT_STAT'] == 5999:
        inactive = 1
    else:
        inactive = 0

    return blood_type, hcc_status, status1, inactive


def split_CONSTAT():
    "create a csv file that represent CONSTAT"
    dict_ = {'Value': [], 'Description': []}
    with open('CONSTAT.txt') as f:
        for line in f:
            line_lst = line.split()
            value = int(line_lst[0])
            describe = ' '.join(line_lst[2:])
            dict_['Value'].append(value)
            dict_['Description'].append(describe)
            a = 5
    constat_df = pd.DataFrame(dict_)
    constat_df.to_csv('CONSTAT.csv', index=False)


def create_column_summary(active_col, column_name):
    """return the csv summary of that column"""
    status_count = active_col.value_counts(dropna=False)
    status_count = status_count.to_frame()
    status_count = status_count.reset_index(level=0)
    status_count.columns = ['Value', 'Count']

    constat = pd.read_csv('CONSTAT.csv')
    final_df = constat.merge(status_count, how='right')
    final_df = final_df.sort_values(by='Count', ascending=False)
    final_df.to_csv(f'{column_name}_description.csv', index=False)


def get_dynamic_features(row, score: str = 'MELD'):
    meld_score = calculate_MELD(row, score)

    patient_id = row['PX_ID']
    dsa = np.nan
    status_event_time = row['CANHX_BEGIN_DT']
    sodium = row['CANHX_SERUM_SODIUM']
    inactive_status = 1 if int(row['CANHX_STAT_CD']) in (6999, 1999, 2999, 4999, 5999, 3999) else 0
    return 1, patient_id, status_event_time, 0, 0, meld_score, meld_score, sodium, dsa, dsa, inactive_status


def get_initial_meld(patient_group, score: str = 'MELD'):
    # patient_group = patient_group[]
    patient_group = patient_group[((patient_group['CANHX_BEGIN_DT'] <= SIMULATOR_START_TIME) & (
            patient_group['CANHX_END_DT'] >= SIMULATOR_START_TIME)) | (
                                          (patient_group['CAN_ACTIVATE_DT'] > 0) & (
                                          ((patient_group[
                                                'CANHX_BEGIN_DT'] - SIMULATOR_START_TIME) / np.timedelta64(1,
                                                                                                           'Y')) <=
                                          patient_group[
                                              'CAN_ACTIVATE_DT']) & (((patient_group[
                                                                           'CANHX_END_DT'] - SIMULATOR_START_TIME) / np.timedelta64(
                                      1, 'Y')) >= patient_group[
                                                                         'CAN_ACTIVATE_DT']))]
    if patient_group.shape[0] == 0:
        return pd.Series({'patient_meld': np.nan, 'patient_sodium': np.nan, 'inactive': np.nan})
    else:
        patient_group = patient_group.sort_values(by='CANHX_BEGIN_DT', ascending=False)
        initial_row = patient_group.iloc[0]
        meld_score = calculate_MELD(initial_row, score)
        inactive_status = 1 if int(initial_row['CANHX_STAT_CD']) in (6999, 1999, 2999, 4999, 5999, 3999) else 0
        return pd.Series({'patient_meld': meld_score, 'patient_sodium': initial_row['CANHX_SERUM_SODIUM'],
                          'inactive': inactive_status})


if __name__ == '__main__':
    # static_file = pd.read_csv('./experiment/cand_liin.csv')
    # status_count = static_file['CAN_SOURCE'].value_counts(dropna=False)
    # status_count.to_csv('can_source_count.csv')
    institution = pd.read_sas('./SRTR/institution.sas7bdat', encoding='cp1252')

    institution.to_csv('./experiment/institution.csv')
