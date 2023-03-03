import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from dataPreparation.config import SIMULATOR_START_TIME, SIMULATOR_END_TIME
def get_srtr_tx():
    """get the srtr transplant date"""
    candi_small = pd.read_csv('./analysis_data/cand_liin_small.csv')
    patient_transplant_dt = candi_small[['PX_ID','REC_TX_DT']]
    pass
def load_sas():
    patient_ids = pd.read_csv('./analysis_data/SRTR_Patient.csv')
    patient_ids = patient_ids['Patient ID']
    static_file = pd.read_sas('../dataPreparation/SRTR/cand_liin.sas7bdat')
    static_file['CAN_ABO'] = static_file['CAN_ABO'].str.decode('utf-8')
    static_file['CAN_PREV_ABDOM_SURG'] = static_file['CAN_PREV_ABDOM_SURG'].str.decode('utf-8')
    static_file['CAN_GENDER'] = static_file['CAN_GENDER'].str.decode('utf-8')
    static_file['CAN_BACTERIA_PERIT'] = static_file['CAN_BACTERIA_PERIT'].str.decode('utf-8')
    static_file['CAN_ACPT_HCV_POS'] = static_file['CAN_ACPT_HCV_POS'].str.decode('utf-8')
    static_file['CAN_LIFE_SUPPORT'] = static_file['CAN_LIFE_SUPPORT'].str.decode('utf-8')
    static_file['CAN_WORK_INCOME'] = static_file['CAN_WORK_INCOME'].str.decode('utf-8')
    static_file['CAN_TIPSS'] = static_file['CAN_TIPSS'].str.decode('utf-8')
    static_file['CAN_MALIG'] = static_file['CAN_MALIG'].str.decode('utf-8')
    static_file['PX_ID'] = static_file['PX_ID'].astype('int32')
    static_file_small = static_file[static_file['PX_ID'].isin(patient_ids)]
    static_file_small.to_csv('./analysis_data/cand_liin_small.csv', index=False)

    dynamic_file = pd.read_sas('../dataPreparation/SRTR/stathist_liin.sas7bdat')
    dynamic_file['PX_ID'] = dynamic_file['PX_ID'].astype('int32')
    dynamic_file_small = dynamic_file[dynamic_file['PX_ID'].isin(patient_ids)]

    dynamic_file_small.to_csv('./analysis_data/stathist_liin_small.csv', index=False)
    return None, dynamic_file


def load_static_csv():
    static_file = pd.read_csv('./analysis_data/cand_liin_small.csv')

    return static_file


def get_race(row):
    race = row['CAN_RACE']
    if race == 8:
        return 0  # white
    elif race == 16:
        return 1 # black
    else:
        return 2 # other


def get_blood_type(row):
    """get the integer blood type in Livsim Format"""
    raw_blood_type = row['CAN_ABO']
    if raw_blood_type in ('A1', 'A', 'A2'):
        blood_type = 0 #'A'
    elif raw_blood_type in ('A1B', 'A2B', 'AB'):
        blood_type = 1 #'AB'
    elif raw_blood_type in 'B':
        blood_type = 2 #'B'
    elif raw_blood_type in 'O':
        blood_type = 3 #'O'
    else:
        blood_type = np.nan
    return blood_type

def get_yes_no(value):
    if value == 'Y':
        return 1
    else:
        return 0

def get_static_row_features(row):
    blood_type = get_blood_type(row)
    race = get_race(row)

    return blood_type, race, get_yes_no(row['CAN_PREV_ABDOM_SURG']), get_yes_no(row['CAN_BACTERIA_PERIT']), \
           get_yes_no(row['CAN_LIFE_SUPPORT']), get_yes_no(row['CAN_WORK_INCOME']), get_yes_no(row['CAN_TIPSS']), \
           get_yes_no(row['CAN_MALIG'])


