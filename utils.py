import logging
import sys
from telegram import Bot, ReplyParameters
import asyncio
from config import TELEGRAM_BOT_TOKEN, VA_GROUP_ID, CLOSERS_GROUP_ID

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TelegramAutomation")

async def send_va_alert(message: str, original_text: str = None):
    """Sends an alert to the internal VA Telegram group."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    alert_text = f"⚠ *Human intervention required*\n\n{message}"
    if original_text:
        alert_text += f"\n\n*Original Message:*\n`{original_text}`"
    
    try:
        await bot.send_message(
            chat_id=VA_GROUP_ID, 
            text=alert_text, 
            parse_mode='Markdown'
        )
        logger.warning(f"VA Alert sent: {message}")
    except Exception as e:
        logger.error(f"Failed to send VA alert: {e}")

async def send_public_notification(text: str, va_text: str = None, reply_to_message_id: int = None):
    """Sends a notification to both Closers and VA groups with potentially different wording."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # 1. To Closers Group (Exact wording as reply)
    try:
        reply_params = ReplyParameters(message_id=reply_to_message_id) if reply_to_message_id else None
        await bot.send_message(
            chat_id=CLOSERS_GROUP_ID,
            text=text,
            reply_parameters=reply_params
        )
    except Exception as e:
        logger.error(f"Failed to send msg to Closers group: {e}")

    # 2. To VA Group (Detailed version for log)
    try:
        final_va_text = va_text if va_text else text
        await bot.send_message(
            chat_id=VA_GROUP_ID,
            text=final_va_text
        )
    except Exception as e:
        logger.error(f"Failed to send msg to VA group: {e}")

async def send_telegram_reply(chat_id: int, message_id: int, text: str):
    """Sends a reply to a specific message in a chat."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_parameters=ReplyParameters(message_id=message_id)
        )
        logger.info(f"Sent reply to message {message_id} in {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send reply to {message_id}: {e}")

