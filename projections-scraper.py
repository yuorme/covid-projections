#!/usr/bin/env python
# coding: utf-8

import os
import time
from datetime import date, timedelta

import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup

import io
import re
import itertools
import zipfile

from column_translater import lanl_to_ihme_translator

def get_date_list(min_date):
    '''
    generates list of dates from today backwards to min_date
    '''
    date_list = []
    day = date.today()
    while str(day) != min_date:
        day_str = str(day)
        date_list.append(day_str)
        day = day - timedelta(days=1)

    return date_list

def get_lanl_df(min_date='2020-04-04'):
    '''
    download lanl projections and compiles into one csv file
    returns: None
    '''

    lanl_dates = get_date_list(min_date)
    lanl_metrics = ['deaths', 'confirmed']

    for metric in lanl_metrics:

        df_list = []

        for date in lanl_dates:

            for suffix in ['','_website']: #LANL added _website suffix to files in their 2020-04-26 update

                for scope in ['us','global']:

                    url = f'https://covid-19.bsvgateway.org/forecast/{scope}/files/{date}/{metric}/{date}_{metric}_quantiles_{scope}{suffix}.csv'
                    r = requests.get(url)

                    if r.ok:
                        data = r.content.decode('utf8')
                        df = pd.read_csv(io.StringIO(data))
                        df['metric'] = metric
                        df.drop(columns=['simple_state','simple_countries'], inplace=True, errors='ignore')
                        df.rename(columns={'state':'location_name','countries':'location_name'}, inplace=True)
                        df_list.append(df)
                        print(f'lanl scraped {metric}: {date} {scope} {suffix}')
                    else:
                        print('no metrics for:', date, scope, suffix)

                    time.sleep(0.2) #pause between requests

        #merge and process data
        if len(df_list) > 0:
            df = pd.concat(df_list)
            df.columns = [c.replace('.','') for c in df.columns] #remove periods in quantile colnames
            df.to_csv(os.path.join('data', f'lanl_{metric}_compiled.csv'), index=False)
        else:
            print('error: dataframe list is empty')

def get_ihme_filelist():
    '''
    parse IHME downloads page for links to zip files
    returns: list of zip file urls
    '''

    url = 'http://www.healthdata.org/covid/data-downloads'

    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')

    file_list = [p.find_all('a') for p in soup.find_all('p') if p.find_all('a', href=re.compile('ihmecovid19storage')) != []]
    file_list = list(itertools.chain.from_iterable(file_list)) #join list of lists
    file_list = [f['href'] for f in file_list] #get file url
    file_list.append(file_list.pop(0)) #insert latest list at end to ensure chronological order
    file_list = ['http://www.healthdata.org' + f if '/sites/default/' in f else f for f in file_list] #append base url for files hosted on IHME website

    return file_list

def get_ihme_df():
    '''
    download ihme projections and compiles into one csv file
    returns: None
    '''

    df_list = []

    file_list = get_ihme_filelist()

    for f in file_list:

        r = requests.get(f, stream=True)
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        zf.extractall(os.path.join('data','ihme_archive'))

        model_folder = zf.namelist()[0][:-1] #drop trailing slash

        if '/' in model_folder:
            model_folder = model_folder.split('/')[0]

        if model_folder != 'ihme-covid19': #parse from zip file folder name
            model_version = model_folder
        else: #parse from url folder name
            model_version = f.split('/')[-2]

        print('processing:', model_version)

        df = [pd.read_csv(zf.open(file)) for file in zf.namelist() if file.endswith('.csv')][0]
        df.rename(columns={'date_reported':'date'}, inplace=True) #fix inconsistent column names
        df['model_version'] = model_version
     #     df = pd.read_csv(z.open('hospitalization_all_locs_corrected.csv'))
        df_list.append(df)

        time.sleep(0.2)

    if len(df_list) > 0:
        df = pd.concat(df_list).drop(columns=['V1','Unnamed: 0','location','location_id'], errors='ignore') #drop problematic columns if they exist in the df
        df['location_name'] = np.where(df['location_name'] == 'US', 'United States of America', df['location_name'])
        df.to_csv(os.path.join('data','ihme_compiled.csv'), index=False)

    return df

