import asyncio
import logging
import os

import db
import openai_api
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
import dotenv

dotenv.load_dotenv()
dp = Dispatcher()

HELLO_MESSAGE = """Привет!
\nНапишите ваш запрос, он должен включать следующую информацию:
\n1) Статус (объект готов или на этапе строительства)
\n2) Количество комнат
\n3) Бюджет
\n4) Локацию (город)
\n\nПример: Я хочу готовую квартиру в Анталье с 4 спальнями стоимостью до 100000$
"""

ERROR_MESSAGE = """
, ваш запрос не был обработан.
\nК сожалению мы не смогли точно разобрать критерии вашего поиска.
\nПожалуйста, напишите запрос подробнее и согласно критериям.
"""


@dp.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer(HELLO_MESSAGE)


@dp.message()
async def on_all_messages(message: types.Message):
    openai_response = openai_api.get_keywords_values(message.text)
    if not openai_response['is_ok']:
        return await message.answer(message.from_user.first_name + ERROR_MESSAGE)
    a = openai_response['args']
    types = [1, 69, 70, 71, 72, 114, 121]
    try:
        index = types[int(a['bedrooms']) - 1]
    except:
        return message.answer("Некорректный запрос!")
    url = 'https://tolerance-homes.ru/turcia/' + a['location'] + '/' + a['type'] + f"/?&price-max={a['price']}+%24&ap-types[{index}]=1"
    return message.answer(url)
async def main():
    bot = Bot(os.getenv('TELEGRAM_TOKEN'), parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
