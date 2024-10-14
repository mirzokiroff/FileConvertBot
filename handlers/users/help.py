from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp(), state="*")
async def bot_help(message: types.Message):
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam",
            "Fikr, Taklif yoki Savolingiz bo'lsa @mirzokirov1 ga murojaat qilishingiz mumkun!")
    
    await message.answer("\n".join(text))