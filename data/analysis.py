import datetime

import pandas as pd


def parse_timestamp_from_filename(filename, strformat="%Y%m%d-%H%M%S", suffix='.csv'):
    filename = filename.split('/')[-1]
    filename = filename.rstrip(suffix)
    timestamp = datetime.datetime.strptime(filename, strformat)
    return timestamp


def get_most_popular_wines(df_start, df_end):
    """
    Returns a dataframe sorted by wine sales between `df_start` and `df_end`
    """
    df = df_start.set_index('id').join(df_end.set_index('id'), lsuffix='_start', rsuffix='_end')
    df['stock_diff'] = df['stock_end'] - df['stock_start']
    df.sort_values(by='stock_diff', inplace=True)
    return df


def compile_saq_data(all_store_data_paths):
    all_data = []
    for store in all_store_data_paths:
        df = pd.read_csv(store)
        df['timestamp'] = parse_timestamp_from_filename(store)
        all_data.append(df)


def load_saq_online_data_to_df(path):
    return pd.read_csv(path)


def generate_consumption_df(df):
    """
    Convert a dataframe of wine stocks to one of wine consomption.

    If stock increases from t to t+1 then add a NaN

    """
    diff_df = df.diff(axis=1)
    diff_df[diff_df < 0 ] = pd.nan


def plot_all_wine_over_time():
    pass
