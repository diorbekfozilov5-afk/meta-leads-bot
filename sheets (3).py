"""Google Sheets bilan ishlash uchun yordamchi funksiyalar."""

import os
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_SERVICE_ACCOUNT_FILE = os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]
_SPREADSHEET_ID = os.environ["GOOGLE_SPREADSHEET_ID"]
_SHEET_NAME = os.environ.get("GOOGLE_SHEET_NAME", "Leads")

_client = None
_sheet = None


def _get_sheet():
    global _client, _sheet
    if _sheet is None:
        creds = Credentials.from_service_account_file(_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        _client = gspread.authorize(creds)
        spreadsheet = _client.open_by_key(_SPREADSHEET_ID)
        try:
            _sheet = spreadsheet.worksheet(_SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            _sheet = spreadsheet.add_worksheet(title=_SHEET_NAME, rows=1000, cols=10)
            _sheet.append_row(
                ["Vaqt", "Lead ID", "Ism", "Telefon", "Email", "Form ID", "Ad ID", "Campaign ID"]
            )
    return _sheet


def append_lead_row(row: list):
    """Google Sheets'ning oxiriga yangi qator qo'shadi."""
    sheet = _get_sheet()
    sheet.append_row(row, value_input_option="USER_ENTERED")
