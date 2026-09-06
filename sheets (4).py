"""Google Sheets bilan ishlash uchun yordamchi funksiyalar."""

import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Ikkita usuldan biri bilan ishlaydi:
# 1) GOOGLE_SERVICE_ACCOUNT_JSON - Render kabi hostinglarda, JSON faylning
#    butun matnini to'g'ridan-to'g'ri environment variable sifatida qo'yasiz.
# 2) GOOGLE_SERVICE_ACCOUNT_FILE - lokal ishlatganda, JSON faylning yo'li.
_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
_SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
_SPREADSHEET_ID = os.environ["GOOGLE_SPREADSHEET_ID"]
_SHEET_NAME = os.environ.get("GOOGLE_SHEET_NAME", "Leads")

_client = None
_sheet = None


def _get_sheet():
    global _client, _sheet
    if _sheet is None:
        if _SERVICE_ACCOUNT_JSON:
            info = json.loads(_SERVICE_ACCOUNT_JSON)
            creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        elif _SERVICE_ACCOUNT_FILE:
            creds = Credentials.from_service_account_file(_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        else:
            raise RuntimeError(
                "GOOGLE_SERVICE_ACCOUNT_JSON yoki GOOGLE_SERVICE_ACCOUNT_FILE "
                "environment variable'laridan biri o'rnatilishi kerak."
            )
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
