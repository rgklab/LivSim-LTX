import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
import math
# first step: generate the independent random variable A,D
MU, SIGMA = 0, 1
EXPLOSURE_NOISE = 1
def variable_set_up():
    # expose
    a = np.random.normal(MU, SIGMA, 10000)
    # confounder
    d = np.random.normal(MU, SIGMA, 10000)
    # mediator expo coefficient = 2 confounder_coefficient = 3
    b = 2 * a - 3 * d + np.random.normal(MU, EXPLOSURE_NOISE)
    # distination expo_coefficient = 1.5 mediator_coefficient=2.3 confounder_coefficient=1.1
    c = 6 * a + 1.1 * d + 2.3 * b + np.random.normal(MU, EXPLOSURE_NOISE)
    return d, a, b, c


# def variable_build_up():
#     input = np.random.normal(MU, SIGMA, 10000)
#     input.reshape(-1, 1)
#     output = 3 * input
#     return input.reshape(-1,1), output.reshape(-1,1)


def apply_odd_ratio(row):
    expo = row['expo']
    weight = row['expo weight']
    if expo == 1:
        return (1 - weight) / weight
    else:
        return 1

def apply_odd_ratio_linear(row, mediator_cof):
    try:
        a = math.exp(mediator_cof * row['expo'] * row['mediator']/math.pow(EXPLOSURE_NOISE/2, 2))
        return 1 / a
    except:
        pass



def predict_on_expo(confounder, expo, mediator):
    regr = LinearRegression(fit_intercept=False)
    features = pd.DataFrame({'expo': expo, 'confounder': confounder, 'mediator': mediator})
    regr.fit(features[['confounder', 'mediator']], features['expo'])

    features['expo weight'] = features.apply(lambda row: apply_odd_ratio_linear(row, regr.coef_[1]), axis=1)
    return features


def get_total_effect(features_with_weight, distination):
    total_model = LinearRegression(fit_intercept=False)
    total_model.fit(features_with_weight[['expo', 'confounder']], distination)
    print('total model: ', total_model.coef_[0])

def get_direct_effect(features_with_weight, distination):
    direct_model = LinearRegression(fit_intercept=False)
    direct_model.fit(features_with_weight[['expo', 'confounder']], distination, sample_weight=features_with_weight['expo weight'])
    print('direct model: ', direct_model.coef_[0])
    pass

def try_out(input, output):
    model = LinearRegression(fit_intercept=False)
    model.fit(input, output)
    print(model.coef_)

if __name__ == '__main__':
    np.random.seed(3)
    confounder, expo, mediator, distination = variable_set_up()
    features_with_weight = predict_on_expo(confounder, expo, mediator)
    get_total_effect(features_with_weight, distination)
    get_direct_effect(features_with_weight, distination)

    # try_out(features_with_weight, distination)
    # input, output = variable_build_up()
    # try_out(input, output)