def get_static_feature(static):
    # get static useful info exclude decease origin for now.
    static_useful = static[
        ['PX_ID', 'CAN_ABO', 'CAN_PREV_ABDOM_SURG', 'CAN_BACTERIA_PERIT', 'CAN_AGE_AT_LISTING', 'CAN_RACE',
         'CAN_LIFE_SUPPORT', 'CAN_WORK_INCOME', 'CAN_TIPSS', 'CAN_PRIMARY_PAY', 'CAN_EDUCATION', 'CAN_MALIG',
         'CAN_VENTILATOR', 'CAN_PREV_PA', 'CAN_PREV_LU', 'CAN_DIAB_TY', 'CAN_GENDER', 'CAN_DEATH_DT', 'CAN_DGN']]
    static_useful[['CAN_ABO', 'CAN_RACE', 'CAN_PREV_ABDOM_SURG', 'CAN_BACTERIA_PERIT', 'CAN_LIFE_SUPPORT', 'CAN_WORK_INCOME', 'CAN_TIPSS', 'CAN_MALIG']] = static_useful.apply(get_static_row_features, axis=1, result_type='expand')
    # static_useful.to_csv('./analysis_data/cand_liin_useful.csv', index=False)
    return static_useful

def get_srtr_transplant():
    pass

def get_dynamic_features():
    patient_df = pd.read_csv('./analysis_data/SRTR_Patient.csv')
    patient_df = patient_df[['Patient ID', 'Patient Allocation MELD', 'Inactive', 'Patient Arrival Time']]
    patient_df.columns = range(4)
    status_df = pd.read_csv('./analysis_data/SRTR_Status.csv')
    status_df = status_df[['Patient ID', 'Updated Allocation MELD', 'Updated Inactive Status', 'Status Event Time']]
    status_df.columns = range(4)
    waitlist_df = pd.read_csv('./analysis_data/SRTR_Waitlist_matchmeld.csv')
    waitlist_df = waitlist_df[['Patient ID', 'Patient Starting MELD', 'Inactive', 'Patient Arrival Time']]
    waitlist_df.columns = range(4)
    patient_meld = status_df
    transplant_df = pd.read_csv('./analysis_data/DeepsurvSRTR_RawOutput_TxID.csv')
    transplant_df = transplant_df[['Transplant Patient ID', 'Allocation MELD', 'Inactive', 'Transplant Time']]
    patient_meld.columns = ['Patient ID', 'MELD', 'Inactive Status', 'Patient Event Time']
    combined_df = pd.merge(patient_meld, transplant_df, left_on='Patient ID', right_on='Transplant Patient ID', how='inner')
    combined_df = combined_df[combined_df['Patient Event Time'] < combined_df['Transplant Time']]
    combined_df = combined_df[['Patient ID', 'MELD', 'Inactive Status', 'Patient Event Time']]
    combined_df['DDLT'] = 0
    transplant_df['DDLT'] = 1
    transplant_df.columns = ['Patient ID', 'MELD', 'Inactive Status', 'Patient Event Time', 'DDLT']
    patient_meld = pd.concat([combined_df, transplant_df])
    arrival_df = pd.concat([waitlist_df, patient_df])
    arrival_df = arrival_df[[0, 3]]
    arrival_df.columns = ['Patient ID', 'Patient Arrival Time']
    patient_meld = pd.merge(patient_meld, arrival_df, on='Patient ID')
    patient_meld = patient_meld.sort_values(by=['Patient Event Time'])
    patient_meld = patient_meld[patient_meld['Patient Event Time'] > patient_meld['Patient Arrival Time']]

    patient_meld.to_csv('./analysis_data/dynamic_feature.csv', index=False)


def get_combined_features():
    patient_meld = pd.read_csv('./analysis_data/dynamic_feature.csv')
    cand_liin_useful = pd.read_csv('./analysis_data/cand_liin_useful.csv')
    gender_feature_df = pd.merge(patient_meld, cand_liin_useful, how='inner', left_on='Patient ID', right_on='PX_ID')
    gender_feature_df = gender_feature_df.drop(columns=['PX_ID'])
    gender_feature_df = gender_feature_df.dropna()
    gender_feature_df.to_csv('./analysis_data/gender_feature_df.csv', index=False)


