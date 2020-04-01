
import datetime

from webapp.api import wine
from data.storage import upload_data_to_s3


def main():
    """
    Combine all existing S3 data into a single CSV and upload it
    """
    counter = wine.StockCounter()
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filepath = f"online_data_{now}.csv"
    counter.online_df.to_csv(filepath)
    upload_data_to_s3(filepath, filepath.lstrip('./'))


if __name__ == '__main__':
    main()
