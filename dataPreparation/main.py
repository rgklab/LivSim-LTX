# This is a sample Python script.
import os
from dateutil import parser
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from config import SIMULATOR_START_TIME, SIMULATOR_END_TIME, INPUT_DIRECTORY, \
    OUTPUT_DIRECTORY, DATA_DIRECTORY, COHORT_DIR
from utils import vprint

TRANCATE_NUM = 1000
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import numpy as np
from livsim_file_util import get_static_features, get_dynamic_removal_features, create_column_summary, \
    get_dynamic_features, get_blood_type, get_initial_meld

np.random.seed(7777)
def get_constraint_px():
    split_PXIDs = {}
    for pxid_split in ["train", "val", "test"]:
        split_PXIDs[pxid_split] = [*map(
            float,
            open(f"./data_splits/srtr_{pxid_split}_split.txt", "r").readlines())
                                   ]
    return split_PXIDs

def load_raw_donor_sas():
    file = pd.read_sas(f'{DATA_DIRECTORY}/tx_li.sas7bdat')
    file['DON_ABO'] = file['DON_ABO'].str.decode('utf-8')

    file.to_csv(f'{INPUT_DIRECTORY}/tx_li.csv', index=False)
    return file


def load_sas(verbose=0):
    """
    Load static data files and enforce inclusion/exclusion criteria
    and load dynamic data which contains the risks estimated from different models.
    Requirements:
        SRTR_2023_simulator_stathist_liin.pkl is located in LivSim_Input/preprocessed/.
        (This is a version of the stathist_liin data table that includes risk scores
        from each of the models for evaluation).
    """
    vprint("Loading CAND_LIIN from SAS file...", verbose)
    cand_liin = pd.read_sas(f'{DATA_DIRECTORY}/cand_liin.sas7bdat')
    vprint("CAND_LIIN loaded successfully!", verbose)

    vprint("Loading STATHIST_LIIN from pickle file...", verbose)
    stathist_liin = pd.read_pickle(f'{INPUT_DIRECTORY}/SRTR_2023_simulator_stathist_liin.pkl')
    vprint("STATHIST_LIIN loaded successfully!", verbose)

    # stathist_liin = stathist_liin.drop('PERS_ID', axis=1)

    vprint("Loading cohort files...", verbose)
    cohort = set()
    for file_dir in os.listdir(COHORT_DIR):
        f = open(COHORT_DIR + "/" + file_dir, "r")
        for pxid in f:
            cohort.add(float(pxid))
    vprint("Cohort files loaded successfully!", verbose)
    
    cand_liin['CAN_ABO'] = cand_liin['CAN_ABO'].str.decode('utf-8')
    cand_liin['CAN_SOURCE'] = cand_liin['CAN_SOURCE'].str.decode('utf-8')

    
    # Filter by inclusion/exclusion criteria
    cand_liin = cand_liin[cand_liin["PX_ID"].isin(cohort)]
    stathist_liin = stathist_liin[stathist_liin["PX_ID"].isin(cohort)]

    # For patients who have neither a death nor removal date, right-censor these
    # patients and impute their date of censorship with the last observed time
    # for that patient in the data.
    # static_file = static_file[((~static_file["CAN_DEATH_DT"].isnull()) | (~static_file["CAN_REM_DT"].isnull())) &
    #                           (~static_file["CAN_ACTIVATE_DT"].isnull())]

    vprint("Imputing removal dates for candidates with neither death nor removal dates...", verbose)
    for i, row in cand_liin.iterrows():
        curr_pxid = row["PX_ID"]
        # impute death data to too sick to transplant 5 and 13
        if row["CAN_REM_CD"] in [5.0, 13.0]:
            cand_liin.loc[i, "CAN_DEATH_DT"] = row["CAN_REM_DT"]

        if pd.isnull(row["CAN_DEATH_DT"]) and pd.isnull(row["CAN_REM_DT"]):
            # Impute with the last observed time for that patient in the data.
            stathist_liin_pxid = stathist_liin[stathist_liin["PX_ID"] == curr_pxid]
            cand_liin.loc[i, "CAN_REM_DT"] = stathist_liin_pxid["CANHX_BEGIN_DT"].max()
    vprint("Imputed removal dates successfully!", verbose)


    # removal count
    # status_count = static_file['CAN_REM_DT']
    # nan_count = len(status_count) - status_count.count()
    # non_nan_count = status_count.count()
    # print(f'null count removal {nan_count}')
    # print(f'not null count removal {non_nan_count}')
    # Drop rows if critical columns are NaN

    ## TODO -- replace the below with a filtration by our inclusion/exclusion
    ## criteria. (REDUNDANT)
    # cand_liin = cand_liin[~cand_liin["CAN_INIT_SRTR_LAB_MELD"].isnull()]

    # static_file = static_file[((~static_file["CAN_DEATH_DT"].isnull()) | (~static_file["CAN_REM_DT"].isnull())) &
    #                           (~static_file["CAN_ACTIVATE_DT"].isnull())]

    # All patients who have neither a death date or removal date are presumed to
    # still be active on the waitlist. We right-censor these patients and impute
    # their date of censorship with their last observed time in the data.
    # TODO -- Michael do this.
    # cand_liin = cand_liin[(cand_liin["CAN_LIVING_DON_TX"] == 0)] ## TODO -- this should be redundant with our inclusion criteria.

    # ## TODO -- merge the removal feature (HCC and status 1) of load_sample_csv here
    # # Get rid of all Patient with HCC diagnosis and all Patient that dead before the simulator start
    # static_file_hcc = cand_liin[cand_liin['CAN_DGN'].eq(4401) | cand_liin['CAN_DGN2'].eq(4401)]
    # static_file_remove_WL = cand_liin[cand_liin['CAN_REM_DT'] <= SIMULATOR_START_TIME]
    # # Get rid of all Patient with status1 in initial Status and dynamic status
    # # static info
    # static_file_status1 = cand_liin[
    #     cand_liin['CAN_INIT_STAT'].eq(6011) | cand_liin['CAN_INIT_STAT'].eq(6010) | cand_liin['CAN_INIT_STAT'].eq(
    #         6012)]
    # # dynamic info
    # dynamic_file_status1 = stathist_liin[
    #     stathist_liin['CANHX_STAT_CD'].eq(6010) | stathist_liin['CANHX_STAT_CD'].eq(6011) | stathist_liin[
    #         'CANHX_STAT_CD'].eq(6012) | stathist_liin['CANHX_STAT_CD'].eq(3010)]
    # patient_removal = pd.concat([static_file_hcc['PX_ID'], static_file_remove_WL['PX_ID'], static_file_status1['PX_ID'],
    #                              dynamic_file_status1['PX_ID']], ignore_index=True)
    # cand_liin = cand_liin[~cand_liin['PX_ID'].isin(patient_removal)]
    # stathist_liin = stathist_liin[~stathist_liin['PX_ID'].isin(patient_removal)]

    # dynamic_file = pd.read_sas(f'{DATA_DIRECTORY}/stathist_liin.sas7bdat')
    # dynamic_file.to_csv('./experiment/stathist_liin.csv', index=False)


    vprint("Saving CAND_LIIN, STATHIST_LIIN to CSV...", verbose)
        
    cand_liin.to_csv(f'{INPUT_DIRECTORY}/cand_liin.csv', index=False)
    stathist_liin.to_csv(f'{INPUT_DIRECTORY}/SRTR_2023_simulator_stathist_liin.csv', index=False)

    vprint("CAND_LIIN, STATHIST_LIIN saved successfully!", verbose)

    return


