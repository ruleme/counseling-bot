"""
Bot instance module to avoid circular imports.
"""

from aiogram import Bot
import config

# Global bot instance
bot: Bot = None


def get_bot() -> Bot:
    """Get or create bot instance."""
    global bot
    if bot is None:
        bot = Bot(token=config.BOT_TOKEN)
    return bot


def set_bot(bot_instance: Bot):
    """Set bot instance (used by main.py)."""
    global bot
    bot = bot_instance

