import logging
import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from environs import Env

from loader import db
from loader import dp, bot
from states.admin_states import Admin

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

    if is_admin:
        await message.answer(f"Assalomu alaykum {message.from_user.first_name} 🤖\nAdmin sahifaga xush kelibsiz ⚙️",
                             reply_markup=types.ReplyKeyboardRemove())

        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Xabar yuborish")],
            ],
            resize_keyboard=True
        )

        await message.answer("Admin paneliga xush kelibsiz!", reply_markup=kb)
        await Admin.message.set()
    else:
        await message.answer("Kechirasiz, siz admin emassiz.")


# "Xabar yuborish" tugmasi bosilganda
@dp.message_handler(state=Admin.message)
async def admin_message(message: types.Message):
    if message.text == "Xabar yuborish":
        await message.reply("Tayyor Xabarni Jo'nating!", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Bekor qilish")]], resize_keyboard=True))
        await Admin.reklama.set()


@dp.message_handler(state=Admin.reklama, content_types=types.ContentType.ANY)
async def handle_reklama(msg: types.Message, state: FSMContext):
    all_users = await db.select_all_users()
    if msg.text == "Bekor qilish":
        await msg.answer("Bekor qilindi")  # noqa

        await msg.reply(
            "Istasangiz yana Istalgan Reklamani yuborishingiz mumkun\n\n"
            "Eslatma!!! Siz nima yuborsangiz foydalanuvchilarga ham yuboriladi",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[[types.KeyboardButton(text="Xabar yuborish")]],
                resize_keyboard=True, row_width=True
            ))
        await Admin.message.set()
    else:
        await bot.send_message(chat_id=msg.chat.id, text="Reklama yuborish boshlandi 🤖✅")
        try:
            summa = 0
            blocked_users = []
            for user in all_users:
                user_id = user['id']
                try:
                    if int(user['telegram_id']) != 5467465403:
                        await msg.copy_to(int(user['telegram_id']), caption=msg.caption,
                                          caption_entities=msg.caption_entities, reply_markup=msg.reply_markup)
                        summa += 1
                except aiogram.exceptions.ChatNotFound as e:
                    print(f"User with ID {user_id} User with Username "
                          f"{user['full_name']} not found >>> {e}")
                    blocked_users.append(user['full_name'])
                except aiogram.exceptions.BotBlocked as e:
                    logging.warning(f"User with ID {user_id}, User with Username {user['full_name']} >>> {e}")
                except aiogram.exceptions.UserDeactivated as e:
                    logging.warning(f"User with ID {user_id}, User with Username {user['full_name']} >>> {e}")

            await bot.send_message(ADMIN_IDS[0], text=f"Botni bloklagan yoki topilmagan Userlar soni: {summa}"
                                                      f"\n\nBotni bloklagan yoki topilmagan Userlar: {blocked_users}")
            await state.finish()
            await msg.answer("Reklama barcha foydalanuvchilarga muvaffaqiyatli yuborildi!")

            await msg.reply(
                "Istasangiz yana Istalgan Reklamani yuborishingiz mumkun\n\n"
                "Eslatma!!! Siz nima yuborsangiz foydalanuvchilarga ham yuboriladi",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[[types.KeyboardButton(text="Xabar yuborish")]],
                    resize_keyboard=True, row_width=True
                ))
            await Admin.message.set()
        except Exception as e:
            print(f"Error: {e}")
