import tempfile

import pandas as pd
import requests

import constants
import data.storage
from constants import DOWNLOAD_URL


class CaseData:
    def __init__(self, use_cached=True, local_path=None):
        if use_cached and not local_path:
            cache_files = sorted(data.storage.list_data_on_s3(Prefix=constants.CASE_DATA_CSV))
            print(f'Using cached files {cache_files[-1]}')
            self.case_df = data.storage.get_s3_data_to_df(cache_files[-1],
                                                          parse_dates=['date'])
        elif local_path:
            self.case_df = pd.read_csv(local_path, parse_dates=['date'])
        else:
            with tempfile.NamedTemporaryFile as temp:
                filename = download_data(download_url=DOWNLOAD_URL, download_name=temp.name)
                df = create_cases_df_for_quebec(filename)

            self.case_df = df


def filter_for_quebec(df):
    return df.loc[df['province'] == 'Quebec']


def download_data(download_url=DOWNLOAD_URL, download_name='download.xlsx'):
    download = requests.get(download_url)
    with open(download_name, 'wb') as f:
        f.write(download.content)

    return download_name


def aggregate_df(df):
    agg_df = df.groupby('date').count()
    agg_df['cum_value'] = df.groupby('date').count()['daily_value'].cumsum()
    agg_df = agg_df.reset_index()
    return agg_df


def create_cases_df_for_quebec(path_to_download):
    """Create a long-style dataframe"""

    cases_df = pd.read_excel(path_to_download, header=3)
    deaths_df = pd.read_excel(path_to_download, header=3, sheet_name=1)
    recovered_df = pd.read_excel(path_to_download, header=3, sheet_name=2)

    cases_df = filter_for_quebec(cases_df)
    deaths_df = filter_for_quebec(deaths_df)
    recovered_df = filter_for_quebec(recovered_df)  # raw data is cumulative recovered

    cases_df['daily_value'] = cases_df['provincial_case_id']
    cases_df['date'] = cases_df['date_report']
    cases_agg_df = aggregate_df(cases_df)
    cases_agg_df['status'] = 'cases'

    deaths_df['daily_value'] = deaths_df['province_death_id']
    deaths_df['date'] = deaths_df['date_death_report']
    deaths_agg_df = aggregate_df(deaths_df)
    deaths_agg_df['status'] = 'deaths'

    recovered_df['status'] = 'recovered'
    recovered_df['cum_value'] = recovered_df['cumulative_recovered']
    recovered_df['date'] = recovered_df['date_recovered']

    cols = ['status', 'cum_value', 'date']
    df = pd.concat([cases_agg_df[cols], deaths_agg_df[cols], recovered_df[cols]])

    # later - subtract recovered and deaths from cases
    df_shortform = df.set_index(['date', 'status'])['cum_value'].unstack(fill_value=0).reset_index()

    return df_shortform