# Press the green button in the gutter to run the script.

def load_sample_csv(folder='./experiment'):
    static_file = pd.read_csv(f'{folder}/cand_liin.csv',
                                parse_dates=['CAN_ACTIVATE_DT', 'CAN_LAST_ACT_STAT_DT', 'CAN_REM_DT', 'CAN_DEATH_DT',
                                            'REC_TX_DT'])
    dynamic_file = pd.read_csv(f'{folder}/SRTR_2023_simulator_stathist_liin.csv', parse_dates=['CANHX_BEGIN_DT', 'CANHX_END_DT'])

    # impute DSA info
    static_file = static_file[static_file['CAN_LISTING_CTR_ID'].notna()] #TODO: fix this
    return static_file, dynamic_file


def create_donors(organ_file):
    """
    create Donor.txt
    """
    donor_df = organ_file[['DON_OPO_CTR_ID', 'REC_TX_DT', 'DON_ABO', 'DONOR_ID']]
    donor_df.insert(1, 'DSA ID2', donor_df['DON_OPO_CTR_ID'])
    donor_df.columns = ['DSA ID1', 'DSA ID2', 'Donor Arrival Time', 'Donor ABO Blood Type', 'Organ ID']
    donor_df.insert(0, 'Replication#', 1)
    donor_df['Donor Arrival Time'] = round(
        (donor_df['Donor Arrival Time'] - SIMULATOR_START_TIME) / np.timedelta64(1, 'Y'), 5)
    # select only the arrival time that after simulation start
    donor_df = donor_df[(donor_df['Donor Arrival Time'] >= 0) & (
                donor_df['Donor Arrival Time'] <= relativedelta(SIMULATOR_END_TIME, SIMULATOR_START_TIME).years)]

    donor_df['Donor ABO Blood Type'] = donor_df['Donor ABO Blood Type'].apply(get_blood_type)
    donor_df = donor_df.dropna()
    donor_df = donor_df.drop_duplicates(subset=['Organ ID'])
    # donor_df = donor_df[donor_df['DSA ID1'] < 709]
    donor_df = donor_df.sample(frac=0.552)
    donor_df = donor_df.sort_values(by='Donor Arrival Time')
    donor_df.to_csv(f'./{OUTPUT_RESULT_DIRECTORY}/SRTR_Donors.csv', index=False)


