import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Добавляем App в пути

import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from database.database import create_db, session_maker
from handlers.register import register
from handlers.login import login
from middlewares.db import DataBaseSession


load_dotenv()
 

async def main():
    await create_db()
    dp = Dispatcher()
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_routers(register, login)
    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print('Бот включен!')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен!')
