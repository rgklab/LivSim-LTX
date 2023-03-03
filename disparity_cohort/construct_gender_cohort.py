import pandas as pd
from dateutil import parser
import numpy as np
from dateutil import relativedelta
from dataPostProcessing.get_post_analysis_data import get_static_feature
def load_sas():
    static_file = pd.read_sas('../dataPreparation/SRTR/cand_liin.sas7bdat')
    static_file['CAN_ACTIVATE_DT'] = pd.to_datetime(static_file['CAN_ACTIVATE_DT'])
    static_file['CAN_ABO'] = static_file['CAN_ABO'].str.decode('utf-8')
    static_file['CAN_SOURCE'] = static_file['CAN_SOURCE'].str.decode('utf-8')
    static_file['WL_ORG'] = static_file['WL_ORG'].str.decode('utf-8')
    static_file['CAN_PREV_ABDOM_SURG'] = static_file['CAN_PREV_ABDOM_SURG'].str.decode('utf-8')
    static_file['CAN_GENDER'] = static_file['CAN_GENDER'].str.decode('utf-8')
    static_file['CAN_BACTERIA_PERIT'] = static_file['CAN_BACTERIA_PERIT'].str.decode('utf-8')
    static_file['CAN_ACPT_HCV_POS'] = static_file['CAN_ACPT_HCV_POS'].str.decode('utf-8')
    static_file['CAN_LIFE_SUPPORT'] = static_file['CAN_LIFE_SUPPORT'].str.decode('utf-8')
    static_file['CAN_WORK_INCOME'] = static_file['CAN_WORK_INCOME'].str.decode('utf-8')
    static_file['CAN_TIPSS'] = static_file['CAN_TIPSS'].str.decode('utf-8')
    static_file['CAN_MALIG'] = static_file['CAN_MALIG'].str.decode('utf-8')
    static_file['PX_ID'] = static_file['PX_ID'].astype('int32')

    # removal count
    # status_count = static_file['CAN_REM_DT']
    # nan_count = len(status_count) - status_count.count()
    # non_nan_count = status_count.count()
    # print(f'null count removal {nan_count}')
    # print(f'not null count removal {non_nan_count}')
    # Drop rows if critical columns are NaN
    static_file = static_file[~static_file["CAN_INIT_SRTR_LAB_MELD"].isnull()]
    # age greater than 18
    static_file = static_file[static_file['CAN_AGE_AT_LISTING'] >= 18]
    # organ is liver
    static_file = static_file[static_file['WL_ORG'] == 'LI']
    # remove status 1
    static_file = static_file[~static_file['CAN_INIT_STAT'].isin([6010, 6011, 6012, 3010])]
    # change the user to only contain patient still on waitlist as of 2013-06-18
    static_file = static_file[static_file['CAN_ACTIVATE_DT'] > parser.parse(('2013-06-18'))]
    static_file = static_file[static_file['CAN_ACTIVATE_DT'] < parser.parse(('2018-03-01'))]
    # remove users that death date is not before 2018-03-01 apparently the paper result only consider this time interval for mortality analysis
    dynamic_file = pd.read_sas('../dataPreparation/SRTR/stathist_liin.sas7bdat')
    dynamic_file['CANHX_BEGIN_DT'] = pd.to_datetime(dynamic_file['CANHX_BEGIN_DT'])
    dynamic_file = dynamic_file[dynamic_file['CANHX_BEGIN_DT'] < parser.parse('2018-03-01')]
    # static_file_new = static_file.merge(dynamic_file_user, how='inner', on='PX_ID')
    # static_file_new = static_file_new['PX_ID']
    dynamic_file = dynamic_file[dynamic_file['CANHX_BEGIN_DT'] > parser.parse('2013-06-18')]
    # change the user to only contain patient still on waitlist as of 2013-06-18
    dynamic_file['PX_ID'] = dynamic_file['PX_ID'].astype('int32')


    dynamic_file = dynamic_file[dynamic_file['PX_ID'].isin(static_file['PX_ID'])]
    static_file.to_csv(f'./cand_liin.csv', index=False)
    dynamic_file.to_csv(f'./stathist_liin.csv', index=False)
    return static_file, dynamic_file
