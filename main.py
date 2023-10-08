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
    # await message.answer(f'[Debug data] Openai Response:\n{openai_response}')
    location, bedrooms = openai_response['args']['location'], openai_response['args']['bedrooms']
    price = openai_response['args']['price']
    meters, obj_type = openai_response['args']['meters'], openai_response['args']['type']
    location = location.replace('Antalia', 'Antalya')
    db_response = db.get_apartment_offers(location, price, bedrooms, meters, 'is_building_ready', obj_type)
    if not db_response['is_ok']:
        return await message.answer(f'{message.from_user.first_name}' + ERROR_MESSAGE)
    args = db_response['obj']
    response_text = f"{message.from_user.first_name}, по вашему запросу было найдено {len(args)} результатов."
    if len(args) == 0:
        return await message.answer(response_text)
    response_text += f'\nhttp://94.198.218.2?location={location}&price={price}&bedrooms={bedrooms}&meters={meters}&is_ready=1&apart_type={obj_type}'
    #for a in args:
    #    response_text += f"\nhttps://tolerance-homes.ru/objects/{a[0]}"
    await message.answer(response_text)


async def main():
    bot = Bot(os.getenv('TELEGRAM_TOKEN'), parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
