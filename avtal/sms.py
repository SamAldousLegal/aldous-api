import os
import glob
import pandas as pd
import json
import requests
import logging
from auth_utils import get_auth_header

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(r'avtal\\extend_sms_responses.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

INPUT_DIR = r'avtal\\files-in\\'
OUTPUT_DIR = r'avtal\\files-out\\'
API_URL = "https://api.aldouslegal.com/api/v1/collect/data/debtor"

FIELDS_MAPPING = {
    "File": "de_number",
    "DOB": "de_dob",
    "Charged": "de_charge_date",
    "Home": "de_home_phone",
    "Other": "de_other_phone",
    "Cell": "de_cell_phone",
    "Work": "de_work_phone",
    "Mode": "de_active",
    "Status": "de_status",
    "Owing": "de_owing",
    "Paid": "de_paid",
    "Group": "de_group_id",
    "Client": "cl_name",
    "Program": "cl_user_1",
    "Software": "cl_cell_extension"
}

def load_csv_data(file_path):
    logger.info(f"Loading CSV data from {file_path}")
    df = pd.read_csv(file_path)
    return df

def fetch_api_data(account_ids):
    if not account_ids:
        logger.warning("No account IDs provided to fetch API data.")
        return None

    header = get_auth_header()
    fields_str = ",".join(FIELDS_MAPPING.values())
    accounts_str = ",".join(map(str, account_ids))

    url = f"{API_URL}?fields={fields_str}&join=(client,inner,cl_rowid,de_rowid_client)&filter=de_number__in=({accounts_str})"
    logger.info(f"Fetching API data for {len(account_ids)} accounts")
    response = requests.get(url, headers=header)

    if response.status_code == 200:
        logger.info("API request successful.")
        return response.json()
    else:
        logger.error(f"API request failed: {response.status_code} {response.text}")
        return None

def determine_phone_type(row):
    phone_number = str(row["Phone Number"])[1:]
    if phone_number == str(row.get("Home")):
        return "Home"
    elif phone_number == str(row.get("Cell")):
        return "Cell"
    elif phone_number == str(row.get("Work")):
        return "Work"
    elif phone_number == str(row.get("Other")):
        return "Other"
    else:
        return "None"

def process_file(file_path):
    logger.info(f"Processing file: {file_path}")
    df = load_csv_data(file_path)
    account_ids = df["Agency Account ID"].dropna().astype(str).tolist()

    api_data = fetch_api_data(account_ids)
    if api_data and "data" in api_data:
        api_df = pd.DataFrame(api_data["data"])
        api_df.rename(columns={v: k for k, v in FIELDS_MAPPING.items()}, inplace=True)
        df["Agency Account ID"] = df["Agency Account ID"].astype(str)
        api_df["File"] = api_df["File"].astype(str)

        merged_df = df.merge(api_df, left_on="Agency Account ID", right_on="File", how="left")
        merged_df["Phone Type"] = merged_df.apply(determine_phone_type, axis=1)

        merged_df.drop(columns=["File", "Home", "Work", "Other", "Cell"], inplace=True)

        suffix = file_path.split("SMS Responses - Aldous")[-1].replace(".csv", "")
        out_file = os.path.join(OUTPUT_DIR, f"SMS_Responses-Aldous-Extended{suffix}.csv")
        merged_df.to_csv(out_file, index=False)

        os.rename(file_path, file_path + ".done")
        logger.info(f"Processed and saved extended file: {out_file}")
    else:
        logger.warning("No API data found or returned.")

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pattern = os.path.join(INPUT_DIR, "SMS Responses - Aldous*.csv")
    files = glob.glob(pattern)

    if not files:
        logger.info("No matching files found.")
        return

    for file_path in files:
        process_file(file_path)
