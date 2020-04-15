# Generates human readable labels for IHME data column names
# Adapted on definitions provided by the IHME in their readme.txt

ihme_column_translator = {
    # mean
    'allbed_mean': 'All Beds Used (Mean)',
    'ICUbed_mean': 'ICU Beds Used (Mean)',
    'InvVen_mean': 'Ventilators Used (Mean)',
    'deaths_mean': 'Daily Deaths (Mean)',
    'admis_mean': 'Hospital Admissions (Mean)',
    'newICU_mean': 'New ICU Patients (Mean)',
    'totdea_mean': 'Cumulative Deaths (Mean)',
    'bedover_mean': 'All Beds Shortage (Mean)',
    'icuover_mean': 'ICU Beds Shortage (Mean)',
    # lower
    'allbed_lower': 'All Beds Used (Lower)',
    'ICUbed_lower': 'ICU Beds Used (Lower)',
    'InvVen_lower': 'Ventilators Used (Lower)',
    'deaths_lower': 'Daily Deaths (Lower)',
    'admis_lower': 'Hospital Admissions (Lower)',
    'newICU_lower': 'New ICU Patients (Lower)',
    'totdea_lower': 'Cumulative Deaths (Lower)',
    'bedover_lower': 'All Beds Shortage (Lower)',
    'icuover_lower': 'ICU Beds Shortage (Lower)',
    # upper
    'allbed_upper': 'All Beds Used (Upper)',
    'ICUbed_upper': 'ICU Beds Used (Upper)',
    'InvVen_upper': 'Ventilators Used (Upper)',
    'deaths_upper': 'Daily Deaths (Upper)',
    'admis_upper': 'Hospital Admissions (Upper)',
    'newICU_upper': 'New ICU Patients (Upper)',
    'totdea_upper': 'Cumulative Deaths (Upper)',
    'bedover_upper': 'All Beds Shortage (Upper)',
    'icuover_upper': 'ICU Beds Shortage (Upper)',
}

imhe_to_covidtracking = {
    # mean
    'allbed_mean': 'hospitalizedCurrently',
    'ICUbed_mean': 'inIcuCurrently',
    'InvVen_mean': 'onVentilatorCurrently',
    'deaths_mean': 'deathIncrease',
    'admis_mean': 'hospitalizedIncrease',
    'newICU_mean': 'inIcuIncrease',
    'totdea_mean': 'death',
    'bedover_mean': None,
    'icuover_mean': None,
    # lower
    'allbed_lower': 'hospitalizedCurrently',
    'ICUbed_lower': 'inIcuCurrently',
    'InvVen_lower': 'onVentilatorCurrently',
    'deaths_lower': 'deathIncrease',
    'admis_lower': 'hospitalizedIncrease',
    'newICU_lower': 'inIcuIncrease',
    'totdea_lower': 'death',
    'bedover_lower': None,
    'icuover_lower': None,
    # upper
    'allbed_upper': 'hospitalizedCurrently',
    'ICUbed_upper': 'inIcuCurrently',
    'InvVen_upper': 'onVentilatorCurrently',
    'deaths_upper': 'deathIncrease',
    'admis_upper': 'hospitalizedIncrease',
    'newICU_upper': 'inIcuIncrease',
    'totdea_upper': 'death',
    'bedover_upper': None,
    'icuover_upper': None,
}