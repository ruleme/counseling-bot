"""
Main entry point for the Anonymous Telegram Counseling Bot.
"""

import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers import user_handlers, counselor_handlers, admin_handlers
from database import Database

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

