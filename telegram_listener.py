from telegram import Update
from telegram.ext import ContextTypes
from report_parser import parse_sales_report
from sheets_service import sheets_service
from ghl_service import ghl_service
from config import CLOSERS_GROUP_ID, PROGRAMS
from utils import logger, send_va_alert

async def handle_closers_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monitors the closers group and processes 'Status: Closed' reports."""
    if not update.message or not update.message.text:
        return

    # Check if message is in the correct group and contains trigger
    if update.message.chat_id != CLOSERS_GROUP_ID:
        return

    text = update.message.text
    if "Status: Closed" not in text:
        return

    logger.info("Sales report detected, processing...")
    
    # 1. Parse Report
    data = parse_sales_report(text)
    if not data:
        await send_va_alert("Invalid format or missing fields in sales report.", text)
        return

    # 2. Find Sheet Row
    row_index = sheets_service.find_row_by_email(data['email'])
    if not row_index:
        row_index = sheets_service.find_row_by_name(data['name'])
    
    if not row_index:
        await send_va_alert(f"Contact {data['email']} not found in Sheet rows.", text)
        return

    # 3. Duplicate Check: Verify if Column E is already filled
    try:
        existing_val = sheets_service.sheet.cell(row_index, 5).value # Column E: Payment Plan
        if existing_val:
            logger.info(f"Duplicate detected for {data['email']} at Row {row_index}. Skipping.")
            return
    except Exception as e:
        logger.error(f"Error checking duplicate: {e}")

    # 4. Update Sheet
    success = sheets_service.update_sales_data(row_index, data)
    if not success:
        await send_va_alert("Failed to update Google Sheet row.", text)
        return

    # 5. Apply GHL Tag
    ghl_contact = ghl_service.get_contact_by_email(data['email'])
    if ghl_contact:
        tag = PROGRAMS['default']['tags'].get(data['payment_plan'])
        if tag:
            ghl_service.apply_tag(ghl_contact['id'], tag)
        else:
            await send_va_alert(f"No tag mapping found for plan {data['payment_plan']}", text)
    else:
        await send_va_alert(f"Contact {data['email']} not found in GHL.", text)

    logger.info("Sales report processed successfully.")
