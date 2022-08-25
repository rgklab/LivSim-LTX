import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
def load_sas():
    patient_ids = pd.read_csv('./SRTR_Patient.csv')
    patient_ids = patient_ids['Patient ID']
    static_file = pd.read_sas('../dataPreparation/SRTR/cand_liin.sas7bdat')
    static_file['CAN_ABO'] = static_file['CAN_ABO'].str.decode('utf-8')
    static_file['CAN_PREV_ABDOM_SURG'] = static_file['CAN_PREV_ABDOM_SURG'].str.decode('utf-8')
    static_file['CAN_GENDER'] = static_file['CAN_GENDER'].str.decode('utf-8')
    static_file['CAN_BACTERIA_PERIT'] = static_file['CAN_BACTERIA_PERIT'].str.decode('utf-8')
    static_file['PX_ID'] = static_file['PX_ID'].astype('int32')
    static_file_small = static_file[static_file['PX_ID'].isin(patient_ids)]
    static_file_small.to_csv('./analysis_data/cand_liin_small.csv', index=False)

    dynamic_file = pd.read_sas('../dataPreparation/SRTR/stathist_liin.sas7bdat')
    dynamic_file['PX_ID'] = dynamic_file['PX_ID'].astype('int32')
    dynamic_file_small = dynamic_file[dynamic_file['PX_ID'].isin(patient_ids)]

    dynamic_file_small.to_csv('./analysis_data/stathist_liin_small.csv', index=False)
    return None, dynamic_file

def load_sample_csv():
    static_file = pd.read_csv('./analysis_data/cand_liin_small.csv')
    return static_file
def get_race(row):
    race = row['CAN_RACE']
    if race == 8:
        return 'white'
    elif race == 16:
        return 'black'
    else:
        return 'other'

def get_blood_type(row):
    """get the integer blood type in Livsim Format"""
    raw_blood_type = row['CAN_ABO']
    if raw_blood_type in ('A1', 'A', 'A2'):
        blood_type = 'A'
    elif raw_blood_type in ('A1B', 'A2B', 'AB'):
        blood_type = 'AB'
    elif raw_blood_type in 'B':
        blood_type = 'B'
    elif raw_blood_type in 'O':
        blood_type = 'O'
    else:
        blood_type = np.nan
    return blood_type

def get_static_features(row):
    blood_type = get_blood_type(row)
    race = get_blood_type(row)
    return blood_type, race

def get_train_patient(static):
    #get static useful info
    static_useful = static[['PX_ID', 'CAN_ABO', 'CAN_AGE_AT_LISTING', 'CAN_RACE', 'CAN_ARTIFICIAL_LI', 'CAN_ACPT_HCV_POS', 'CAN_LIFE_SUPPORT', 'CAN_WORK_INCOME', 'CAN_TIPSS', 'CAN_PRIMARY_PAY', 'CAN_DGN', 'CAN_EDUCATION', 'CAN_MALIG', 'CAN_VENTILATOR', 'CAN_PREV_PA', 'CAN_PREV_LU', 'CAN_DIAB_TY']]
    static_useful[['CAN_ABO', 'CAN_RACE']] = static_useful.apply(get_static_features, axis=1, result_type='expand')
    a = 5





    # race defined as black, white, others

    pass

if __name__ == '__main__':
    static_file = load_sample_csv()
    get_train_patient(static_file)