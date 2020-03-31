import datetime
import re

import data.constants as constants
import data.storage
import pandas as pd


class StockCounter:
    def __init__(self):
        self.files = data.storage.list_data_on_s3()
        print(f"Found {len(self.files)} files on S3")
        self.online_files = list(filter(lambda x: bool(re.match(constants.ONLINE_FILE_REGEX, x)), self.files))
        print(f"{len(self.online_files)} of those were for online stock")
        self.online_df = self.load_online_data()
        print('Getting stock change df')
        self.stock_change_df = self.get_daily_stock_change_df()

    def load_online_data(self):
        all_data = []
        for file in self.online_files:
            print(file)
            df = data.storage.get_s3_data_to_df(file)
            df['timestamp'] = parse_timestamp_from_filename(file)
            all_data.append(df)

        return pd.concat(all_data)

    def get_daily_stock_change_df(self):
        df = self.online_df
        now = datetime.datetime.now()
        one_day_ago = now - datetime.timedelta(days=1)

        most_recent = self.online_df['timestamp'].max()
        closest_to_one_day_ago = self.online_df['timestamp'].iloc[abs(one_day_ago - self.online_df['timestamp']).argmin()]

        stock_change_df = self.online_df.loc[self.online_df['timestamp'] == most_recent].copy()

        stock_change_df['stock_1_day_ago'] = df.loc[
            df['timestamp'] == closest_to_one_day_ago].stock
        stock_change_df['timestamp_1_day_ago'] = df.loc[
            df['timestamp'] == closest_to_one_day_ago].timestamp

        stock_change_df['stock_change'] = stock_change_df['stock'] - stock_change_df['stock_1_day_ago']
        stock_change_df.sort_values(by='stock_change', inplace=True)

        return stock_change_df

    def _negative_stock_change(self, df):
        return self.stock_change_df.loc[self.stock_change_df['stock_change'] <= 0]

    @property
    def bottles_sold(self):
        return abs(self._negative_stock_change(self.stock_change_df)['stock_change'].sum())

    @property
    def glasses_sold(self):
        return abs(self._negative_stock_change(self.stock_change_df)['stock_change'].sum() * constants.GLASSES_IN_A_BOTTLE)


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


if __name__ == '__main__':
    counter = StockCounter()
