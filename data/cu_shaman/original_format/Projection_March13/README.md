# Projection of the COVID-19 outbreak in US

We calibrated a county-level metapopulation model to incidence data reported during Feb 21 2020 to Mar 13 2020 in continental US, and used the calibrated model to project the course of COVID-19 outbreaks in the US. We also simulated the effects of hypothetical social distancing and travel restrictions. The model description and methods are summerized in the technical report (PDF).

# Projection output

Projection_nointervention.csv, Projection_75%transmissibility.csv, Projection_50%transmissibility.csv, and Projection_5%mobility.csv report projections of county-level daily confirmed cases and total infections (median, IQR and 95% CI) within 180 days of Feb 21 2020 for four scenarios: 1) no intervention, 2) a 25% reduction of contact rate, 3) a 50% reduction of contact rate, and 4) a 95% reduction of cross-county mobility. Results were obtained by running 100 simulations of each scenario.

Here, daily confrimed cases are confirmed infections reported by surveillance system. There is a delay between getting infected and reported. Total infections are the number of people transitioning from exposed to documented/undocumented infected. Only part of total infections will be reported in the surveillance system.

Parameters were estimated by fitting the metapopulation model to county-level incidence data from Feb 21 2020 to Mar 13 2020, provided by the New York Times. Parameters could change over time after Mar 13 2020 due to shifting control measures. In addition, we assume a uniform set of parameters for all US counties, which does not reflect the heterogeneity of contact patterns in space. We also did not consider the possible seasonality of SARS-CoV-2.

Summary of columns

county: county names
fips: the fips code for each county
Date: date
report_median, report_2.5, report_25, report_75, report_97.5: the median, 2.5% percentile, 25% percentile, 75% percentile, 97.5% percentile of daily confirmed (documented) case
total_median, total_2.5, total_25, total_75, total_97.5: the median, 2.5% percentile, 25% percentile, 75% percentile, 97.5% percentile of daily infected (both documented and undocumented) case

# Movies

To evaluate the impact of control measures, we examined how daily confirmed cases within 6 months of February 21 2020 were modulated by percent reductions of the contact rate (effected by isolation, quarantine, telecommuting, school closure, etc.) and travel restrictions (effected by reducing commuting and travel among counties). The reductions of contact rates disrupt normal mixing within metapopulation locations, whereas the travel restrictions impact mixing between locations. In particular, we ran model simulations with no intervention (nointervention.mp4), a 25% reduction of contact rate (75%transmissibility.mp4), a 50% reduction of contact rate (50%transmissibility.mp4) and a 95% reduction of cross-county mobility (5%mobility.mp4).

# Citation

Please cite: Sen Pei, Jeffrey Shaman, Initial Simulation of SARS-CoV2 Spread and Intervention Effects in the Continental US. medRxiv.doi: https://doi.org/10.1101/2020.03.21.20040303

New York Times article: https://www.nytimes.com/interactive/2020/03/20/us/coronavirus-model-us-outbreak.html
