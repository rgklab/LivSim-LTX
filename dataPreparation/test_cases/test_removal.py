def test_no_status1(load_removal_files):
    """test there is no status 1 patient in static and dynamic file"""
    static_file, dynamic_file = load_removal_files
    status_1 = static_file['CAN_INIT_STAT'].isin([6010, 6011, 6012, 3010]).any()
    assert not status_1, "There is status 1 in static file after removal"
    status_1 = dynamic_file['CANHX_STAT_CD'].isin([6010, 6011, 6012, 3010]).any()
    assert not status_1, "There is status 1 in dynamic file after removal"


def test_no_hcc(load_removal_files, load_origin_files):
    static_origin, dynamic_origin = load_origin_files
    static_removal, dynamic_removal = load_removal_files
    hcc_patient = static_origin.loc[(static_origin['CAN_DGN'] == 4401) | (static_origin['CAN_DGN2'] == 4401), 'PX_ID']
    assert not hcc_patient.isin(static_removal['PX_ID']).any(), 'There is HCC patient in static file after removal'
    assert not hcc_patient.isin(dynamic_removal['PX_ID']).any(), 'There is HCC patient in dynamic file after removal'