def get_dummy_feature(gender_feature, feature):
    return pd.get_dummies(gender_feature[feature], drop_first=True, prefix=feature)


def create_dummy():
    """get dummy variable """
    gender_feature = pd.read_csv('./analysis_data/gender_feature_df.csv')
    feature_dfs = [get_dummy_feature(gender_feature, feature) for feature in ['CAN_ABO', 'CAN_RACE', 'CAN_ACPT_HCV_POS',
                                                                              'CAN_LIFE_SUPPORT',
                                                                              'CAN_WORK_INCOME', 'CAN_TIPSS',
                                                                              'CAN_PRIMARY_PAY',
                                                                              'CAN_DGN', 'CAN_EDUCATION', 'CAN_MALIG', 'CAN_DIAB_TY'
                                                                              ]]
    female_gender = pd.DataFrame({'female_gender': gender_feature['CAN_GENDER'].map({'F': 1, 'M': 0})})


    gender_feature_2 = gender_feature.drop(['CAN_ABO', 'CAN_RACE', 'CAN_ACPT_HCV_POS',
                                      'CAN_LIFE_SUPPORT',
                                      'CAN_WORK_INCOME', 'CAN_TIPSS', 'CAN_PRIMARY_PAY',
                                      'CAN_DGN', 'CAN_EDUCATION', 'CAN_MALIG', 'CAN_DIAB_TY', 'CAN_GENDER', 'Patient Event Time', 'DDLT', 'Patient Arrival Time'], axis=1)
    gender_survival = gender_feature.drop([
        'CAN_ABO', 'CAN_RACE', 'CAN_ACPT_HCV_POS',
        'CAN_LIFE_SUPPORT',
        'CAN_WORK_INCOME', 'CAN_TIPSS', 'CAN_PRIMARY_PAY',
        'CAN_DGN', 'CAN_EDUCATION', 'CAN_MALIG', 'CAN_DIAB_TY', 'CAN_GENDER'
    ], axis=1)
    feature_dfs_final = pd.concat([gender_feature_2] + feature_dfs + [female_gender], axis=1)
    survival_dfs = pd.concat([gender_survival] + feature_dfs + [female_gender], axis=1)
    feature_dfs_final.to_csv('./analysis_data/gender_feature_final.csv', index=False)
    survival_dfs.to_csv('./analysis_data/gender_feature_survival.csv', index=False)

def normalize_columns(df, column_names):
    """use z score to normalize """
    for column_name in column_names:
        df[column_name] = (df[column_name] - df[column_name].mean())/df[column_name].std()

def final_preprocessing():
    """normalize non-categorical column use z-score and get rid of CAN_ARTIFICIAL_LI', 'CAN_PREV_PA', 'CAN_PREV_LU',
    'CAN_DGN_4315.0', 'CAN_DGN_4520.0' for having very low variance"""
    gender_feature_df = pd.read_csv('./analysis_data/gender_feature_final.csv')
    gender_feature_survival = pd.read_csv('./analysis_data/gender_feature_survival.csv')
    # get rid of the normalizing for now
    # normalize_columns(gender_feature_survival, ['MELD', 'CAN_AGE_AT_LISTING'])
    # normalize_columns(gender_feature_df, ['MELD', 'CAN_AGE_AT_LISTING'])
    gender_feature_df = gender_feature_df.drop(columns=['Inactive Status'])
    gender_feature_survival = gender_feature_survival.drop(columns=['Inactive Status'])
    gender_feature_df.to_csv('./analysis_data/gender_feature_final.csv', index=False)
    gender_feature_survival.to_csv('./analysis_data/gender_feature_survival.csv', index=False)



if __name__ == '__main__':
    load_sas()
    static_file = load_static_csv()
    get_static_feature(static_file)
    get_dynamic_features()
    get_combined_features()
    create_dummy()
    # final_preprocessing()
