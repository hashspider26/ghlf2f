
import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, CLOSERS_GROUP_ID

async def test_reply():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    # We need a real message ID to test a reply, but we can try sending a normal message 
    # and then replying to it if we had the ID.
    # For now, let's just check if the syntax in utils.py would cause an error.
    
    chat_id = CLOSERS_GROUP_ID
    # This is a dummy message ID just to see if the call fails due to argument mismatch
    message_id = 1 
    text = "Test reply"
    
    print(f"Testing reply to {message_id} in {chat_id}...")
    try:
        # In PTB v20+, reply_to_message_id is still a valid kwarg for send_message
        # but it's recommended to use reply_parameters.
        # Let's see if it works.
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=message_id
        )
    except Exception as e:
        print(f"Caught expected/unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_reply())
