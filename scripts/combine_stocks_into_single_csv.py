from webapp.api import wine
from data.storage import upload_data_to_s3
from constants import ONLINE_DATA_CSV


def main():
    """
    Combine all existing S3 data into a single CSV and upload it
    """
    counter = wine.StockCounter()

    counter.online_df.to_csv(ONLINE_DATA_CSV)
    upload_data_to_s3(ONLINE_DATA_CSV, ONLINE_DATA_CSV.lstrip('./'))


if __name__ == '__main__':
    main()
