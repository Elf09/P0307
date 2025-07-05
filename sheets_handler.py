import os
import json
import base64
import gspread
from google.oauth2.service_account import Credentials

# Авторизация и доступ к таблице
def get_sheet():
    creds_json = os.getenv("GOOGLE_CREDS_BASE64")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    if not creds_json or not spreadsheet_id:
        return None

    creds_dict = json.loads(base64.b64decode(creds_json))
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).sheet1

# Получение таблицы в читаемом формате
def get_table_data():
    sheet = get_sheet()
    if not sheet:
        return [["Ошибка доступа к таблице"]]

    data = sheet.get_all_values()
    headers = data[0]
    rows = data[1:]

    result = []
    for row in rows:
        name = row[1]  # B: ФИО
        vacation_periods = []
        # Обход пар колонок C–L (индексы 2–11)
        for i in range(2, 12, 2):
            start = row[i] if i < len(row) else ''
            end = row[i+1] if (i+1) < len(row) else ''
            if start and end:
                vacation_periods.append(f"{start} – {end}")

        periods_str = "; ".join(vacation_periods) if vacation_periods else "Нет данных"
        result.append(f"{name}: {periods_str}")

    return result
