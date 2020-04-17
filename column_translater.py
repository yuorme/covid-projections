#!/usr/bin/env python
# coding: utf-8

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

    