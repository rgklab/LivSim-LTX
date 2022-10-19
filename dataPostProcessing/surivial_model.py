import pandas as pd
from lifelines import CoxPHFitter

def get_odd_weight_lambda(row):
    gender = row['female_gender']
    weight = row['Gender Weight']
    if gender == 1:
        a = (1-weight)/weight
        return (1-weight)/weight
    else:
        return 1
def get_odd_weight():
    weighted_survival = pd.read_csv('./analysis_data/gender_feature_survival_weighted.csv')
    weighted_survival['Gender Weight'] = weighted_survival.apply(get_odd_weight_lambda, axis=1, result_type='expand')
    # weighted_survival = weighted_survival.dropna()
    weighted_survival.to_csv('./analysis_data/gender_feature_survival_weighted_final.csv', index=False)

def extract_female_coeffiecient(summary_df):
    gender_coefficient = summary_df
    pass


def main():
    # weighted Model
    weighted_survival_df = pd.read_csv('./analysis_data/gender_feature_survival_weighted_final.csv')
    weighted_survival_df = weighted_survival_df.drop(columns=['Patient ID', 'MELD', 'CAN_DGN_4201.0', 'CAN_DGN_4231.0', 'CAN_DGN_4250.0', 'CAN_DGN_4205.0', 'CAN_DGN_4303.0', 'CAN_DGN_4308.0', 'Inactive Status'])
    cph_weighted = CoxPHFitter()
    cph_weighted.fit(weighted_survival_df, duration_col='Patient Event Time', event_col='DDLT', entry_col='Patient Arrival Time', weights_col='Gender Weight', robust=True, show_progress=True, fit_options={'step_size': 0.0001, 'precision': 1e-07, 'max_steps': 5000})
    weighted_summary = cph_weighted.summary
    weighted_summary.to_csv('./models/weighted_cox_summary.csv', index=True)
    cph_weighted.print_summary()
    print('Weighted Concordance Index: ', cph_weighted.concordance_index_)
    survival_df = pd.read_csv('./analysis_data/gender_feature_survival.csv')
    # regular ModeL
    # survival_df = survival_df.drop(columns=['Patient ID', 'Patient Event Time'])
    survival_df = survival_df.drop(columns=['Patient ID', 'MELD', 'CAN_DGN_4201.0', 'CAN_DGN_4231.0', 'CAN_DGN_4250.0', 'CAN_DGN_4205.0', 'CAN_DGN_4303.0', 'CAN_DGN_4308.0', 'Inactive Status'])
    cph_regular = CoxPHFitter()
    cph_regular.fit(survival_df, duration_col='Patient Event Time', event_col='DDLT', entry_col='Patient Arrival Time', robust=True, show_progress=True, fit_options={'step_size': 0.0001, 'precision': 1e-07, 'max_steps': 5000})
    cph_regular.print_summary()

    print('Regular Concordance Index: ', cph_regular.concordance_index_)
    regular_summary = cph_regular.summary
    regular_summary.to_csv('./models/regular_cox_summary.csv', index=True)



if __name__ == '__main__':
    get_odd_weight()
    main()


