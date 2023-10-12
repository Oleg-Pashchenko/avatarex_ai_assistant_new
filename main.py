import asyncio
import os

import requests

import openai_api
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
import dotenv
import messages

dotenv.load_dotenv()
dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer(messages.HELLO_MESSAGE)


@dp.message()
async def on_all_messages(message: types.Message):
    openai_response = openai_api.get_keywords_values(message.text)
    if not openai_response['is_ok']:
        return await message.answer(messages.ERROR_MESSAGE(message.from_user.first_name))
    a = openai_response['args']
    types = [1, 69, 70, 71, 72, 114, 121]
    try:
        index = types[int(a['bedrooms'])]
    except:
        return message.answer(messages.ERROR_MESSAGE(message.from_user.first_name))
    if a['type'] == 'kvartiri':
        url = 'https://tolerance-homes.ru/turcia/' + a['location'] + '/' + a[
            'type'] + f"/?&price-max={a['price']}+%24&ap-types[{index}]=1"
    else:
        url = 'https://tolerance-homes.ru/turcia/' + a['location'] + '/' + a[
            'type'] + f"/?&price-max={a['price']}+%24"
    response = requests.get(url).text
    if int(response.split('Найдено ')[1].split()[0].replace('</b>', '').replace('<b>', '')) == 0:
        return message.answer(messages.ERROR_MESSAGE_ZERO_RESULT(message.from_user.first_name))
    return message.answer(messages.SUCCESS_MESSAGE(message.from_user.first_name, url))


async def main():
    bot = Bot(os.getenv('TELEGRAM_TOKEN'), parse_mode=ParseMode.MARKDOWN)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
