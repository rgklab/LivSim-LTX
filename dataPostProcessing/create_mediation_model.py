import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
import math
# first step: generate the independent random variable A,D
MU, SIGMA = 0, 1
EXPLOSURE_NOISE = 0.2
def variable_set_up():
    # expose
    a = np.random.randint(2, size=10000)
    # confounder
    d = np.random.normal(MU, SIGMA, 10000)
    # mediator expo coefficient = 2 confounder_coefficient = 3
    b = 2 * a + 3 * d
    # distination expo_coefficient = 1.5 mediator_coefficient=2.3 confounder_coefficient=1.1
    c = 1.5 * a + 1.1 * d + 2.3 * b
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
    return 1 / math.exp(mediator_cof * row['expo'] * row['mediator']/EXPLOSURE_NOISE)




def predict_on_expo(confounder, expo, mediator):
    regr = LogisticRegression(fit_intercept=False)
    features = pd.DataFrame({'expo': expo, 'confounder': confounder, 'mediator': mediator})
    regr.fit(features[['confounder', 'mediator']], features['expo'])
    weight = regr.predict_proba(features[['confounder', 'mediator']])
    weight = pd.DataFrame({'expo weight': weight[:, 1]})
    print('logistic regression', regr.coef_)
    features_with_weight = pd.concat([features, weight], axis=1)
    features_with_weight['expo weight'] = features_with_weight.apply(apply_odd_ratio, axis=1)
    return features_with_weight


def get_total_effect(features_with_weight, distination):
    total_model = LinearRegression(fit_intercept=False)
    total_model.fit(features_with_weight[['expo', 'confounder']], distination)
    print('total model: ', total_model.score(features_with_weight[['expo', 'confounder']], distination))

def get_direct_effect(features_with_weight, distination):
    direct_model = LinearRegression(fit_intercept=False)
    direct_model.fit(features_with_weight[['expo', 'confounder']], distination, sample_weight=features_with_weight['expo weight'])

    print('direct model',direct_model.score(features_with_weight[['expo', 'confounder']], distination))
    pass

def try_out(input, output):
    model = LinearRegression(fit_intercept=False)
    model.fit(input, output)
    print(model.coef_)

if __name__ == '__main__':
    confounder, expo, mediator, distination = variable_set_up()
    features_with_weight = predict_on_expo(confounder, expo, mediator)
    get_total_effect(features_with_weight, distination)
    get_direct_effect(features_with_weight, distination)

    # try_out(features_with_weight, distination)
    # input, output = variable_build_up()
    # try_out(input, output)

