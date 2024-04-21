import logging

import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from environs import Env  # noqa

from loader import dp, bot, db
from states.personalData import Admin

env = Env()
env.read_env()

ADMIN_IDS = env.list("ADMINS")


@dp.message_handler(commands="admin", state='*')
async def admin_handler(message: types.Message):
    is_admin = False
    for admin in ADMIN_IDS:
        if message.from_user.id == int(admin):
            is_admin = True
            break

    if is_admin and message.text == '/admin':
        await message.answer(f"Hello {message.from_user.first_name} 🤖\nWelcome to Admin page ⚙️",
                             reply_markup=types.ReplyKeyboardRemove())

        await message.reply("Iltimos, quyidagilardan birini tanlang !",
                            reply_markup=types.ReplyKeyboardMarkup(
                                keyboard=[
                                    [types.KeyboardButton(text="advertising"),
                                     types.KeyboardButton(text="Guruh qo'shish ➕")],
                                    [types.KeyboardButton(text="Guruhlar"),
                                     types.KeyboardButton(text="Guruh o'chirish ❌")],
                                ], resize_keyboard=True
                            ))
        await Admin.video.set()

    else:
        await message.answer("You are not Admin ❌")


@dp.message_handler(state=Admin.video)
async def send_advertisement(message: types.Message):
    text = message.text
    if text == "advertising":

        await message.reply("Tayyor Reklamani Jo'nating!", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Bekor qilish ❌")]], resize_keyboard=True))
        await Admin.reklama.set()

    elif text == "Guruh qo'shish ➕":

        await message.reply("Guruh ID ni va Nomini kiriting:"
                            "\n\nQuyidagi korinishda kiriting: 1234567890123, Guruh_Nomi",
                            reply_markup=types.ReplyKeyboardMarkup(
                                keyboard=[
                                    [types.KeyboardButton(text="Bekor qilish ❌")]
                                ], resize_keyboard=True
                            ))
        await Admin.add_group.set()

    elif text == "Guruhlar":

        channels = await db.select_all_channel()

        await message.answer("Sizning adminlikka ega bo'lgan guruhlar:", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="advertising"), types.KeyboardButton(text="Guruh qo'shish ➕")],
                [types.KeyboardButton(text="Guruhlar"), types.KeyboardButton(text="Guruh o'chirish ❌")],
            ], resize_keyboard=True
        ))
        await Admin.video.set()

        for chat_id in channels:
            await message.answer(f"Guruh ID va Nomi: {chat_id['chat_id']}"
                                 f"\n\nGuruhni o'chirish uchun ID : {chat_id['id']}")

    elif text == "Guruh o'chirish ❌":
        channels = await db.select_all_channel()
        for chat_id in channels:
            await message.answer(f"Guruh ID va Nomi: {chat_id['chat_id']}"
                                 f"\n\nGuruhni o'chirish uchun ID : {chat_id['id']}")
        await message.reply("Guruhni o'chirish uchun ID kiriting !")
        await Admin.delete_channel.set()
    else:

        await message.reply("Iltimos, advertising nomli tugmani yoki Guruh qo'shish tugmasini bosing !!!")


@dp.message_handler(state=Admin.reklama, content_types=types.ContentType.ANY)
async def handle_reklama(msg: types.Message, state: FSMContext):
    if msg.text == "Bekor qilish ❌":
        await msg.answer("Bekor qilindi ☑️")
        await msg.reply(
            "Istasangiz yana Istalgan Reklamani yuborishingiz mumkun\n\n"
            "Eslatma!!! Siz nima yuborsangiz kanallarga ham yuboriladi",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text="advertising"), types.KeyboardButton(text="Guruh qo'shish ➕")],
                    [types.KeyboardButton(text="Guruhlar"), types.KeyboardButton(text="Guruh o'chirish ❌")],
                ], resize_keyboard=True
            ))
        await Admin.video.set()
    else:
        await bot.send_message(chat_id=msg.chat.id, text="Reklama yuborish boshlandi 🤖✅")
        try:
            channels = await db.select_all_channel()
            for chat_id in channels:
                try:
                    await msg.copy_to(chat_id['chat_id'], caption=msg.caption, caption_entities=msg.caption_entities,
                                      reply_markup=msg.reply_markup)
                except aiogram.exceptions.ChatNotFound as e:
                    print(f"Group with ID {chat_id['chat_id']} not found >>> {e}")
                except aiogram.exceptions.BotBlocked as e:
                    logging.warning(f"Bot is blocked in group with ID {chat_id['chat_id']} >>> {e}")

            await msg.answer("Reklama barcha admin bo'lgan guruhlarga muvaffaqiyatli yuborildi!")

            await msg.reply(
                "Istasangiz yana Istalgan Reklamani yuborishingiz mumkun\n\n"
                "Eslatma!!! Siz nima yuborsangiz foydalanuvchilarga ham yuboriladi",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text="advertising"), types.KeyboardButton(text="Guruh qo'shish ➕")],
                        [types.KeyboardButton(text="Guruhlar"), types.KeyboardButton(text="Guruh o'chirish ❌")],
                    ], resize_keyboard=True
                ))
            await Admin.video.set()
        except Exception as e:
            print(f"Error: {e}")


@dp.message_handler(state=Admin.add_group)
async def add_group_handler(message: types.Message):
    try:
        if message.text == "Bekor qilish ❌":
            await message.answer("Bekor qilindi ☑️", reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text="advertising"), types.KeyboardButton(text="Guruh qo'shish ➕")],
                    [types.KeyboardButton(text="Guruhlar"), types.KeyboardButton(text="Guruh o'chirish ❌")],
                ], resize_keyboard=True
            ))
        else:
            group_id = message.text
            channels = await db.select_channel(chat_id=group_id)
            if group_id not in channels['chat_id']:
                await db.add_channel(chat_id=group_id)
                await message.reply(f"Guruh {group_id} muvaffaqiyatli qo'shildi!",
                                    reply_markup=types.ReplyKeyboardMarkup(
                                        keyboard=[
                                            [types.KeyboardButton(text="advertising"),
                                             types.KeyboardButton(text="Guruh qo'shish ➕")],
                                            [types.KeyboardButton(text="Guruhlar"),
                                             types.KeyboardButton(text="Guruh o'chirish ❌")],
                                        ], resize_keyboard=True
                                    ))
                await Admin.video.set()
            else:
                await message.reply("Kechirasiz, bu Guruh qo'shilgan!", reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text="advertising"), types.KeyboardButton(text="Guruh qo'shish ➕")],
                        [types.KeyboardButton(text="Guruhlar"), types.KeyboardButton(text="Guruh o'chirish ❌")],
                    ], resize_keyboard=True
                ))
                await Admin.video.set()
    except ValueError:
        await message.reply("Noto'g'ri guruh ID kiritildi. Iltimos, faqat sonlarni kiriting!")


@dp.message_handler(state=Admin.delete_channel)
async def delete_channel(message: types.Message):
    try:
        group_id = int(message.text)
        await db.delete_channel(group_id)
        await message.reply("Guruh muvaffaqiyatli o'chirildi!", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="advertising"), types.KeyboardButton(text="Guruh qo'shish ➕")],
                [types.KeyboardButton(text="Guruhlar"), types.KeyboardButton(text="Guruh o'chirish ❌")],
            ], resize_keyboard=True
        ))
        await Admin.video.set()
    except ValueError:
        await message.reply("Noto'g'ri guruh ID kiritildi yoki topilmadi !")
