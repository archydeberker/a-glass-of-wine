import datetime
import re

import pandas as pd

import data.storage
import constants
from data.analysis import parse_timestamp_from_filename


def glasses_sold_yesterday(stock_change_df):
    total_bottles_sold = stock_change_df['stock_change'].sum()
    return f"{abs(int(total_bottles_sold * constants.GLASSES_IN_A_BOTTLE)):,}"


class Wine:
    def __init__(self, name, img, sales):
        self.name = name
        self.img = self._format_img(img)
        self.sales = int(abs(sales))

    def _format_img(self, img_url):
        img_url = img_url.split('?')[0]
        img_url += '?quality=80&fit=bounds&height=166&width=111&canvas=111:166'
        return img_url


class StockDataFetcher:
    """
    A wrapper around a stock counter which controls refreshing
    """
    def __init__(self, counter, refresh_interval=datetime.timedelta(hours=1)):
        self._counter = counter
        self.last_refreshed = datetime.datetime.now()
        self.refresh_interval = refresh_interval

    @property
    def counter(self):
        # TODO can we make this asynchronous, experience will suck when this is
        # refreshed
        if datetime.datetime.now() - self.last_refreshed > self.refresh_interval:
            print('Refreshing wine data from S3')
            self._counter.__init__(use_cached=True)

        return self._counter


class StockCounter:
    def __init__(self, use_cached=False):
        if use_cached:
            cache_files = sorted(data.storage.list_data_on_s3(Prefix='online_data'))
            print(f'Using cached files {cache_files[-1]}')
            self.online_df = data.storage.get_s3_data_to_df(cache_files[-1],
                                                            parse_dates=['timestamp'],
                                                            dtype={'wine_name': 'object',
                                                                   'id': 'int64',
                                                                   'stock': 'int64',
                                                                   'timestamp': 'str',
                                                                   'wine_img': 'str'})
        else:
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

        stock_1_day_ago_df = df.loc[df['timestamp'] == closest_to_one_day_ago]

        stock_change_df = self.online_df.loc[self.online_df['timestamp'] == most_recent].copy()

        # Care required on the join. Use a right join so that all wines that were in stock 1 day
        # ago appear in the list
        stock_change_df.set_index('id', inplace=True)
        stock_1_day_ago_df.set_index('id', inplace=True)

        stock_change_df = stock_change_df.join(stock_1_day_ago_df, how='right', lsuffix='_now', rsuffix='_1_day_ago')

        stock_change_df.drop(['wine_name_now', 'wine_img_now'], axis=1, inplace=True)
        stock_change_df.rename({'wine_name_1_day_ago': 'wine_name',
                                'wine_img_1_day_ago': 'wine_img'}, inplace=True, axis=1)

        # Assume if a wine dropped out of the stock list it was sold out
        stock_change_df['stock_now'].fillna(0)

        stock_change_df['stock_change'] = stock_change_df['stock_now'] - stock_change_df['stock_1_day_ago']
        stock_change_df.sort_values(by='stock_change', inplace=True)

        # Drop duplicates
        stock_change_df.drop_duplicates(subset=['wine_name'], inplace=True)

        return stock_change_df

    def _negative_stock_change(self, df):
        return self.stock_change_df.loc[self.stock_change_df['stock_change'] <= 0]

    @property
    def bottles_sold(self):
        return abs(self._negative_stock_change(self.stock_change_df)['stock_change'].sum())

    @property
    def glasses_sold(self):
        return abs(self._negative_stock_change(self.stock_change_df)['stock_change'].sum() * constants.GLASSES_IN_A_BOTTLE)

    @property
    def sales_by_wine_type(self):
        _df = self.stock_change_df.copy()
        _df.dropna(inplace=True, subset=['wine_type_now'])
        _df = _df.groupby('wine_type_now').sum()
        return {'red': _df.loc['Red wine']['stock_change'],
                  'white': _df.loc['White wine']['stock_change'],
                  'rose': _df.loc['Rosé']['stock_change'],
                  }
