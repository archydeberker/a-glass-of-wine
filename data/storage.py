import boto3
from botocore.exceptions import ClientError
from data import constants


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


if __name__ == '__main__':
    upload_data_to_s3('20200329-181955.csv', 'test.csv')