def process_lanl_compiled(metric):
    '''
    process lanl datasets for merge
    '''
    df = pd.read_csv(os.path.join('data',f'lanl_{metric}_compiled.csv'))

    lanl_keep_cols = ['dates','location_name','q025','q50','q975','fcst_date'] #TODO: using 95% CI (97.5/2.5). Is this consistent with IHME?
    lanl_index = ['fcst_date','location_name','dates']
    lanl_metrics = [c for c in lanl_keep_cols if 'q' == c[0]]
    lanl_metrics_diff = [c+'_diff' for c in lanl_metrics]
    df = df[lanl_keep_cols]

    df = df.sort_values(lanl_index).reset_index(drop=True) #sort to allow diff
    df[lanl_metrics_diff] =  df.sort_values(lanl_index)[lanl_metrics].diff()

    #replace negative values caused by the diff crossing over states
    for c in lanl_metrics_diff:
        df[c] = np.where(df[c] < 0, 0, df[c])

    df.columns = [c if 'q' not in c else metric+'_'+c for c in df.columns] #add metric name to lanl metric columns
    df.set_index(lanl_index, inplace=True)

    return df

def get_yyg_filelist(date = '2020-04-12'):
    '''
    parse YYG downloads page for links to csv files
    returns: list of paths to csv files
    '''

    us_url = f'https://github.com/youyanggu/covid19_projections/tree/master/projections/{date}'
    global_url = f'https://github.com/youyanggu/covid19_projections/tree/master/projections/{date}/global'

    urls = [us_url, global_url]
    patterns = {global_url : f'(?<={date}/).+_ALL.csv(?=\")', us_url : f'(?<={date}/)US_.+.csv(?=\")'}

    file_list = []
    for url in urls:
        r = requests.get(url)
        t = requests.get(url).text
        pattern = patterns[url]
        filenames = re.findall(pattern, t)
        file_list += filenames
    return file_list

def get_yyg_df(min_date = '2020-04-01'):
    '''
    download yyg projections and compiles into one csv file
    returns: None
    '''

    yyg_dates = get_date_list(min_date)
    files = get_yyg_filelist()

    df_list = []
    for date in yyg_dates: #remove limitation here
        for f in files:
            url = f'https://raw.githubusercontent.com/youyanggu/covid19_projections/master/projections/{date}/{f}'
            r = requests.get(url)

            if r.ok:
                print('Pulling: ', f, ' for ', date)
                data = r.content.decode('utf8')
                df = pd.read_csv(io.StringIO(data))
                df.rename(columns=yyg_to_ihme_translator, inplace=True) #rename columns w imported dict
                df['model_version'] = date
                if 'US' in f:
                    df['location_name'] = us_state_abbrev[f[3:5]] #lookup state abbrevation and convert to full name
                else:
                    df['location_name'] = f.split('/')[1].split('_')[0]
                #location names here
                df_list.append(df)
                print(f'yyg scraped : {date}')
            else:
                print('Cannot pull: ', f, ' for ', date)

            time.sleep(0.2) #pause between requests

    if len(df_list) > 0:
        df = pd.concat(df_list)
        # df.columns = [c.replace('.','') for c in df.columns] #remove periods in quantile colnames
        #df.to_csv('yyg_test_compiled.csv', index=False)
        return df
    else:
        print('error: dataframe list is empty')

def merge_projections():
    '''
    process and merge IHME / LANL data
    '''

    print('merging projection data...')

    #load and merge LANL deaths and confirmed case data
    lanl_con = process_lanl_compiled('confirmed')
    lanl_dea = process_lanl_compiled('deaths')

    lanl = lanl_dea.merge(lanl_con, right_index=True, left_index=True).reset_index()
    lanl.rename(columns=lanl_to_ihme_translator, inplace=True) #convert to IHME column names
    lanl['model_name'] = 'LANL'

    #load IHME data
    ihme = pd.read_csv(os.path.join('data','ihme_compiled.csv'))

    #HACK: drop new IHME columns
    ihme.drop(columns=['mobility_data_type','total_tests_data_type'], inplace=True)
    new_ihme_columns = ['mobility_composite','total_tests','confirmed_infections','est_infections_mean','est_infections_lower','est_infections_upper']
    ihme.drop(columns=new_ihme_columns, inplace=True)

    ihme = ihme[ihme.model_version != '2020_04_05.05.us']
    ihme['model_name'] = 'IHME'

    #concatenate IHME and LANL data
    merged = pd.concat([ihme, lanl], axis=0, ignore_index=True)
    merged.to_csv(os.path.join('data','merged_projections.csv'), index=False)

    print('merged data:', merged.shape)

if __name__ == "__main__":
    get_lanl_df()
    get_ihme_df()
    merge_projections()
