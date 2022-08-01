import pandas as pd
import pytest
from main import load_sample_csv
@pytest.fixture
def load_origin_files():
    static, dynamic = load_sample_csv(False, '../experiment')
    return static, dynamic

@pytest.fixture
def load_removal_files():
    static, dynamic = load_sample_csv(True, '../experiment')
    return static, dynamic
@pytest.fixture
def patient():
    patient = pd.read_csv('../experiment/SRTR_Patient.csv', parse_dates=['Patient Arrival Time'])
    return patient

@pytest.fixture
def waitlist_matchmeld():
    waitlist = pd.read_csv('../experiment/SRTR_Waitlist_matchmeld.csv', parse_dates=['Patient Arrival Time'])
    return waitlist

@pytest.fixture
def status():
    status = pd.read_csv('../experiment/SRTR_Status.csv', parse_dates=['Status Event Time'])
    status = status.astype({'Status Event Time': float, 'Patient ID': int, 'Dies': int, 'Removed from Waitlist': int, 'Updated Allocation MELD': float,'Updated Lab MELD': float,'Updated Sodium': float,'Updated Inactive Status': int}, errors='ignore')
    return status