
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Замените 'your-creds.json' на путь к вашему JSON
SHEET_ID = "ВАШ_ID_ТАБЛИЦЫ"
RANGE = "Лист1!A1"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("your-creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

def append_to_sheet(row):
    sheet.append_row(row)
