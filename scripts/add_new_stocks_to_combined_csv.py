import data.storage as storage
import pandas as pd
import constants
from data.storage import list_files_newer_than_date, load_new_files


def main():
    existing_df = storage.load_latest_online_combined_df()
    latest_timestamp = existing_df['timestamp'].max()
    print(f"Most recent timestamp in existing datafrae is {latest_timestamp}")

    new_files = list_files_newer_than_date(latest_timestamp)
    new_df = load_new_files(new_files)

    print(f'Adding {len(new_df)} new rows to the combined dataframe')

    combined_df = pd.concat([existing_df, new_df])

    combined_df.to_csv(constants.ONLINE_DATA_CSV)
    storage.upload_data_to_s3(constants.ONLINE_DATA_CSV, constants.ONLINE_DATA_CSV.lstrip('./'))


if __name__ == '__main__':
    main()
