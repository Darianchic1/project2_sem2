import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.settings import settings
from services.database import Database
from models import Base
from routers import router as main_router
from middlewares.admin import AdminMiddleware, BanMiddleware, UserTrackingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

async def init_db():
    db = Database()
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return db

async def main():
    db = await init_db()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    dp['db'] = db
    
    # Подключаем middleware в правильном порядке
    dp.message.middleware(UserTrackingMiddleware()) 
    dp.callback_query.middleware(UserTrackingMiddleware())
    
    dp.message.middleware(BanMiddleware()) 
    dp.callback_query.middleware(BanMiddleware())
    
    dp.message.middleware(AdminMiddleware()) 
    dp.callback_query.middleware(AdminMiddleware())
    
    dp.include_router(main_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())