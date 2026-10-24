"""Run one polling worker with recoverable sessions and a readiness endpoint."""
import asyncio
import contextlib
import logging
import os

import config
from keep_alive import Health, start_health_server

logger = logging.getLogger(__name__)


async def monitor(health, bot, db):
    while True:
        try:
            await asyncio.wait_for(bot.get_me(), timeout=15)
            def check_database():
                with contextlib.closing(db.get_connection()) as conn:
                    conn.execute("SELECT 1").fetchone()
            await asyncio.to_thread(check_database)
            health.mark_ready()
        except Exception:
            health.unavailable()
            logger.warning("Readiness check failed")
        await asyncio.sleep(30)


async def main():
    config.validate()
    from aiogram import Bot, Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
    from bot_instance import set_bot
    from database import Database
    from handlers import admin_handlers, counselor_handlers, user_handlers
    from utils.middleware import PrivateChatMiddleware

    bot = Bot(token=config.BOT_TOKEN)
    set_bot(bot)
    dp = Dispatcher(storage=MemoryStorage(), events_isolation=SimpleEventIsolation())
    dp.message.outer_middleware(PrivateChatMiddleware())
    dp.include_router(admin_handlers.router)
    dp.include_router(counselor_handlers.router)
    dp.include_router(user_handlers.router)
    db = Database()
    health = Health()
    server = start_health_server(health, int(os.getenv("PORT", "8080")))
    task = asyncio.create_task(monitor(health, bot, db))
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        logger.info("Starting polling worker")
        await dp.start_polling(bot, close_bot_session=False)
    finally:
        health.unavailable()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        await asyncio.to_thread(server.shutdown)
        server.server_close()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    # Do not expose request URLs containing the bot token through HTTP logs.
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