# def get_csv_files():
#     static_file = pd.read_csv('./cand_liin.csv')
#     dynamic_file = pd.read_csv('./stathist_liin.csv')
#     static_file['CAN_ACTIVATE_DT'] = pd.to_datetime(static_file['CAN_ACTIVATE_DT'])
#     static_file['CAN_ABO'] = static_file['CAN_ABO'].str.decode('utf-8')
#     static_file['CAN_SOURCE'] = static_file['CAN_SOURCE'].str.decode('utf-8')
#     static_file['WL_ORG'] = static_file['WL_ORG'].str.decode('utf-8')
#     static_file['CAN_PREV_ABDOM_SURG'] = static_file['CAN_PREV_ABDOM_SURG'].str.decode('utf-8')
#     static_file['CAN_GENDER'] = static_file['CAN_GENDER'].str.decode('utf-8')
#     static_file['CAN_BACTERIA_PERIT'] = static_file['CAN_BACTERIA_PERIT'].str.decode('utf-8')
#     static_file['CAN_ACPT_HCV_POS'] = static_file['CAN_ACPT_HCV_POS'].str.decode('utf-8')
#     static_file['CAN_LIFE_SUPPORT'] = static_file['CAN_LIFE_SUPPORT'].str.decode('utf-8')
#     static_file['CAN_WORK_INCOME'] = static_file['CAN_WORK_INCOME'].str.decode('utf-8')
#     static_file['CAN_TIPSS'] = static_file['CAN_TIPSS'].str.decode('utf-8')
#     static_file['CAN_MALIG'] = static_file['CAN_MALIG'].str.decode('utf-8')
#     static_file['PX_ID'] = static_file['PX_ID'].astype('int32')
#     static_file['CAN_DEATH_DT'] = pd.to_datetime(static_file['CAN_DEATH_DT'])
#
#     dynamic_file['CANHX_BEGIN_DT'] = pd.to_datetime(dynamic_file['CANHX_BEGIN_DT'])
#     dynamic_file['CANHX_BEGIN_DT'] = pd.to_datetime(dynamic_file['CANHX_BEGIN_DT'])
#     return static_file, dynamic_file
def get_death_status(row):
    if row['CAN_DEATH_DT'] < parser.parse('2018-03-01'):
        return [1, round((row['CAN_DEATH_DT'] - row['CANHX_BEGIN_DT'])/ np.timedelta64(1,'M'), 5)]
    else:
        return [0, round((parser.parse('2018-03-01') - row['CANHX_BEGIN_DT'])/ np.timedelta64(1,'M'), 5)]
def dead_main():
    # load sas file into csv
    static_file, dynamic_file = load_sas()
    # get static feature needed
    static_useful = get_static_feature(static_file)
    # get gender out
    female_gender = pd.DataFrame({'female': static_file['CAN_GENDER'].map({'F': 1, 'M': 0})})
    static_useful = static_useful.drop(columns=['CAN_GENDER'])
    # exlude diab type of known
    static_useful = static_useful[(static_useful['CAN_DIAB_TY'] != 5) & (static_useful['CAN_DIAB_TY'] != 998)]
    static_useful = pd.concat([static_useful, female_gender], axis=1)
    # process dynamic file
    dynamic_useful = dynamic_file[['PX_ID', 'CANHX_SRTR_LAB_MELD', 'CANHX_REASON_STAT_INACT', 'CANHX_BEGIN_DT']]
    dynamic_useful['Inactive'] = dynamic_useful['CANHX_REASON_STAT_INACT'].notna()
    dynamic_useful['Inactive'] = dynamic_useful['Inactive'].astype(int)
    dynamic_useful = dynamic_useful.drop(columns=['CANHX_REASON_STAT_INACT'])
    gender_feature_df = pd.merge(dynamic_useful, static_useful, how='inner', on='PX_ID')
    gender_feature_df['meld'] = gender_feature_df['CANHX_SRTR_LAB_MELD'] % 100
    gender_feature_df[['death', 'Survival_Time']] = gender_feature_df.apply(get_death_status, axis=1, result_type='expand')
    gender_feature_df = gender_feature_df[gender_feature_df['Survival_Time'] != 0]

    gender_feature_df = gender_feature_df.drop(columns=['PX_ID', 'CANHX_BEGIN_DT', 'CAN_DEATH_DT', 'CANHX_SRTR_LAB_MELD'])
    gender_feature_df = gender_feature_df.dropna()
    gender_feature_df.to_csv('./gender_feature_df_dead.csv', index=False)





if __name__ == '__main__':
    dead_main()
    ###### CANHX_REASON_STAT_INACT
    ####### lab meld