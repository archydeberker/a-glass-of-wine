import data.storage as storage
import numpy as np
import pandas as pd
from data.analysis import parse_timestamp_from_filename
import constants

def list_new_files(newest_file_in_df):
    """Check for CSVs which are not in the current combined dataframe"""
    online_files = np.asarray(storage.list_online_stock_files())
    dates = [parse_timestamp_from_filename(x) for x in online_files]
    include = [date > newest_file_in_df for date in dates]

    return online_files[include]


def load_new_files(files):
    new_data = []
    for file in files:
        print(file)
        df = storage.get_s3_data_to_df(file)
        df['timestamp'] = parse_timestamp_from_filename(file)
        new_data.append(df)

    return pd.concat(new_data)


def main():
    existing_df = storage.load_latest_online_combined_df()
    latest_timestamp = existing_df['timestamp'].max()
    print(f"Most recent timestamp in existing datafrae is {latest_timestamp}")

    new_files = list_new_files(latest_timestamp)
    new_df = load_new_files(new_files)

    print(f'Adding {len(new_df)} new rows to the combined dataframe')

    combined_df = pd.concat([existing_df, new_df])

    combined_df.to_csv(constants.ONLINE_DATA_CSV)
    storage.upload_data_to_s3(constants.ONLINE_DATA_CSV, constants.ONLINE_DATA_CSV.lstrip('./'))


if __name__ == '__main__':
    main()
