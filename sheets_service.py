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
        self.creds = Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_FILE, scopes=self.scope
        )
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(GOOGLE_SHEET_ID).get_worksheet(0)

    def find_row_by_email(self, email: str):
        """Finds row index by matching email in column B (trimmed, case-insensitive)."""
        try:
            email_clean = email.strip().lower()
            # Find the value in column 2 (Email)
            cells = self.sheet.findall(email_clean, in_column=2)
            for cell in cells:
                if cell.value.strip().lower() == email_clean:
                    return cell.row
            return None
        except Exception as e:
            logger.error(f"Sheet Error (find_by_email): {e}")
            return None

    def find_row_by_name(self, name: str):
        """Finds row index by matching name in column A (trimmed, case-insensitive)."""
        try:
            name_clean = name.strip()
            # Case-insensitive match using regex
            import re
            pattern = re.compile(rf"^{re.escape(name_clean)}$", re.IGNORECASE)
            cell = self.sheet.find(pattern, in_column=1)
            return cell.row if cell else None
        except Exception as e:
            logger.error(f"Sheet Error (find_by_name): {e}")
            return None

    def update_sales_data(self, row_index: int, data: dict):
        """Updates the missing columns for a sales report."""
        try:
            # Mapping based on your spec:
            # Column E: Payment Plan
            # Column F: Payment Platform
            # Column G: Date
            # Column H: 1st Payment (Amount)
            # Column I: Notes
            updates = [
                {'range': f'E{row_index}', 'values': [[data['payment_plan']]]},
                {'range': f'F{row_index}', 'values': [[data['platform']]]},
                {'range': f'G{row_index}', 'values': [[data['date']]]},
                {'range': f'H{row_index}', 'values': [[data['amount']]]},
                {'range': f'I{row_index}', 'values': [[data['notes']]]},
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
