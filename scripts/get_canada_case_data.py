import datetime
import tempfile

import pandas as pd
import requests

from constants import CASE_DOWNLOAD_URL
from data import storage


def filter_for_quebec(df):
    return df.loc[df['province'] =='Quebec']


def main():
    download = requests.get(CASE_DOWNLOAD_URL)
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filepath = f"canada_case_data_{now}.csv"

    with tempfile.NamedTemporaryFile('wb') as f:
        f.write(download.content)
        create_cases_df_for_quebec(f.name, outpath=filepath)


def create_cases_df_for_quebec(path_to_download, outpath):
    """Create a long-style dataframe"""

    cases_df = pd.read_excel(path_to_download, header=3)
    deaths_df = pd.read_excel(path_to_download, header=3, sheet_name=1)
    recovered_df = pd.read_excel(path_to_download, header=3, sheet_name=2)

    cases_df = filter_for_quebec(cases_df)
    deaths_df = filter_for_quebec(deaths_df)
    recovered_df = filter_for_quebec(recovered_df)

    cases_df['status'] = 'cases'
    cases_df['value'] = cases_df['provincial_case_id']
    cases_df['date'] = cases_df['date_report']

    deaths_df['status'] = 'deaths'
    deaths_df['value'] = deaths_df['province_death_id']
    deaths_df['date'] = deaths_df['date_death_report']

    recovered_df['status'] = 'recovered'
    recovered_df['value'] = recovered_df['cumulative_recovered']
    recovered_df['date'] = recovered_df['date_recovered']

    cols = ['status', 'value', 'date']
    df = pd.concat([cases_df[cols], deaths_df[cols], recovered_df[cols]])

    df.to_csv(outpath)

    filepath = 'latest_case_data.csv'
    storage.upload_data_to_s3(outpath, filepath.lstrip('./'))



if __name__ == '__main__':
    main()
