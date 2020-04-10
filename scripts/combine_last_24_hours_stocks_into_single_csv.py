import datetime

import data.storage as storage
import constants
from data.storage import list_files_newer_than_date, load_new_files


def main():

    today = datetime.datetime.now()
    one_day_ago = today + datetime.timedelta(days=-1)

    print(f"Current timestamp {today}")

    new_files = list_files_newer_than_date(one_day_ago)
    today_df = load_new_files(new_files)

    print(f"{len(today_df)} rows in today data, spanning {today_df['timestamp'].min()} to "
          f"{today_df['timestamp'].max()}")

    today_df.to_csv(constants.TODAY_SAQ_DATA_CSV)
    storage.upload_data_to_s3(constants.TODAY_SAQ_DATA_CSV, constants.TODAY_SAQ_DATA_CSV.lstrip('./'))


if __name__ == '__main__':
    main()
