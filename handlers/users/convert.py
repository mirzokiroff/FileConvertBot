import os

import convertapi
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from environs import Env

from loader import dp, bot
from states.file_states import FormState

env = Env()
env.read_env()

convertapi.api_credentials = env.str('convertapi')


@dp.message_handler(state=FormState.waiting_for_file, content_types=types.ContentTypes.ANY)
async def document_handler(message: types.Message, state: FSMContext):
    if message.content_type == 'document':
        document = message.document
        file_id = document.file_id
        file = await bot.get_file(file_id)

        file_path = f"./documents/{document.file_name}"
        await bot.download_file(file.file_path, file_path)

        await state.update_data(file_path=file_path)
        await message.answer("Fayl qabul qilindi. O'tkazish uchun formatlarni tanlang.",
                             reply_markup=await get_conversion_buttons(document.file_name))
        await FormState.waiting_for_format.set()

    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)

        file_path = f"./documents/image.jpg"
        await bot.download_file(file.file_path, file_path)

        await state.update_data(file_path=file_path)
        await message.answer("Rasm qabul qilindi. O'tkazish uchun formatlarni tanlang.",
                             reply_markup=await get_conversion_buttons('image.jpg'))
        await FormState.waiting_for_format.set()
    elif message.content_type == 'video':
        video = message.video
        file_id = video.file_id
        file = await bot.get_file(file_id)

        file_path = f"./documents/{video.file_name}"
        await bot.download_file(file.file_path, file_path)

        await state.update_data(file_path=file_path)
        await message.answer("Video qabul qilindi. O'tkazish uchun formatlarni tanlang.",
                             reply_markup=await get_conversion_buttons(video.file_name))
        await FormState.waiting_for_format.set()

    elif message.content_type == 'sticker':
        sticker = message.sticker
        file_id = sticker.file_id
        file = await bot.get_file(file_id)

        file_path = f"./documents/{sticker.file_unique_id}.webp"

        await bot.download_file(file.file_path, file_path)

        await state.update_data(file_path=file_path)

        await message.answer("Sticker qabul qilindi. O'tkazish uchun formatlarni tanlang.",
                             reply_markup=await get_conversion_buttons(sticker.file_unique_id))

        await FormState.waiting_for_format.set()