def fill_static_info(livsim_file, static_file):
    # assign patient id
    livsim_file['Patient ID'] = static_file['PX_ID'].astype('int32')
    livsim_file['Patient Arrival Time'] = static_file['CAN_ACTIVATE_DT']
    # skip the MELD Score for now
    # row specific data
    # print(static_file.apply(
    #     get_static_features, axis=1, result_type='expand').values)
    data_to_fill = np.array(static_file.apply(
        get_static_features, axis=1, result_type='expand').values)
    livsim_file["Patient ABO Blood Type"] = data_to_fill[:,0]
    livsim_file["Patient HCC Status"] = data_to_fill[:, 1]
    livsim_file["Status1"] = data_to_fill[:, 2]
    livsim_file["Inactive"] = data_to_fill[:, 3]
    
    # # raise
    # data_to_fill = pd.DataFrame(static_file.apply(
    #     get_static_features, axis=1, result_type='expand').values,
    #     columns = ['Patient ABO Blood Type', 'Patient HCC Status', 'Status1', 'Inactive'])
    # livsim_file[['Patient ABO Blood Type', 'Patient HCC Status', 'Status1', 'Inactive']] = data_to_fill
    # Sodium score
    static_dsa = static_file[['PX_ID', 'CAN_LISTING_CTR_ID']]
    livsim_file = livsim_file.merge(static_dsa, how='left', left_on='Patient ID', right_on='PX_ID')
    livsim_file['DSA ID1'] = livsim_file['CAN_LISTING_CTR_ID']
    livsim_file['DSA ID2'] = livsim_file['CAN_LISTING_CTR_ID']
    livsim_file = livsim_file.drop(columns=['PX_ID', 'CAN_LISTING_CTR_ID'])
    # drop blood type Z
    livsim_file = livsim_file[livsim_file['Patient ABO Blood Type'].notnull()]
    # sort livsim_file by arrival time

    return livsim_file


