import logging
import sys
from telegram import Bot, ReplyParameters
import asyncio
from config import TELEGRAM_BOT_TOKEN, VA_GROUP_ID

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

