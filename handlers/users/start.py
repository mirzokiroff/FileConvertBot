import asyncpg
from aiogram import types
from aiogram.types import ReplyKeyboardRemove

from data.config import ADMINS
from loader import dp, db, bot
from states.file_states import FormState


@dp.message_handler(commands=['start'], state="*")
async def bot_start(message: types.Message):
    try:
        user = await db.add_user(telegram_id=message.from_user.id,
                                 full_name=message.from_user.full_name,
                                 username=message.from_user.username,
                                 is_premium=message.from_user.is_premium
                                 )
    except asyncpg.exceptions.UniqueViolationError:
        user = await db.select_user(telegram_id=message.from_user.id)

    # Adminga xabar beramiz
    count = await db.count_users()
    msg = (f"{message.from_user.full_name} bazaga qo'shildi.\n\n"
           f"Foydalanuvchi Ma'lumotlari:\n\n"
           f"Foydalanuvchi telegram id: {message.from_user.id}\n\n"
           f"Foydalanuvchi username: {message.from_user.username}\n\n"
           f"Foydalanuvchi Premium Telegram: {message.from_user.is_premium}\n\n"
           f"Bazada {count} ta foydalanuvchi bor.")
    await bot.send_message(chat_id=ADMINS[0], text=msg)
    await message.reply(
        f"Assalomu Alaykum! {message.from_user.full_name}\nFile Converter botiga xush kelibsiz!\n\n"
        f"Siz bu Bot bilan fayllarni bir formatdan boshqasiga o'zgartirishingiz mumkin\n\n"
        f"📷 Rasmlar, 🗂 Fayllar va boshqa formatdagi fayllar qo'llab quvvatlanadi\n\n\n"
        f"Konvertatsiya qilish uchun menga faylni yuboring yoki qo'shimcha ma'lumot olish uchun /help yozing.",
        reply_markup=ReplyKeyboardRemove())
    await FormState.waiting_for_file.set()