def create_patient(static_file, dynamic_file, score: str = 'MELD'):
    """ create patient.txt and Waitlist_match_MELD.txt one is before the simulation start, one is after the simulation start"""
    patient_df = pd.DataFrame(
        {'Replication#': 1, 'Patient ID': [], 'DSA ID1': [], 'DSA ID2': [], 'Patient Arrival Time': [],
         'Patient ABO Blood Type': [],
         'Patient Allocation MELD': [], 'Patient Lab MELD': [], 'Patient HCC Status': [], 'Status1': [],
         'Sodium Score': [], 'Inactive': []})
    waitlist_df = pd.DataFrame(
        {'Patient ID': [], 'DSA ID1': [], 'Patient Arrival Time': [], 'Patient ABO Blood Type': [],
         'Patient Starting MELD': [], 'Patient HCC Status': [], 'Status1': [],
         'Sodium Score': [], 'DSA ID2': [], 'Inactive': []})
    # decode blood type

    # arrival Time
    static_file['CAN_ACTIVATE_DT'] = round(
        (static_file['CAN_ACTIVATE_DT'] - SIMULATOR_START_TIME) / np.timedelta64(1, 'Y'), 5)
    # patients arrive after simulation start
    static_file_after = static_file[static_file['CAN_ACTIVATE_DT'] >= 0]
    # patients arrive before simulation start
    static_file_before = static_file[static_file['CAN_ACTIVATE_DT'] < 0]
    patient_df = fill_static_info(patient_df, static_file_after)
    patient_df['Replication#'] = 1
    waitlist_df = fill_static_info(waitlist_df, static_file_before)
    # no reason to cap DSA
    # patient_df = patient_df[patient_df['DSA ID1'] < 709]
    # waitlist_df = waitlist_df[waitlist_df['DSA ID1'] < 709]
    static_file = static_file.drop(columns=['CAN_GENDER'])
    dynamic_allocation = dynamic_file.merge(static_file, on='PX_ID', how='inner',  suffixes=('_x', ''))
    patient_meld = dynamic_allocation.groupby(by=['PX_ID']).apply(get_initial_meld, score=score)
    # patient_meld = patient_meld.reset_index().dropna()
    patient_meld = patient_meld.reset_index()
    patient_meld.rename(columns={'PX_ID': 'Patient ID'}, inplace=True)
    patient_df = patient_df.merge(patient_meld, on='Patient ID', how='inner')
    patient_df['Patient Allocation MELD'] = patient_df['patient_meld']
    patient_df['Patient Lab MELD'] = patient_df['patient_meld']
    patient_df['Sodium Score'] = patient_df['patient_sodium']
    patient_df['Inactive'] = patient_df['inactive']
    patient_df = patient_df.drop(columns=['patient_meld', 'patient_sodium', 'inactive'])
    waitlist_df = waitlist_df.merge(patient_meld, on="Patient ID", how="inner")
    waitlist_df['Patient Starting MELD'] = waitlist_df['patient_meld']
    waitlist_df['Sodium Score'] = waitlist_df['patient_sodium']
    waitlist_df['Inactive'] = waitlist_df['inactive']
    waitlist_df = waitlist_df.drop(columns=['patient_meld', 'patient_sodium', 'inactive'])
    waitlist_df = waitlist_df.sort_values(by='Patient Arrival Time')
    patient_df = patient_df[
        patient_df['Patient Arrival Time'] <= relativedelta(SIMULATOR_END_TIME, SIMULATOR_START_TIME).years]
    patient_df = patient_df.sort_values(by='Patient Arrival Time')
    patient_df = patient_df.drop_duplicates()
    waitlist_df = waitlist_df.drop_duplicates()
    # px_dict = get_constraint_px()
    # constraint_patient = pd.Series(px_dict['train'] + px_dict['val'])
    # patient_df = patient_df[patient_df['Patient ID'].isin(constraint_patient)]
    # waitlist_df = waitlist_df[waitlist_df['Patient ID'].isin(constraint_patient)]
    patient_df.to_csv(f'./{OUTPUT_RESULT_DIRECTORY}/SRTR_Patient.csv', index=False)
    waitlist_df.to_csv(f'./{OUTPUT_RESULT_DIRECTORY}/SRTR_Waitlist_matchmeld.csv', index=False)
    return patient_df, waitlist_df

