import os

from dotenv import load_dotenv

from scripts.download_data import download_data
from scripts.parse_small_csv import load_data

load_dotenv(".env")

small_file_url = os.environ["SMALL_CSV_FILE_URL"]
small_file_name = os.environ["SMALL_CSV_FILE_NAME"]

large_file_url = os.environ["LARGE_CSV_FILE_URL"]
large_file_name = os.environ["LARGE_CSV_FILE_NAME"]
data_dir = os.environ["DATA_DIR_PATH"]

small_csv_path = download_data(
    url=small_file_url,
    filename=small_file_name,
    target_path=data_dir,
)
big_csv_path = download_data(
    url=large_file_url,
    filename=large_file_name,
    target_path=data_dir,
)

df_small = load_data(small_csv_path)
print(df_small)
