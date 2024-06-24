from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from src.load_env_vars import G_SHEET_ID

root_dir = Path(__file__).resolve().parents[1]
credentials_path = root_dir / "google_sheets_credentials.json"

class GSheetHelper:
    """A class to interact with Google Sheets API."""
    def __init__(self, sheet_id=G_SHEET_ID, credentials_path=credentials_path):
        self.sheet_id = sheet_id
        self.credentials_path = credentials_path
        self.client = None
        self.workbook = None
        self.sheet = None

    def authorize(self):
        """Authorize the Google Sheets API client."""
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.workbook = self.client.open_by_key(self.sheet_id)

    def select_worksheet(self, sheet_name):
        """Select the worksheet by name."""
        if not self.workbook:
            raise Exception("Workbook not initialized. Call authorize() first.")
        self.sheet = self.workbook.worksheet(sheet_name)

    def _get_first_empty_row_in_column_a(self):
        """Get the row number of the first empty cell in column A."""
        if not self.sheet:
            raise Exception("Sheet not selected. Call select_worksheet() first.")

        column_a_values = self.sheet.col_values(1)
        for i, value in enumerate(column_a_values):
            if value == '':
                return i + 1
        return len(column_a_values) + 1

    def upload_data(self, data):
        """Append data to the selected worksheet."""
        if not self.sheet:
            raise Exception("Sheet not selected. Call select_worksheet() first.")
        start_cell = f'A{self._get_first_empty_row_in_column_a()}'
        self.sheet.update(data, start_cell)

