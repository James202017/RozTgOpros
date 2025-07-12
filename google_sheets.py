
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = os.getenv("GSHEET_CREDENTIALS_JSON")
    sheet_name = os.getenv("GSHEET_SHEET_NAME")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(credentials)
    sheet = client.open(sheet_name).sheet1
    return sheet

def append_row(data):
    sheet = get_sheet()
    sheet.append_row(data)
