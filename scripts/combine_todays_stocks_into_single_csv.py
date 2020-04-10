import datetime

import data.storage as storage
import constants
from data.storage import list_files_newer_than_date, load_new_files


def main():

    today = datetime.datetime.now().date()
    today_midnight = datetime.datetime(today.year, today.month, today.day)

    print(f"Today midnight timestamp {today_midnight}")

    new_files = list_files_newer_than_date(today_midnight)
    today_df = load_new_files(new_files)

    print(f"{len(today_df)} rows in today data, spanning {today_df['timestamp'].min()} to "
          f"{today_df['timestamp'].max()}")

    today_df.to_csv(constants.TODAY_SAQ_DATA_CSV)
    storage.upload_data_to_s3(constants.TODAY_SAQ_DATA_CSV, constants.TODAY_SAQ_DATA_CSV.lstrip('./'))


if __name__ == '__main__':
    main()
