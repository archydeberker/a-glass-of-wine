import os

S3_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID_WINE')
S3_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY_WINE')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME_WINE')

ONLINE_FILE_REGEX = '2020.*\.csv'
ONLINE_CACHE_REGEX = 'online_data_2020.*\.csv'
GLASSES_IN_A_BOTTLE = 6


class Colours:
    red = '#7f0000'
    white = '#fff8e1'
    rose = '#ffcdd2'