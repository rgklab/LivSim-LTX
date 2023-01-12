import pandas as pd
from dateutil import parser

def load_sas():
    static_file = pd.read_sas('../dataPreparation/SRTR/cand_liin.sas7bdat')
    static_file['CAN_ACTIVATE_DT'] = pd.to_datetime(static_file['CAN_ACTIVATE_DT'])
    static_file['CAN_ABO'] = static_file['CAN_ABO'].str.decode('utf-8')
    static_file['CAN_SOURCE'] = static_file['CAN_SOURCE'].str.decode('utf-8')
    static_file['WL_ORG'] = static_file['WL_ORG'].str.decode('utf-8')
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
    # 


    # dynamic_file = pd.read_sas('./SRTR/stathist_liin.sas7bdat')
    # dynamic_file.to_csv('./experiment/stathist_liin.csv', index=False)
    dynamic_file = pd.read_sas('../dataPreparation/SRTR/stathist_liin.sas7bdat')
    dynamic_file['CANHX_BEGIN_DT'] = pd.to_datetime(dynamic_file['CANHX_BEGIN_DT'])
    dynamic_file_user = dynamic_file[dynamic_file['CANHX_BEGIN_DT'] > parser.parse('2013-06-18')]
    static_file_new = static_file.merge(dynamic_file_user, how='inner', on='PX_ID')
    static_file_new = static_file_new['PX_ID']

    # change the user to only contain patient still on waitlist as of 2013-06-18
    static_file = static_file[static_file['PX_ID'].isin(static_file_new)]
    dynamic_file = dynamic_file[dynamic_file['PX_ID'].isin(static_file_new)]
    # only study until 2018-03-01
    dynamic_file = dynamic_file[dynamic_file['CANHX_BEGIN_DT'] < par]
    static_file.to_csv(f'./cand_liin.csv', index=False)
    dynamic_file.to_csv(f'./stathist_liin.csv', index=False)
    return None, dynamic_file
if __name__ == '__main__':
    load_sas()