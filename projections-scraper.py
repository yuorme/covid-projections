#!/usr/bin/env python
# coding: utf-8

import os
import time
from datetime import datetime, date, timedelta

import pandas as pd
import numpy as np
from pangres import upsert

import requests 
from bs4 import BeautifulSoup

import io
import re
import itertools
import zipfile
from sqlalchemy import create_engine

from column_translater import lanl_to_ihme_translator
from region_abbreviations import us_state_abbrev
from config import app_config
from plot_option_data import csv_dtypes

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

    # LANL uses US instead of United States of America, let's make it match IHME
    df.loc[df.location_name == "US", 'location_name'] = "United States of America"

    #replace negative values caused by the diff crossing over states
    for c in lanl_metrics_diff:
        df[c] = np.where(df[c] < 0, 0, df[c])

    df.columns = [c if 'q' not in c else metric+'_'+c for c in df.columns] #add metric name to lanl metric columns
    df.set_index(lanl_index, inplace=True)
  
    return df

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
    new_ihme_columns = [
        'mobility_composite','total_tests','confirmed_infections',
        'est_infections_mean','est_infections_lower','est_infections_upper',
        'deaths_mean_smoothed','deaths_lower_smoothed','deaths_upper_smoothed',
        'totdea_mean_smoothed','totdea_lower_smoothed','totdea_upper_smoothed',
        #more new columns
        'total_pop', 
        'deaths_mean_p100k_rate', 'deaths_lower_p100k_rate', 'deaths_upper_p100k_rate', 
        'totdea_mean_p100k_rate', 'totdea_lower_p100k_rate', 'totdea_upper_p100k_rate', 
        'deaths_mean_smoothed_p100k_rate', 'deaths_lower_smoothed_p100k_rate', 'deaths_upper_smoothed_p100k_rate', 
        'totdea_mean_smoothed_p100k_rate', 'totdea_lower_smoothed_p100k_rate', 'totdea_upper_smoothed_p100k_rate', 
        'confirmed_infections_p100k_rate', 'est_infections_mean_p100k_rate', 'est_infections_lower_p100k_rate', 
        'est_infections_upper_p100k_rate', 
        'inf_cuml_mean', 'inf_cuml_lower', 'inf_cuml_upper', 
        'sero_pct', 'sero_pctlower', 'sero_pctupper', 
        'seroprev_mean', 'seroprev_upper', 'seroprev_lower',
        #even more new columns
        'deaths_data_type', 'confirmed_infections_data_type', 'est_infections_data_type', 
        'seroprev_data_type', 'observed'
     ]
    ihme.drop(columns=new_ihme_columns, inplace=True)

    #HACK: drop old IHME forecasts to save space
    drop_models = [
        '2020_04_05.05.us','2020-03-25','2020_03_26','2020_03_27','2020_03_29',
        '2020_03_30','2020_03_31.1','2020_04_01.2','2020_04_05.08.all','2020_04_07.06.all',
        '2020_04_09.06','2020_04_12.02'
    ]
    ihme = ihme[~ihme.model_version.isin(drop_models)]
    ihme['model_name'] = 'IHME'

    #concatenate IHME and LANL data
    merged = pd.concat([ihme, lanl], axis=0, ignore_index=True)
    merged.to_csv(os.path.join('data','merged_projections.csv'), index=False)

    print('merged data:', merged.shape)


def create_projections_table():

    print('creating db')
    # create the covid_projections db
    engine = create_engine(app_config['sqlalchemy_database_uri'], echo=False)

    # Make same changes as in the load_projections function
    df = pd.read_csv(os.path.join('data','merged_projections.csv'), nrows=50)
    
    dtypes = [
        'category','str',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'float32','float32','float32',
        'category','category',
        'float32','float32','float32',
        'float32','float32','float32',
    ]

    if len(df.columns) != len(dtypes):
        print(f'len mismatch between df.columns ({len(df.columns)}) and dtypes ({len(dtypes)})')

    pd_dtypes = dict(zip(df.columns, dtypes))

    df = pd.read_csv(os.path.join('data','merged_projections.csv'), dtype=pd_dtypes)
    df = df[df.model_version != '2020_04_05.05.us']

    print(df.info(memory_usage='deep'))
    print(df.columns)

    df['date'] = pd.to_datetime(df['date'])
    df['model_date'] = pd.to_datetime(df['model_version'].str[0:10].str.replace('_','-'))
    df['location_abbr'] = df['location_name'].map(us_state_abbrev)
    # df = df[df['model_date'] > (datetime.today() - timedelta(days=31))] # only loading model versions from the past 31 days
    index_col = ['location_name', 'date', 'model_date', 'model_name']
    df.set_index(index_col,inplace= True)
    df = df[~df.index.duplicated()]
    # drop old table and insert new table
    # df.to_sql(app_config['database_name'], con=engine, if_exists='replace', method='multi', chunksize=1000) #Todo: Do we want to specify data types in the table?
    # 'ALTER TABLE projections ADD PRIMARY KEY (location_name, date, model_date, model_name);'
    # This upsert package requires us to name the index
    # df.index.name = 'index'
    
    print('starting upsert')

    #if we need to do it day by day
    model_dates = df[df.index.get_level_values('model_date') >= '2021-04-01']\
        .index.get_level_values('model_date').unique() #HACK! - hardcoded to do fill
    print(model_dates)
    
    for md in model_dates:
        #upsert by model_date rather than all at once
        dff = df[df.index.get_level_values('model_date') == md] 
        print(f'''
            model_date: {md}, 
            model_names: {dff.index.get_level_values('model_name').unique()} 
            memory: {dff.memory_usage(deep=True).sum()}
        ''')

        upsert(engine=engine,
            df=dff,
            table_name=app_config['database_name'],
            if_row_exists='ignore', chunksize=5000,
            add_new_columns=False,
            create_schema=False,
            adapt_dtype_of_empty_db_columns=False)

if __name__ == "__main__":
    # get_lanl_df()
    # get_ihme_df()
    # merge_projections()
    create_projections_table()
