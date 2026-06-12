import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN, SENTRY_DSN
from bot.database import init_db
from bot.handlers import commands_router, content_router, payments_router
from bot.middleware import RateLimitMiddleware

if SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Установите переменную окружения.")
        return
    
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.message.middleware(RateLimitMiddleware(limit=5, period=60))
    dp.callback_query.middleware(RateLimitMiddleware(limit=10, period=60))
    
    dp.include_router(commands_router)
    dp.include_router(content_router)
    dp.include_router(payments_router)
    
    logger.info("Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())