def create_status(dynamic_file, static_file, available_patient, score: str = 'MELD'):
    """create the dynamic file for the status.txt"""
    ## TODO - make too-sick to transplant patients as mortality events
    # get rid of end date before simulation start
    dynamic_file['CANHX_BEGIN_DT'][dynamic_file['CANHX_BEGIN_DT'] < SIMULATOR_START_TIME] = SIMULATOR_START_TIME
    
    # handle death and removal
    rem_death_df = static_file[['PX_ID', 'CAN_REM_DT', 'CAN_DEATH_DT', 'REC_TX_DT', "CAN_REM_CD"]]
    rem_death_df = rem_death_df[rem_death_df['CAN_REM_DT'].notnull()]
    death_df = rem_death_df[rem_death_df['CAN_REM_DT'] == rem_death_df['CAN_DEATH_DT']]
    rem_df = rem_death_df[(rem_death_df['CAN_REM_DT'] != rem_death_df['CAN_DEATH_DT']) & (
                rem_death_df['CAN_REM_DT'] != rem_death_df['REC_TX_DT'])]

    # death event
    death_result = death_df.apply(lambda row: get_dynamic_removal_features(row, True), axis=1, result_type='expand')
    # status_df = status_df.append(), ignore_index=True)
    # removal event
    removal_result = rem_df.apply(lambda row: get_dynamic_removal_features(row, False), axis=1, result_type='expand')
    # Meld score calculation
    normal_df = dynamic_file[dynamic_file['CAN_REM_DT'] != dynamic_file['CANHX_BEGIN_DT']]
    normal_result = normal_df.apply(lambda row: get_dynamic_features(row, score), axis=1, result_type='expand')
    status_df = pd.concat([death_result, removal_result, normal_result], ignore_index=True)
    status_df.columns = ['Replication#', 'Patient ID', 'Status Event Time', 'Dies', 'Removed from Waitlist',
                         'Updated Allocation MELD', 'Updated Lab MELD', 'Updated Sodium', 'DSA ID1', 'DSA ID2',
                         'Updated Inactive Status']

    status_df['Status Event Time'] = round(
        (status_df['Status Event Time'] - SIMULATOR_START_TIME) / np.timedelta64(1, 'Y'), 5)
    static_dsa = static_file[['PX_ID', 'CAN_LISTING_CTR_ID']]
    status_df = status_df.merge(static_dsa, how='inner', left_on='Patient ID', right_on='PX_ID')
    status_df['DSA ID1'] = status_df['CAN_LISTING_CTR_ID']
    status_df['DSA ID2'] = status_df['CAN_LISTING_CTR_ID']
    status_df = status_df.drop(columns=['PX_ID', 'CAN_LISTING_CTR_ID'])
    # status_df = status_df[status_df['DSA ID1'] < 709]
    status_df = status_df[
        status_df['Status Event Time'] <= relativedelta(SIMULATOR_END_TIME, SIMULATOR_START_TIME).years]

    status_df = status_df[status_df['Patient ID'].isin(available_patient)]
    status_df = status_df.sort_values(by='Status Event Time')
    status_df = status_df.drop_duplicates()
    status_df.to_csv(f'./{OUTPUT_RESULT_DIRECTORY}/SRTR_Status.csv', index=False)


def post_process(score: str = 'MELD'):
    """do post process analysis after LivSim run"""
    results_path = f'../LivSim_Output/{score}/results/'
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    static_file_removal, dynamic_file_removal = load_sample_csv(folder=INPUT_DIRECTORY)

    deathID = pd.read_csv(f'../LivSim_Output/{score}/RawOutput_IDdeaths.csv')
    death_gender = static_file_removal[['PX_ID', 'CAN_GENDER']]
    death_gender  = death_gender[death_gender['PX_ID'].isin(deathID['Death Patient ID'])]
    gender_count = death_gender['CAN_GENDER'].value_counts(dropna=False)
    gender_count.to_csv(f'{results_path}/new_SRTR_gender_count.csv', index=True)

    static_file_removal = static_file_removal[static_file_removal['CAN_DEATH_DT'] > SIMULATOR_START_TIME]['CAN_GENDER']
    total_gender_count = static_file_removal.value_counts(dropna=False)
    total_gender_count = total_gender_count.apply(lambda row: round(row*0.85))

    total_gender_count.to_csv(f'{results_path}/total_death_gender_count.csv', index=False)

