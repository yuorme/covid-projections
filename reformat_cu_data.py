import urllib
from bs4 import BeautifulSoup
import pandas as pd
import datetime


def get_tbody(soup):
    tbodys = soup.findAll('tbody')
    if len(tbodys) != 1:
        raise Exception('Unexpected number of tbody elements')
    tbody = tbodys[0]
    return tbody


def get_projection_directory_hrefs():
    fp = urllib.request.urlopen("https://github.com/shaman-lab/COVID-19Projection")
    soup = BeautifulSoup(fp)

    tbody = get_tbody(soup)

    rows = tbody.findAll('tr', {'class': 'js-navigation-item'})

    directory_rows = [row for row in rows if row.find('td', {'class': 'icon'}).find('svg', {'aria-label': 'directory'}) is not None]

    directory_hrefs = [
        directory_row.find(
            'td', {'class': 'content'}).find(
            'a', {'class': 'js-navigation-open'}).attrs['href'] for 
        directory_row in directory_rows]
    projection_directory_hrefs = [h for h in directory_hrefs if 'Projection_' in h]
    return projection_directory_hrefs


def get_model_version(model_version_subdir, y=2020):
    date_string = model_version_subdir.replace('/', '').replace('Projection_', '')
    model_version_string = datetime.datetime.strptime(date_string + str(y), '%B%d%Y').strftime('%Y-%m-%d')
    return model_version_string


def get_projection_df_from_hrefs(bed_href, projection_href, quant_convention_dict, naming_convention_dict, compiled_df, model_version_subdir):
    bed_df = pd.read_csv(
        'https://raw.githubusercontent.com/{}'.format(bed_href).replace('blob', ''),
        encoding='latin_1')
    projection_df = pd.read_csv(
        'https://raw.githubusercontent.com/{}'.format(projection_href).replace('blob', ''),
        encoding='latin_1')
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
    compiled_df = pd.read_csv('data/ihme_compiled.csv')

    all_projection_dfs = []
    projection_directory_hrefs = get_projection_directory_hrefs()
    for projection_directory_href in projection_directory_hrefs:
        print("https://github.com" + projection_directory_href)
        model_version_subdir = projection_directory_href.split('/')[-1]
        fp = urllib.request.urlopen("https://github.com" + projection_directory_href)
        soup = BeautifulSoup(fp)
        tbody = get_tbody(soup)
        rows = tbody.findAll('tr', {'class': 'js-navigation-item'})
        icons = [e.find('td', {'class': 'icon'}) for e in rows]

        file_rows = [row for row in rows if row.find(
            'td', {'class': 'icon'}).find(
            'svg', {'aria-label': 'file'}) is not None]

        file_hrefs = [
            file_row.find(
                'td', {'class': 'content'}).find(
                'a', {'class': 'js-navigation-open'}).attrs['href'] for 
            file_row in file_rows]

        bed_hrefs = sorted([f for f in file_hrefs if 'bed_' in f and 'csv' in f])
        projection_hrefs = sorted([f for f in file_hrefs if 'Projection_' in f.split('/')[-1] and 'csv' in f])
        if [e.split('/')[-1].replace('bed_', '') for e in bed_hrefs] != [e.split('/')[-1].replace('Projection_', '') for e in projection_hrefs]:
            print('Number of bed files do not match number of projection files. Skipping.')
            continue
        print(model_version_subdir)
        for bed_href, projection_href in zip(bed_hrefs, projection_hrefs):
            model = bed_href.split('/')[-1].replace('bed_', '').replace('.csv', '')
            print(model)
            projection_df = get_projection_df_from_hrefs(bed_href, projection_href, quant_convention_dict, naming_convention_dict, compiled_df, model_version_subdir)
            projection_df['model'] = 'CU_shamanlab_' + model
            all_projection_dfs.append(projection_df)

            m = projection_df['model'].iloc[0]
            mv = projection_df['model_version'].iloc[0]

            projection_df.to_csv('{d}{m}_{mv}.csv'.format(d=cu_dir, m=m, mv=mv))
    complete_projection_df = pd.concat(all_projection_dfs)
    return complete_projection_df


def main():
    complete_projection_df = get_cu_df()


if __name__ == '__main__':
    main()