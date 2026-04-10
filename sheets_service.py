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
            creds_dict = json.loads(google_creds_json)
            self.creds = Credentials.from_service_account_info(
                creds_dict, scopes=self.scope
            )
        else:
            self.creds = Credentials.from_service_account_file(
                GOOGLE_SERVICE_ACCOUNT_FILE, scopes=self.scope
            )
            
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open_by_key(GOOGLE_SHEET_ID)
        
        # 1. Connect to Sales Sheet
        all_sheets = self.spreadsheet.worksheets()
        self.sales_sheet = None
        for s in all_sheets:
            title = s.title.upper()
            if "MENTORSHIP" in title and "SALES" in title:
                self.sales_sheet = s
                logger.info(f"Connected to Sales Sheet: '{s.title}'")
                break
        
        if not self.sales_sheet:
            self.sales_sheet = all_sheets[0]
            logger.warning(f"Could not find Sales tab. Falling back to '{self.sales_sheet.title}'")

        # 2. Connect to (or create) Memory Sheet
        try:
            self.memory_sheet = self.spreadsheet.worksheet("BOT_MEMORY")
            logger.info("Connected to 'BOT_MEMORY' storage sheet.")
        except gspread.WorksheetNotFound:
            self.memory_sheet = self.spreadsheet.add_worksheet(title="BOT_MEMORY", rows="1000", cols="3")
            self.memory_sheet.append_row(["Email", "Message ID", "Timestamp"])
            logger.info("Created new 'BOT_MEMORY' storage sheet.")

    def find_row_by_email(self, email: str):
        """Finds row index in Sales Sheet by matching email in column C (Index 3)."""
        try:
            email_clean = email.strip().lower()
            cells = self.sales_sheet.findall(email_clean, in_column=3)
            for cell in cells:
                if cell.value.strip().lower() == email_clean:
                    return cell.row
            return None
        except Exception as e:
            logger.error(f"Sheet Error (find_by_email): {e}")
            return None

    def find_row_by_name(self, name: str):
        """Finds row index in Sales Sheet by matching name in column B (Index 2)."""
        try:
            name_clean = name.strip()
            import re
            pattern = re.compile(rf"^{re.escape(name_clean)}$", re.IGNORECASE)
            cell = self.sales_sheet.find(pattern, in_column=2)
            return cell.row if cell else None
        except Exception as e:
            logger.error(f"Sheet Error (find_by_name): {e}")
            return None

    def update_sales_data(self, row_index: int, data: dict):
        """Updates main Sales Sheet columns."""
        try:
            updates = [
                {'range': f'G{row_index}', 'values': [[data['closer_name']]]},
                {'range': f'J{row_index}', 'values': [[data['payment_plan']]]},
                {'range': f'K{row_index}', 'values': [[data['platform']]]},
                {'range': f'L{row_index}', 'values': [[data['date']]]},
                {'range': f'M{row_index}', 'values': [[data['amount']]]},
                {'range': f'O{row_index}', 'values': [[data['notes']]]},
            ]
            self.sales_sheet.batch_update(updates)
            logger.info(f"Updated row {row_index} in Sales Sheet.")
            return True
        except Exception as e:
            logger.error(f"Sheet Error (update_sales_data): {e}")
            return False

    def update_onboarding_status(self, row_index: int, column: str, value: str = "✅"):
        """Updates onboarding status (writes ✅ by default)."""
        try:
            cell_range = f"{column}{row_index}"
            self.sales_sheet.update_acell(cell_range, value)
            logger.info(f"Updated onboarding status in {column}{row_index}")
            return True
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False

    # --- BOT MEMORY METHODS ---

    def save_message_tracking(self, email: str, message_id: int):
        """Saves message link in the hidden BOT_MEMORY sheet."""
        try:
            email_clean = email.strip().lower()
            # Try to find existing entry
            try:
                cell = self.memory_sheet.find(email_clean, in_column=1)
                if cell:
                    self.memory_sheet.update_acell(f"B{cell.row}", str(message_id))
                    logger.info(f"Updated existing memory for {email_clean}")
                    return True
            except gspread.CellNotFound:
                pass
            
            # If not found, append new row
            from datetime import datetime
            self.memory_sheet.append_row([email_clean, str(message_id), datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            logger.info(f"Added new memory entry for {email_clean}")
            return True
        except Exception as e:
            logger.error(f"Memory Save Error: {e}")
            return False

    def get_message_tracking(self, email: str):
        """Retrieves message ID from the hidden BOT_MEMORY sheet."""
        try:
            email_clean = email.strip().lower()
            cell = self.memory_sheet.find(email_clean, in_column=1)
            if cell:
                val = self.memory_sheet.acell(f"B{cell.row}").value
                return int(val) if val else None
            return None
        except gspread.CellNotFound:
            return None
        except Exception as e:
            logger.error(f"Memory Get Error: {e}")
            return None

sheets_service = SheetsService()