def main(score: str = "MELD"):
    # static_file, dynamic_file = load_sas()
    static_file_removal, dynamic_file_removal = load_sample_csv(folder=INPUT_DIRECTORY)
    dynamic_file_removal = dynamic_file_removal[dynamic_file_removal['CANHX_END_DT'] > SIMULATOR_START_TIME]
    # check for existence of output directory
    global OUTPUT_RESULT_DIRECTORY
    OUTPUT_RESULT_DIRECTORY = OUTPUT_DIRECTORY+'/'+score
    if not os.path.exists(OUTPUT_RESULT_DIRECTORY):
        os.makedirs(OUTPUT_RESULT_DIRECTORY)
    patient_df, waitlist_df = create_patient(static_file_removal, dynamic_file_removal, score)
    available_patient = pd.concat([patient_df['Patient ID'], waitlist_df['Patient ID']], axis=0)
    create_status(dynamic_file_removal, static_file_removal, available_patient, score)
    create_geography_parnter()
    # load_raw_donor_sas()  # call only on the first run
    tx_li = pd.read_csv(f'./{INPUT_DIRECTORY}/tx_li.csv', parse_dates=['REC_TX_DT'])
    create_donors(tx_li)


def create_geography_parnter():
    """create Input_Geography.txt, Input_SPartners.txt"""

    # matrix = np.zeros((709, 709), dtype=np.int8)
    matrix = np.zeros((867, 867), dtype=np.int8)
    np.savetxt(f'./{OUTPUT_RESULT_DIRECTORY}/SRTR_Input_Geography.txt', matrix, fmt='%.0f\n')
    np.savetxt(f'./{OUTPUT_RESULT_DIRECTORY}/SRTR_Input_SPartners.txt', matrix, fmt='%.0f\n')

    pass


# abondoned used ids for inclusion/exclusion criteria
# def preprocess_files(static_file, dynamic_file):
#     """remove HCC diagnosis and status 1 patient"""
#     # Get rid of all Patient with HCC diagnosis and all Patient that dead before the simulator start
#     static_file_hcc = static_file[static_file['CAN_DGN'].eq(4401) | static_file['CAN_DGN2'].eq(4401)]
#     static_file_remove_WL = static_file[static_file['CAN_REM_DT'] <= SIMULATOR_START_TIME]
#     # Get rid of all Patient with status1 in initial Status and dynamic status
#     # static info
#     static_file_status1 = static_file[
#         static_file['CAN_INIT_STAT'].eq(6011) | static_file['CAN_INIT_STAT'].eq(6010) | static_file['CAN_INIT_STAT'].eq(
#             6012)]
#     # dynamic info
#     dynamic_file_status1 = dynamic_file[
#         dynamic_file['CANHX_STAT_CD'].eq(6010) | dynamic_file['CANHX_STAT_CD'].eq(6011) | dynamic_file[
#             'CANHX_STAT_CD'].eq(6012) | dynamic_file['CANHX_STAT_CD'].eq(3010)]
#     patient_removal = pd.concat([static_file_hcc['PX_ID'], static_file_remove_WL['PX_ID'], static_file_status1['PX_ID'],
#                                  dynamic_file_status1['PX_ID']], ignore_index=True)
#     static_file_removal = static_file[~static_file['PX_ID'].isin(patient_removal)]
#     dynamic_file_removal = dynamic_file[~dynamic_file['PX_ID'].isin(patient_removal)]
#     dynamic_file_removal.to_csv(f'./{INPUT_DIRECTORY}/stathist_liin_with_risk_score_removal.csv', index=False)
#     static_file_removal.to_csv(f'./{INPUT_DIRECTORY}/cand_linn_removal.csv', index=False)

#     return static_file_removal, dynamic_file_removal


if __name__ == '__main__':
    # print(f'output_directory is {OUTPUT_DIRECTORY}')
    # print(f'scoring is {MELD_POLICY}')
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
