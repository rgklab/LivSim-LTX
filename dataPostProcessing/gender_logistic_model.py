import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pickle

filename = 'gender_model.sav'
def load_gender_data():
    return pd.read_csv('./analysis_data/gender_feature_final.csv')

def plot_roc_curve(y_test, y_pred_proba):
    fpr, tpr, _ = metrics.roc_curve(y_test, y_pred_proba)
    auc = metrics.roc_auc_score(y_test, y_pred_proba)

    plt.plot(fpr, tpr, label="AUC="+str(auc))
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.legend(loc=4)
    plt.show()

def gender_model():
    """create the gender model"""
    gender_df = load_gender_data()
    x = gender_df.drop(columns=['female_gender', 'Patient ID']) # Features
    logreg = LogisticRegression(solver='lbfgs', max_iter=5000)
    y = gender_df.female_gender # Target Variable
    # x['intercept'] = 1.0
    # logit = sm.Logit(y, x)
    # result = logit.fit(method='bfgs')
    # y_predict = result.predict(x)
    # y_predict.to_csv('./models/predicted_female.csv', index=False)
    logreg.fit(x, y)
    logreg.predict(x)
    y_proba = logreg.predict_proba(x)
    plot_roc_curve(y, y_proba[:, 1])
    gender_prob = pd.DataFrame({'female weight': y_proba[:, 1]})

    gender_prob.to_csv('./models/predicted_female.csv', index=False)
    # x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=16)
    # instantiate the model


def create_prob_with_id():
    gender_df = load_gender_data()
    female_prob = pd.read_csv('./models/gender_female.csv')
    female_prob = pd.DataFrame({'Patient ID': gender_df['Patient ID'], 'female_prob': female_prob['0']})
    female_prob.to_csv('./models/predicted_female.csv', index=False)

def create_weighted_survival_data():
    female_weight = pd.read_csv('./models/predicted_female.csv')
    female_weight.columns = ['Gender Weight']
    survival_data = pd.read_csv('./analysis_data/gender_feature_survival.csv')
    weighted_survival = pd.concat([survival_data, female_weight], axis=1)
    weighted_survival.to_csv('./analysis_data/gender_feature_survival_weighted.csv', index=False)
if __name__ == '__main__':
    gender_model()
    create_weighted_survival_data()
    # create_prob_with_id()