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

NYTIMES_STATE_URL = ('https://github.com/nytimes/covid-19-data/raw/master/us-states.csv')

def fetch_df(url):
    """Fetches a Pandas DataFrame from a remote source"""
    r = requests.get(url)
    return pd.read_csv(io.BytesIO(r.content))


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

def get_lanl_df(metric='deaths', min_date='2020-04-04'):
    '''
    download lanl projections and compiles into one csv file
    returns: None
    '''
    
    lanl_dates = get_date_list(min_date)
    
    df_list = []

    for date in lanl_dates:
        
        url = f'https://covid-19.bsvgateway.org/forecast/us/files/{date}/{metric}/{date}_{metric}_quantiles_us.csv'
        r = requests.get(url)
        
        if r.ok:
            data = r.content.decode('utf8')
            df = pd.read_csv(io.StringIO(data))
            df_list.append(df)
            print(f'lanl scraped:{date}')
        else:
            print(f'lanl no data:{date}')
       
        time.sleep(0.2) #pause between requests
        
    #merge and process data
    if len(df_list) > 0:
        df = pd.concat(df_list)
        df.columns = [c.replace('.','') for c in df.columns] #remove periods in quantile colnames
        df.to_csv(os.path.join('data','lanl_compiled.csv'), index=False)
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
        df = pd.concat(df_list).drop(columns=['V1','Unnamed: 0','location']) #drop problematic columns
        df['location_name'] = np.where(df['location_name'] == 'US', 'United States of America', df['location_name'])
        df.to_csv(os.path.join('data','ihme_compiled.csv'), index=False)

def get_nytimes_df():
    print('processing: NY Times case data.')

    df = fetch_df(NYTIMES_STATE_URL)

    # Add 'daily_deaths' column. Drops first date of data.
    df['dt'] = pd.to_datetime(df['date'])
    df['prev_dt'] = df['dt'] - pd.to_timedelta(1, unit='d')
    df_merged = df.merge(df[['state', 'dt', 'deaths']],
                     left_on=['state', 'prev_dt'],
                     right_on=['state', 'dt'],
                     suffixes=('', '_y'))
    df_merged['daily_deaths'] = df_merged['deaths'] - df_merged['deaths_y']
    df = df_merged.drop(columns=['dt', 'prev_dt', 'dt_y', 'deaths_y'])

    # Add USA totals
    df_us = df.groupby('date')[['cases', 'deaths', 'daily_deaths']].sum().reset_index()
    df_us['state'] = 'United States of America'
    df_us['fips'] = 0
    df = pd.concat([df, df_us])

    # Rename state to location_name
    df = df.rename(columns={'state': 'location_name'})

    df.to_csv(os.path.join('data', 'nytimes_cases.csv'))

if __name__ == "__main__":
    get_lanl_df()
    get_ihme_df()
    get_nytimes_df()
