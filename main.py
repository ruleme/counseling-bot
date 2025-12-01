"""
Main entry point for the Anonymous Telegram Counseling Bot.
Includes Flask web server for Replit keep-alive.
"""

import logging
import asyncio
from threading import Thread
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask

import config
from handlers import user_handlers, counselor_handlers, admin_handlers
from database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
from bot_instance import get_bot, set_bot

bot = Bot(token=config.BOT_TOKEN)
set_bot(bot)  # Set global bot instance
dp = Dispatcher(storage=MemoryStorage())

# Initialize database
db = Database()

# Flask app for keep-alive (Replit)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Counseling Bot is running!"

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}

def run_flask():
    """Run Flask server in a separate thread."""
    app.run(host='0.0.0.0', port=8080)

async def main():
    """Main function to start the bot."""
    # Register routers (admin first so commands are processed before state handlers)
    dp.include_router(admin_handlers.router)
    dp.include_router(counselor_handlers.router)
    dp.include_router(user_handlers.router)
    
    logger.info("Bot starting...")
    
    # Check if admin ID is set
    if config.ADMIN_ID == 0:
        logger.warning("⚠️ ADMIN_ID is not set! Please set it in config.py or environment variable.")
    
    # Check if bot token is set
    if config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN is not set! Please set it in config.py or environment variable.")
        return
    
    # Start polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    # Start Flask server in background thread (for Replit keep-alive)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started on port 8080")
    
    # Start bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
