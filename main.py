import asyncio
import logging
from aiogram.types import BotCommand
import config, db
from bot_instance import bot, dp
import common, ads, admin  # مطمئن شو پوشه handlers ساخته باشی
from fastapi import FastAPI
from contextlib import asynccontextmanager
import db
logging.basicConfig(level=logging.INFO)

async def set_commands():
    await bot.set_my_commands([BotCommand(command="start", description="شروع")])
@asynccontextmanager
async def lifespan(app:FastAPI):
    await db.init()
    print("connected to postgres")
    yield
    await db.close_db()
    print("disconnected")
app=FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return{"message":"Fastapi is running"}
async def main():
    db.init_pool()
    dp.include_router(common.router)
    dp.include_router(ads.router)
    dp.include_router(admin.router)
    await set_commands()
    print("ربات روشن شد...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())