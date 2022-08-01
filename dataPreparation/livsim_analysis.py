import pandas as pd
import numpy as np
from main import get_constraint_px, load_sample_csv
def get_gender_count():
    patient_df = pd.read_csv('./deepsurv_result/SRTR_Patient.csv')
    waitlist_df = pd.read_csv('./deepsurv_result/SRTR_Waitlist_matchmeld.csv')
    patient_ids =pd.concat([patient_df['Patient ID'], waitlist_df['Patient ID']], axis=0)
    px_dict = get_constraint_px()
    constraint_patient = pd.Series(px_dict['train'] + px_dict['val'])
    patient_ids = patient_ids[patient_ids.isin(constraint_patient)]
    static_file_removal, dynamic_file_removal = load_sample_csv(True)
    death_gender = static_file_removal[['PX_ID', 'CAN_GENDER']]
    death_gender = death_gender[death_gender['PX_ID'].isin(patient_ids)]
    gender_count = death_gender['CAN_GENDER'].value_counts(dropna=False)
    gender_count.to_csv('./post_processing/Total_gender_count.csv', index=True)

if __name__ == '__main__':
    get_gender_count()