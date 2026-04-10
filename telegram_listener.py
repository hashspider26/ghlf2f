from telegram import Update
from telegram.ext import ContextTypes
from report_parser import parse_sales_report
from sheets_service import sheets_service
from ghl_service import ghl_service
from config import CLOSERS_GROUP_ID, PROGRAMS
from utils import logger, send_va_alert
from database import save_message_tracking

async def handle_closers_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Monitors the closers group and processes 'Status: Closed' reports."""

    if not update.message or not update.message.text:
        return

    chat_id = update.message.chat_id
    text = update.message.text
    sender_name = update.message.from_user.first_name if update.message.from_user else "Unknown"
    
    # Debug logging to see what's happening
    logger.info(f"Message received from {sender_name} (Chat ID: {chat_id})")
    
    # 1. Check if message is in the correct group
    if chat_id != CLOSERS_GROUP_ID:
        logger.info(f"Ignoring message because Chat ID {chat_id} does not match CLOSERS_GROUP_ID {CLOSERS_GROUP_ID}")
        return

    # 2. Check for trigger
    if "Status: Closed" not in text:
        logger.info("Ignoring message: 'Status: Closed' trigger not found.")
        return

    logger.info(f"Sales report detected from {sender_name}, processing...")
    
    # 3. Parse Report
    data = parse_sales_report(text)
    if not data:
        await send_va_alert("Invalid format or missing fields in sales report.", text)
        return
    
    # Add closer name to data
    data['closer_name'] = sender_name

    # 2. Find Sheet Row
    row_index = sheets_service.find_row_by_email(data['email'])
    if not row_index:
        row_index = sheets_service.find_row_by_name(data['name'])
    
    if not row_index:
        await send_va_alert(f"Contact {data['email']} not found in Sheet rows.", text)
        return

    # 3. Update Sheet
    success = sheets_service.update_sales_data(row_index, data)
    if success:
        # Save the Telegram Message ID so we can reply later
        save_message_tracking(data['email'], update.message.message_id)
    else:
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
