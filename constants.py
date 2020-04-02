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


CASE_DOWNLOAD_URL = 'https://docs.google.com/spreadsheets/d/1D6okqtBS3S2NRC7GFVHzaZ67DuTw7LX49-fqSLwJyeo/export?format=xlsx'
CASE_CITATION = "https://github.com/ishaberry/Covid19Canada"
