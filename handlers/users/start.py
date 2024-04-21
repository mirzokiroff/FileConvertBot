from aiogram import types

from loader import dp


@dp.message_handler(commands=['start'], state="*")
async def bot_start(message: types.Message):
    await message.reply(
        f"Assalomu Alaykum! {message.from_user.full_name}\nPost to Channels botiga xush kelibsiz!")

    # if message.text == '/start':
    #     await message.answer(
    #         "Iltimos, Botdan foydalanish uchun Tilni tanlang\n\n"
    #         "Пожалуйста, выберите язык для использования бота", )