@dp.message_handler(state=FormState.waiting_for_format)
async def format_handler(message: types.Message, state: FSMContext):
    selected_format = message.text

    user_data = await state.get_data()
    file_path = user_data.get('file_path')
    print(file_path)

    original_extension = os.path.splitext(file_path)[-1].lower().strip('.')

    conversion_map = {
        # Image formats
        'png': ['jpg', 'pdf', 'pnm', 'webp', 'tiff', 'gif', 'png', 'svg', 'jpeg'],
        'jpg': ['png', 'pdf', 'webp', 'tiff', 'gif', 'jpeg', 'pnm', 'jpg', 'svg', 'jxl'],
        'jpeg': ['png', 'pdf', 'webp', 'tiff', 'gif', 'jpg', 'pnm', 'svg'],
        'bmp': ['jpg', 'png', 'pdf', 'webp', 'tiff', 'svg', 'pnm'],
        'gif': ['png', 'jpg', 'pnm', 'pdf', 'webp', 'tiff', 'svg', 'gif'],
        'tiff': ['jpg', 'png', 'tiff', 'webp', 'pdf', 'pnm', 'svg'],
        'webp': ['jpg', 'png', 'pdf', 'webp', 'gif', 'tiff', 'pnm', 'svg'],

        # Document formats
        'doc': ['pdf', 'jpg', 'html', 'rtf', 'xps', 'txt', 'odt', 'doc', 'docx', 'xml'],
        'docx': ['pdf', 'txt', 'html', 'odt', 'png', 'webp', 'jpg', 'doc', 'docx', 'xml', 'rtf', 'tiff'],
        'pdf': ['xlsx', 'docx', 'html', 'pptx', 'csv', 'jpg', 'ocr', 'pdf', 'png', 'tiff', 'svg', 'txt', 'webp'],
        'txt': ['jpg'],
        'html': ['pdf', 'jpg', 'docx', 'md', 'odt', 'xlsx', 'xls', 'txt', 'png'],
        'odt': ['pdf', 'doc', 'txt', 'docx', 'png', 'webp', 'jpg', 'xml', 'rtf', 'xps', 'tiff', 'odt'],
        'ppt': ['pdf', 'pptx', 'jpg', 'png', 'tiff', 'webp'],
        'pptx': ['pdf', 'jpg', 'png', 'key', 'tiff', 'webp', 'pptx'],
        'odp': ['png', 'tiff', 'webp', 'jpg', ''],
        'key': ['png', 'tiff', 'pptx', 'jpg', 'pdf'],

        # Video formats
        'mp4': ['avi', 'mkv', 'webm', 'mov', 'flv'],
        'avi': ['mp4', 'mkv', 'webm', 'mov', 'flv'],
        'mkv': ['mp4', 'avi', 'webm', 'mov', 'flv'],
        'mov': ['mp4', 'avi', 'mkv', 'webm', 'flv'],
        'flv': ['mp4', 'avi', 'mkv', 'webm', 'mov'],
        'webm': ['mp4', 'avi', 'mkv', 'mov', 'flv'],

        # Other formats
        'svg': ['pnm', 'jpg', 'svg', 'png', 'tiff', 'webp', 'pdf'],
        'eps': ['png', 'jpg', 'pdf', 'tiff', 'webp'],
        'psd': ['pnm', 'svg', 'jpg', 'tiff', 'png', 'webp'],
    }

    if not os.path.exists(file_path):
        await message.answer(
            "Fayl topilmadi yoki yuklanmagan.\n\nIltimos qaytadan urinib ko'ring yoki dasturchiga aloqaga chiqing ☺️"
            "\n\nDasturchi: @mirzokirov1")
        return

    if selected_format in conversion_map.get(original_extension, []):
        try:
            if selected_format == 'jpeg' and original_extension == 'jpg':
                output_path = file_path.replace('.jpg', '.jpeg')
                os.rename(file_path, output_path)

                with open(output_path, 'rb') as converted_file:
                    await message.answer_document(converted_file)

                os.remove(output_path)
                os.remove(file_path)
            else:
                if selected_format == 'gif':
                    result = convertapi.convert(selected_format, {
                        'Files': [file_path]
                    })
                else:
                    result = convertapi.convert(selected_format, {
                        'File': file_path
                    })

                output_file_name = os.path.basename(file_path)
                output_path = f'./finish_file/{os.path.splitext(output_file_name)[0]}.{selected_format}'

                result.save_files(output_path)

                with open(output_path, 'rb') as converted_file:
                    await message.answer_document(converted_file)

                os.remove(output_path)
                os.remove(file_path)

                await message.answer("Istasangiz yana fayl yuborib davom etishingiz mumkun ☺️",
                                     reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            await message.answer(
                f"Xatolik yuz berdi: Iltimos biror xatolik paytdo bo'lgan bo'lsa\n\n@mirzokirov1 ga murojaat qiling")
    else:
        await message.answer("Tanlangan formatga o'tkazish mumkin emas. Iltimos, boshqa formatni tanlang.☺")

    await FormState.waiting_for_file.set()


async def get_conversion_buttons(file_name):
    # Qo'llab-quvvatlanadigan formatlar ro'yxati
    conversion_map = {
        # Image formats
        'png': ['jpg', 'pdf', 'pnm', 'webp', 'tiff', 'gif', 'png', 'svg', 'jpeg'],
        'jpg': ['png', 'pdf', 'webp', 'tiff', 'gif', 'jpeg', 'pnm', 'jpg', 'svg', 'jxl'],
        'jpeg': ['png', 'pdf', 'webp', 'tiff', 'gif', 'jpg', 'pnm', 'svg'],
        'bmp': ['jpg', 'png', 'pdf', 'webp', 'tiff', 'svg', 'pnm'],
        'gif': ['png', 'jpg', 'pnm', 'pdf', 'webp', 'tiff', 'svg', 'gif'],
        'tiff': ['jpg', 'png', 'tiff', 'webp', 'pdf', 'pnm', 'svg'],
        'webp': ['jpg', 'png', 'pdf', 'webp', 'gif', 'tiff', 'pnm', 'svg'],

        # Document formats
        'doc': ['pdf', 'jpg', 'html', 'rtf', 'xps', 'txt', 'odt', 'doc', 'docx', 'xml'],
        'docx': ['pdf', 'txt', 'html', 'odt', 'png', 'webp', 'jpg', 'doc', 'docx', 'xml', 'rtf', 'tiff'],
        'pdf': ['xlsx', 'docx', 'html', 'pptx', 'csv', 'jpg', 'ocr', 'pdf', 'png', 'tiff', 'svg', 'txt', 'webp'],
        'txt': ['jpg'],
        'html': ['pdf', 'jpg', 'docx', 'md', 'odt', 'xlsx', 'xls', 'txt', 'png'],
        'odt': ['pdf', 'doc', 'txt', 'docx', 'png', 'webp', 'jpg', 'xml', 'rtf', 'xps', 'tiff', 'odt'],
        'ppt': ['pdf', 'pptx', 'jpg', 'png', 'tiff', 'webp'],
        'pptx': ['pdf', 'jpg', 'png', 'key', 'tiff', 'webp', 'pptx'],
        'odp': ['png', 'tiff', 'webp', 'jpg'],
        'key': ['png', 'tiff', 'pptx', 'jpg', 'pdf'],

        # Video formats
        'mp4': ['avi', 'mkv', 'webm', 'mov', 'flv'],
        'avi': ['mp4', 'mkv', 'webm', 'mov', 'flv'],
        'mkv': ['mp4', 'avi', 'webm', 'mov', 'flv'],
        'mov': ['mp4', 'avi', 'mkv', 'webm', 'flv'],
        'flv': ['mp4', 'avi', 'mkv', 'webm', 'mov'],
        'webm': ['mp4', 'avi', 'mkv', 'mov', 'flv'],

        # Other formats
        'svg': ['pnm', 'jpg', 'svg', 'png', 'tiff', 'webp', 'pdf'],
        'eps': ['png', 'jpg', 'pdf', 'tiff', 'webp'],
        'psd': ['pnm', 'svg', 'jpg', 'tiff', 'png', 'webp'],
    }

    # Fayl kengaytmasini aniqlash
    file_extension = os.path.splitext(file_name)[-1].lower().strip('.')

    # Tegishli formatlar ro'yxatini olish
    supported_formats = conversion_map.get(file_extension, [])

    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)

    buttons = [KeyboardButton(fmt) for fmt in supported_formats]
    keyboard.add(*buttons)

    return keyboard
