import tempfile

import numpy as np
import pandas as pd
import requests

import constants
import data.storage
from json.decoder import JSONDecodeError

from functools import lru_cache


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
                filename = download_data(download_url=constants.DOWNLOAD_URL, download_name=temp.name)
                df = create_cases_df_for_quebec(filename)

            self.case_df = df


def filter_for_quebec(df):
    return df.loc[df['province'] == 'Quebec']


def download_data(download_url=constants.DOWNLOAD_URL, download_name='download.xlsx'):
    download = requests.get(download_url)
    with open(download_name, 'wb') as f:
        f.write(download.content)

    return download_name


def aggregate_df(df):
    agg_df = df.groupby('date').count()
    agg_df['cum_value'] = df.groupby('date').count()['daily_value'].cumsum()
    agg_df = agg_df.reset_index()
    return agg_df


def create_cases_df_for_quebec(path_to_download, wideform=True):
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


@lru_cache(1000)
def get_cases_from_api(countries=constants.COUNTRIES_TO_GRAPH,
                       api_url=constants.CASE_API_URL, country_codes=constants.COUNTRY_API_IDS):

    try:
        countries = [get_df_for_country(c,
                                        api_url=api_url,
                                        country_codes=country_codes) for c in countries]
        countries = pd.concat(countries)
        countries.to_csv(constants.COUNTRY_DATA_CACHE_CSV)
        data.storage.upload_data_to_s3(constants.COUNTRY_DATA_CACHE_CSV, constants.COUNTRY_DATA_CACHE_CSV.lstrip('./'))

    except JSONDecodeError as j:
        print("There was a problem fetching cases from the API, using last saved version")
        print(f"Error was {j}")
        countries = data.storage.get_s3_data_to_df(constants.COUNTRY_DATA_CACHE_CSV)

    return countries


def days_since_start_point(df, threshold=100):
    """ Get the timepoint to use as a threshold for days since X"""

    idx = df['sum'].apply(lambda x: abs(x-threshold)).argmin()

    return np.arange(len(df)) - idx


def get_df_for_country(name,
                       api_url=constants.CASE_API_URL,
                       country_codes=constants.COUNTRY_API_IDS):

    response = requests.get(f"{api_url}/{country_codes[name]}")
    j = response.json()['location']

    out = []
    for status in ['confirmed', 'deaths']:
        timeline = j['timelines'][status]['timeline']
        _df = pd.DataFrame.from_dict(timeline, orient='index', columns=['sum'])
        _df['status'] = status
        _df['daily_count'] = _df['sum'].diff()
        _df['daily_count_change'] = _df['daily_count'].diff()
        _df['rolling_daily_count'] = _df['daily_count'].rolling(7).mean()
        _df['rolling_daily_count_change'] = _df['daily_count_change'].rolling(7).mean()
        _df['days_since_100'] = days_since_start_point(_df, threshold=100)
        _df['days_since_30'] = days_since_start_point(_df, threshold=30)
        _df['days_since_3'] = days_since_start_point(_df, threshold=3)

        out.append(_df)

    df = pd.concat(out)

    df['country'] = name

    return df
