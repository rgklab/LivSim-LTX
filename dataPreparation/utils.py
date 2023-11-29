import numpy as np

def vprint(out, verbose):
    """
    Prints output to console depending on the value taken by a "verbose" flag.
    """
    if verbose:
        print(out)
    else:
        pass

def calculate_MELD(row, raw=False):
    """
    """
    bilirubin = row["CANHX_BILI"]
    INR = row["CANHX_INR"]
    creatinine = row["CANHX_SERUM_CREAT"]
    meld_calculated = np.round(
        3.78 * np.log(np.clip(bilirubin, 1, None)) + 
        11.2 * np.log(np.clip(INR, 1, None)) +
        9.57 * np.log(np.clip(creatinine, 1, 4)) + 
        6.43
    )
    if raw:
        return meld_calculated
    return np.round(np.clip(meld_calculated, 6, 40))

def calculate_MELD_na(row, raw=False):
    # MELD + 1.32 x (137 - Na) - [0.033 x MELD*(137 - Na)]
    sodium = row["CANHX_SERUM_SODIUM"]
    meldna_calculated = calculate_MELD(row) + 1.32 * (137 - sodium) - (0.033 * calculate_MELD(row) * (137 - sodium))
    if raw:
        return meldna_calculated
    return np.round(np.clip(meldna_calculated, 6, 40))

def calculate_MELD_30(row, round=True, raw=False):
    # female = 1 if row["CAN_GENDER"] == b'F' else 0 # This is already encoded!!
    female = row["CAN_GENDER"]
    bilirubin = np.clip(row["CANHX_BILI"], 1, None)
    INR = np.clip(row["CANHX_INR"], 1, None)
    creatinine = np.clip(row["CANHX_SERUM_CREAT"], 1, None)
    sodium = np.clip(row["CANHX_SERUM_SODIUM"], 125, 137)
    albumin = np.clip(row["CANHX_ALBUMIN"], 1.5, 3.5) # THIS IS A CHANGE THAT WILL AFFECT THE RESULTS

    inner = (1.33*female) + \
            (4.56 * np.log(bilirubin)) + \
            (0.82 * (137-sodium)) - \
            (0.24 * (137-sodium)*np.log(bilirubin)) + \
            (9.09 * np.log(INR)) + \
            (11.14 * np.log(creatinine)) + \
            (1.85 * (3.5 - albumin)) - \
            (1.83 * (3.5 - albumin) * np.log(creatinine)) + \
            6
    if raw:
        return inner
    if round:
        return np.round(np.clip(inner, 6, 40))
    return inner