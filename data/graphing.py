import pandas as pd

def list_saq_data():
    pass


def load_saq_data_to_df():
    pass

def generate_consumption_df(df):
    """
    Convert a dataframe of wine stocks to one of wine consomption.

    If stock increases from t to t+1 then add a NaN

    """
    diff_df = df.diff(axis=1)
    diff_df[diff_df < 0 ] = pd.nan

def plot_all_wine_over_time()
    pass

