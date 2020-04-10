import datetime

import constants
from data.storage import list_online_stock_files, load_latest_online_combined_df, load_today_df


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


class StockCounter:
    def __init__(self):

        print('Loading df for today')
        self.online_df = load_today_df()
        print(f"Oldest datapoint is {self.online_df['timestamp'].min()}")
        print(f"Latest datapoint is {self.online_df['timestamp'].max()}")
        self.stock_change_df = self.get_daily_stock_change_df()
        print('Calculated stock change df')

    def get_daily_stock_change_df(self):
        df = self.online_df

        most_recent = self.online_df['timestamp'].max()
        oldest = self.online_df['timestamp'].min()

        df.sort_values(by=['id', 'timestamp'], inplace=True)
        df['stock_delta'] = df.groupby('wine_type')['stock'].diff()
        df['wine_consumption'] = df['stock_delta'].apply(lambda x: abs(min(0, x)))
        df['cumulative_wine_consumption'] = df.groupby('id')['wine_consumption'].cumsum()

        stock_1_day_ago_df = df.loc[df['timestamp'] == oldest]

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
        stock_change_df['stock_change'] = stock_change_df['cumulative_wine_consumption_now'] - \
                                          stock_change_df['cumulative_wine_consumption_1_day_ago']

        # Drop duplicates
        stock_change_df.drop_duplicates(subset=['wine_name'], inplace=True)

        stock_change_df.sort_values(by='stock_change', inplace=True, ascending=False)

        return stock_change_df

    @property
    def bottles_sold(self):
        return self.stock_change_df['stock_change'].sum()

    @property
    def glasses_sold(self):
        return self.bottles_sold * constants.GLASSES_IN_A_BOTTLE

    @property
    def sales_by_wine_type(self):
        _df = self.stock_change_df.copy()
        _df.dropna(inplace=True, subset=['wine_type_now'])
        _df = _df.groupby('wine_type_now').sum()
        return {'red': _df.loc['Red wine']['stock_change'],
                'white': _df.loc['White wine']['stock_change'],
                'rose': _df.loc['Rosé']['stock_change'],
                }
