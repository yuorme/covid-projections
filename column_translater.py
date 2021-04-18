#!/usr/bin/env python
# coding: utf-8

# Generates human readable labels for IHME data column names
# Adapted on definitions provided by the IHME in their readme.txt

column_translator = {
    'date': 'Date',
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
    # lanl specific columns in ihme format
    'confirmed_lower':'Cumulative Cases (Lower)',
    'confirmed_mean':'Cumulative Cases (Mean)',
    'confirmed_upper':'Cumulative Cases (Upper)',
    'daily_confirmed_lower':'Daily Cases (Lower)',
    'daily_confirmed_mean':'Daily Cases (Mean)',
    'daily_confirmed_upper':'Daily Cases (Upper)',
    # Smoothed
    'deaths_mean_smoothed': 'Smoothed Daily Deaths (Mean)',
    'deaths_lower_smoothed': 'Smoothed Daily Deaths (Lower)',
    'deaths_upper_smoothed': 'Smoothed Daily Deaths (Upper)',
    'totdea_mean_smoothed': 'Smoothed Cumulative Deaths (Mean)',
    'totdea_lower_smoothed': 'Smoothed Cumulative Deaths (Lower)',
    'totdea_upper_smoothed': 'Smoothed Cumulative Deaths (Upper)',
}

lanl_to_ihme_translator = {
    'dates':'date',
    'state':'location_name',
    'fcst_date':'model_version',
    #cumulative stats
    'deaths_q05':'totdea_lower',
    'deaths_q50':'totdea_mean',
    'deaths_q95':'totdea_upper',
    'confirmed_q05':'confirmed_lower',
    'confirmed_q50':'confirmed_mean',
    'confirmed_q95':'confirmed_upper',
    #calculated daily stats
    'deaths_q05_diff':'deaths_lower',
    'deaths_q50_diff':'deaths_mean',
    'deaths_q95_diff':'deaths_upper',
    'confirmed_q05_diff':'daily_confirmed_lower',
    'confirmed_q50_diff':'daily_confirmed_mean',
    'confirmed_q95_diff':'daily_confirmed_upper',
}

    