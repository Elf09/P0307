# sheets_handler.py

import os
import json
import base64
import gspread
from google.oauth2.service_account import Credentials

GOOGLE_CREDS_BASE64 = os.getenv("GOOGLE_CREDS_BASE64")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

def get_table_data():
    if not GOOGLE_CREDS_BASE64 or not SPREADSHEET_ID:
        return [["Нет данных"]]

    creds_dict = json.loads(base64.b64decode(GOOGLE_CREDS_BASE64))
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet.get_all_values()
