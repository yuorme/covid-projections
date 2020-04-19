import pandas as pd
import numpy as np
import datetime
import os
# from plotnine import *


def get_model_version(model_version_subdir, y=2020):
    date_string = model_version_subdir.replace('/', '').replace('Projection_', '')
    model_version_string = datetime.datetime.strptime(date_string + str(y), '%B%d%Y').strftime('%Y-%m-%d')
    return model_version_string


# def plot_metric_by_date(df, metric):
    # metric_by_date = df.groupby(['date'], as_index=False)[metric].sum().sort_values(
    #     ['date']).reset_index(drop=True)
    # metric_by_date['x'] = np.arange(len(metric_by_date))
    # p = (ggplot(metric_by_date, aes('x', metric)) + geom_line())
    # return p


def get_projection_df_for_model_type(model_type, model_version_subdir, latest_projection_dir, quant_convention_dict, naming_convention_dict, compiled_df):
    model_fs = [f for f in os.listdir(latest_projection_dir) if '.csv' in f and model_type in f]
    bed_fs = [f for f in model_fs if 'bed_' in f]
    projection_fs = [f for f in model_fs if 'Projection_' in f]
    if len(bed_fs) != 1 or len(projection_fs) != 1:
        print('model_type {mt} not found'.format(mt=model_type))
        return None
    bed_f = bed_fs[0]
    projection_f = projection_fs[0]

    bed_df = pd.read_csv(latest_projection_dir + '/' + bed_f, encoding = "ISO-8859-1")
    projection_df = pd.read_csv(latest_projection_dir + '/' + projection_f, encoding = "ISO-8859-1")
    # bed_df = pd.read_csv(latest_projection_dir + '/' + bed_f)
    # projection_df = pd.read_csv(latest_projection_dir + '/' + projection_f)

    bed_df['county'] = bed_df['county'].astype(str)
    bed_df['Date'] = bed_df['Date'].astype(str)

    projection_df['county'] = projection_df['county'].astype(str)
    projection_df['Date'] = projection_df['Date'].astype(str)

    proj_df_size_premerge = projection_df.shape[0]
    projection_df = projection_df.merge(bed_df)
    proj_df_size_postmerge = projection_df.shape[0]
    if proj_df_size_premerge != proj_df_size_postmerge:
        print('proj_df_size_premerge: {}'.format(proj_df_size_premerge))
        print('proj_df_size_postmerge: {}'.format(proj_df_size_postmerge))
        print('bed_df size:{}'.format(bed_df.shape[0]))
        print('Bad merge. Skipping.')
        return None

    cols_to_remove = sorted(set([item for sublist in 
        [['{m}_{q}'.format(m=m, q=q) for q in ['25', '75']] for m in ['report', 'total', 'hosp_need', 'ICU_need', 'vent_need', 'death']]
    for item in sublist] + [c for c in projection_df if 'total_' in c]))

    projection_df = projection_df.drop(cols_to_remove, axis=1)

    projection_df['state'] = projection_df['county'].str[-2:].copy()

    projection_df['date'] = pd.to_datetime(projection_df['Date'], infer_datetime_format=True).dt.strftime('%Y-%m-%d')

    projection_df['model_version'] = get_model_version(model_version_subdir)
    # plot_metric_by_date(projection_df, 'death_50')

    # cc_death_by_date = projection_df[projection_df['county'] == 'Cook County IL'].copy()
    # plot_metric_by_date(cc_death_by_date, 'death_50')

    # plot_metric_by_date(projection_df, 'death_50')

    projection_df['location_name'] = projection_df['county']

    rename_dict = {}
    for nc_k in naming_convention_dict.keys():
        for qc_k in quant_convention_dict.keys():
            rename_dict['{nc}_{qc}'.format(nc=nc_k, qc=qc_k)] = '{nc}_{qc}'.format(
                nc=naming_convention_dict[nc_k], qc=quant_convention_dict[qc_k])

    projection_df = projection_df.rename(columns=rename_dict)
    projection_df = projection_df[[c for c in compiled_df.columns if c in projection_df.columns] + ['fips', 'state']]
    return projection_df


def get_cu_df():
    naming_convention_dict = {
            'ICU_need': 'ICUbed',
            'death': 'totdea',
            'hosp_need': 'allbed',
            'vent_need': 'InvVen'}

    quant_convention_dict = {
        '50': 'mean',
        '2.5': 'lower',
        '97.5': 'upper'}

    print('''Assumptions:
        Assuming upper and lower are 2.5th and 97.5th quantiles respectively. (5 and 95 are not in the data.)
        Ignoring the ICUcapacity and cdc_hosp subdirectory data.
        The following fields assumed to be equivalent:''')
    print('    {}'.format(naming_convention_dict))

    cu_dir = 'data/cu_shaman/'
    cu_dir_original_format = '{}original_format/'.format(cu_dir)

    compiled_df = pd.read_csv('data/ihme_compiled.csv')

    all_projection_dfs = []
    model_version_subdirs = [f for f in os.listdir(cu_dir_original_format) if 'Projection_' in f and '_March13' not in f] # March13 ignored because model format is not equivalent
    for model in ['nointerv', '80contact', '75contact', '70contact', '60contact', '50contact']:
        print(model)
        for model_version_subdir in model_version_subdirs:
            print(model_version_subdir)
            
            # cu_subdirs = os.listdir(cu_dir_original_format)
            latest_projection_dir = cu_dir_original_format + model_version_subdir
            # sub_dirs = [f for f in os.listdir(latest_projection_dir) if not os.path.isfile(latest_projection_dir + f)]
            # print('sub_directories: {}'.format(sub_dirs))
            projection_df = get_projection_df_for_model_type(model, model_version_subdir, latest_projection_dir, quant_convention_dict, naming_convention_dict, compiled_df)
            if projection_df is None:
                continue
            projection_df['model'] = 'CU_shamanlab_' + model
            all_projection_dfs.append(projection_df)

            m = projection_df['model'].iloc[0]
            mv = projection_df['model_version'].iloc[0]

            projection_df.to_csv('{d}{m}_{mv}.csv'.format(d=cu_dir, m=m, mv=mv))
            
    # complete_projection_df = pd.concat(all_projection_dfs)
    # complete_projection_df.to_csv('complete_projection_df.csv', index=False)


def main():
    get_cu_df()


if __name__ == '__main__':
    main()