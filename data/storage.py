import re

import boto3
from botocore.exceptions import ClientError
import constants
from io import BytesIO
import pandas as pd


def _configure_s3_client():
    s3_client = boto3.client(
        "s3", aws_access_key_id=constants.S3_ACCESS_KEY, aws_secret_access_key=constants.S3_SECRET_KEY
    )
    return s3_client


def upload_data_to_s3(filepath, filename):
    """
    Upload a file to an S3 bucket
    :param data: Bytes to upload.
    :param object_name: S3 object name.
    :return: True if file was uploaded, else False
    """
    s3_client = _configure_s3_client()
    try:
        with open(filepath, 'rb') as f:
            s3_client.put_object(Body=f, Bucket=constants.S3_BUCKET_NAME, Key=filename)
    except ClientError as e:
        print(e)
        return False
    return True


def download_file_from_s3(filename):
    s3_client = _configure_s3_client()
    try:
        download = s3_client.get_object(Key=filename, Bucket=constants.S3_BUCKET_NAME)
    except ClientError as e:
        print(e)
        return False
    content = download["Body"].read()
    return content


def list_data_on_s3(bucket=constants.S3_BUCKET_NAME, **kwargs):
    s3_client = _configure_s3_client()
    return [key['Key'] for key in s3_client.list_objects(Bucket=bucket, **kwargs)['Contents']]


def get_s3_data_to_df(filename, **kwargs):
    data = download_file_from_s3(filename)
    return pd.read_csv(BytesIO(data), **kwargs)


def list_online_stock_files(regex=constants.ONLINE_FILE_REGEX):
    files = list_data_on_s3()
    return list(filter(lambda x: bool(re.match(regex, x)), files))


def load_latest_online_combined_df():
    cache_files = sorted(list_data_on_s3(Prefix='online_data'))
    print(f'Using cached files {cache_files[-1]}')
    return get_s3_data_to_df(cache_files[-1],
                             parse_dates=['timestamp'],
                             dtype={'wine_name': 'object',
                                    'id': 'int64',
                                    'stock': 'int64',
                                    'timestamp': 'str',
                                    'wine_img': 'str'})


if __name__ == '__main__':
    contents = list_data_on_s3()
    data = download_file_from_s3(contents[0])
    df = pd.read_csv(BytesIO(data))
    print(df.head())