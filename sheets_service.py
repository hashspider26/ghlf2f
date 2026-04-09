import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_ID
from utils import logger

class SheetsService:
    def __init__(self):
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        import os
        import json
        google_creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        
        if google_creds_json:
            # Load from environment variable (Railway)
            creds_dict = json.loads(google_creds_json)
            self.creds = Credentials.from_service_account_info(
                creds_dict, scopes=self.scope
            )
        else:
            # Fallback to local file
            self.creds = Credentials.from_service_account_file(
                GOOGLE_SERVICE_ACCOUNT_FILE, scopes=self.scope
            )
            
        self.client = gspread.authorize(self.creds)
        
        # Flexible lookup to avoid 'WorksheetNotFound' due to spaces/dashes
        all_sheets = self.client.open_by_key(GOOGLE_SHEET_ID).worksheets()
        self.sheet = None
        for s in all_sheets:
            title = s.title.upper()
            if "MENTORSHIP" in title and "SALES" in title:
                self.sheet = s
                logger.info(f"Connected to sheet tab: '{s.title}'")
                break
        
        if not self.sheet:
            # Fallback to first sheet if keywords not found
            self.sheet = all_sheets[0]
            logger.warning(f"Could not find Mentorship Sales tab. Falling back to '{self.sheet.title}'")

    def find_row_by_email(self, email: str):
        """Finds row index by matching email in column C (Index 3)."""
        try:
            email_clean = email.strip().lower()
            # Find the value in column 3 (Email) based on screenshot
            cells = self.sheet.findall(email_clean, in_column=3)
            for cell in cells:
                if cell.value.strip().lower() == email_clean:
                    return cell.row
            return None
        except Exception as e:
            logger.error(f"Sheet Error (find_by_email): {e}")
            return None

    def find_row_by_name(self, name: str):
        """Finds row index by matching name in column B (Index 2)."""
        try:
            name_clean = name.strip()
            import re
            pattern = re.compile(rf"^{re.escape(name_clean)}$", re.IGNORECASE)
            # Full Name is column 2 based on screenshot
            cell = self.sheet.find(pattern, in_column=2)
            return cell.row if cell else None
        except Exception as e:
            logger.error(f"Sheet Error (find_by_name): {e}")
            return None

    def update_sales_data(self, row_index: int, data: dict):
        """Updates the columns based on your MENTORSHIP-SALES screenshot."""
        try:
            # Updated Mapping:
            # Column G (7): Closer's Name
            # Column J (10): Payment Plan
            # Column K (11): Payment Platform
            # Column L (12): Date
            # Column M (13): 1st Payment
            # Column O (15): Notes
            updates = [
                {'range': f'G{row_index}', 'values': [[data['closer_name']]]},
                {'range': f'J{row_index}', 'values': [[data['payment_plan']]]},
                {'range': f'K{row_index}', 'values': [[data['platform']]]},
                {'range': f'L{row_index}', 'values': [[data['date']]]},
                {'range': f'M{row_index}', 'values': [[data['amount']]]},
                {'range': f'O{row_index}', 'values': [[data['notes']]]},
            ]
            self.sheet.batch_update(updates)
            logger.info(f"Updated row {row_index} in Google Sheet.")
            return True
        except Exception as e:
            logger.error(f"Sheet Error (update_sales_data): {e}")
            return False

    def update_onboarding_status(self, row_index: int, column: str, value: str = "TRUE"):
        """Updates onboarding checkboxes (Column R for Contract, S for Course)."""
        try:
            self.sheet.update_acell(f"{column}{row_index}", value)
            logger.info(f"Updated column {column} in row {row_index} to {value}.")
            return True
        except Exception as e:
            logger.error(f"Sheet Error (update_onboarding): {e}")
            return False

sheets_service = SheetsService()
