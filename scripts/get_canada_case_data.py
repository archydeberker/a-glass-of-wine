from constants import CASE_DATA_CSV, DOWNLOAD_URL
from data.storage import upload_data_to_s3
from webapp.api.cases import download_data, create_cases_df_for_quebec

if __name__ == '__main__':
    filename = 'download.xlsx'
    filename = download_data(download_url=DOWNLOAD_URL, download_name=filename)
    df = create_cases_df_for_quebec(filename)

    df.to_csv(CASE_DATA_CSV)

    upload_data_to_s3(CASE_DATA_CSV, CASE_DATA_CSV.lstrip('./'))
