import asyncio
import uvicorn
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from telegram_listener import handle_closers_message
from webhook_server import app
from utils import logger

async def run_bot():
    """Starts the Telegram bot."""
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handler for messages
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_closers_message))
    
    logger.info("Starting Telegram Bot...")
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        # Keep running until cancelled
        while True:
            await asyncio.sleep(1)

async def run_web_server():
    """Starts the FastAPI webhook server."""
    import os
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting FastAPI Webhook Server on port {port}...")
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Main runner to orchestrate bot and server."""
    # Run both services concurrently
    await asyncio.gather(
        run_bot(),
        run_web_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System shutting down...")
