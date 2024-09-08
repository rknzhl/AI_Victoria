import aiohttp
import asyncio
import logging
import sys
import os

from db import DataBase

import other_part_of_core

from aiogram import Bot, Dispatcher, html, Router, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from pydub import AudioSegment
from random import randint

from config import API_TOKEN, DOWNLOAD_DIR, FORMATTED_DIR, RESULT_PATH

dp = Dispatcher()
router = Router()

dp.include_router(router)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

params = {
    "formal": 1,
    "discussion_context": 1,
    "timecodes": 1,
    "list_of_orders": 1,
    "need_password": 0
}

db = DataBase(params)

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    db.add_user(message.from_user.id)
    await message.answer(f"Добрый день, {html.bold(message.from_user.full_name)}!")

@router.message(F.voice | F.audio)
async def handle_voice_message(message: types.Message):
    if message.voice:
        file_id = message.voice.file_id
        real_name = f"{file_id}_{message.voice.file_unique_id}.ogg"
        mime = "audio/x-vorbis+ogg"
    else:
        file_id = message.audio.file_id
        real_name = f"{message.audio.file_unique_id}_{message.audio.file_name}"
        mime = message.audio.mime_type

    try:
        file = await bot.download(file_id)
        file_path = os.path.join(DOWNLOAD_DIR, f"{real_name}")
    except Exception as e:
        await message.reply("К сожалению, при загрузке вашего файла возникли проблемы")
        os.remove(file_path)
        return
        
    with open(file_path, 'wb') as f:
        f.write(file.read())

    try:
        if mime == "audio/mpeg":
            wav_path = os.path.join(FORMATTED_DIR, f"{file_id}.wav")
            audio = AudioSegment.from_file(file_path, format="mp3")
            audio.export(wav_path, format="wav")
        elif mime == "audio/mp4":
            wav_path = os.path.join(FORMATTED_DIR, f"{file_id}.wav")
            audio = AudioSegment.from_file(file_path, format="m4a")
            audio.export(wav_path, format="wav")
        elif mime == "audio/x-vorbis+ogg":
            wav_path = os.path.join(FORMATTED_DIR, f"{file_id}.wav")
            audio = AudioSegment.from_file(file_path, format="ogg")
            audio.export(wav_path, format="wav")
        else:
            await message.reply("Извините, данное расширение пока не поддерживается")
            os.remove(file_path)
            return
    except Exception as e:
        await message.reply("К сожалению, при конвертации вашего файла возникли проблемы")
        os.remove(file_path)
        return

    os.remove(file_path)
    await input_format_handler(message)

def has_keyboard_changed(new_keyboard, old_keyboard):
    new_buttons = new_keyboard.inline_keyboard
    old_buttons = old_keyboard.inline_keyboard if old_keyboard else None
    
    if old_buttons is None or len(new_buttons) != len(old_buttons):
        return True
    
    for new_row, old_row in zip(new_buttons, old_buttons):
        for new_button, old_button in zip(new_row, old_row):
            if new_button.text != old_button.text:
                return True
    return False

def generate_input_format_keyboard(user_id):
    input_params = db.get_args(user_id)
    formal = "✅" if input_params["formal"] else "❌"
    non_formal = "✅" if not input_params["formal"] else "❌"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{formal} Формальный протокол", callback_data="formal:True"),
            InlineKeyboardButton(text=f"{non_formal} Неформальный протокол", callback_data="formal:False")
        ], [
            InlineKeyboardButton(text=f"⚙️ Дополнительные параметры ⚙️", callback_data="input_params")
        ], [
            InlineKeyboardButton(text=f"🔨 Начать обработку 🔨", callback_data="processing:begin")
        ]
        
    ])
    return keyboard

async def input_format_handler(message: types.Message):
    keyboard = generate_input_format_keyboard(message.from_user.id)
    await message.reply("Задайте параметры:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("formal:"))
async def callback_input_format_option(call: CallbackQuery):
    input_params = db.get_args(call.from_user.id)

    if call.data == "formal:True":
        input_params["formal"] = True
    else:
        input_params["formal"] = False

    db.set_args(call.from_user.id, input_params)

    keyboard = generate_input_format_keyboard(call.from_user.id)
    if has_keyboard_changed(keyboard, call.message.reply_markup):
        await call.message.edit_reply_markup(reply_markup=keyboard)

    await call.answer()

@router.callback_query(F.data == "input_params:getback")
async def callback_input_format_get_back(call: CallbackQuery):
    keyboard = generate_input_format_keyboard(call.from_user.id)
    if has_keyboard_changed(keyboard, call.message.reply_markup):
        await call.message.edit_reply_markup(reply_markup=keyboard)

    await call.answer()

def generate_input_format_internal_keyboard(user_id):
    input_params = db.get_args(user_id)
    if input_params["formal"]:
        list_of_orders = "✅" if input_params["list_of_orders"] else "❌"
        need_password = "✅" if input_params["need_password"] else "❌"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{list_of_orders} Показать список постановлений", callback_data="set_params:formal:list_of_orders")
            ], [
                InlineKeyboardButton(text=f"{need_password} Установка автоматического пароля", callback_data="set_params:formal:need_password")
            ], [
                InlineKeyboardButton(text=f"Назад", callback_data="input_params:getback")
            ]
        ])
    else:
        discussion_context = "✅" if input_params["discussion_context"] else "❌"
        timecodes = "✅" if input_params["timecodes"] else "❌"
        need_password = "✅" if input_params["need_password"] else "❌"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{discussion_context} Показать контекст разговора", callback_data="set_params:non_formal:discussion_context"),
            ], [
                InlineKeyboardButton(text=f"{timecodes} Показать таймкоды", callback_data="set_params:non_formal:timecodes")
            ], [
                InlineKeyboardButton(text=f"{need_password} Установка автоматического пароля", callback_data="set_params:non_formal:need_password")
            ], [
                InlineKeyboardButton(text=f"Назад", callback_data="input_params:getback")
            ]
        ])
    return keyboard

@router.callback_query(F.data == "input_params")
async def callback_input_format_internal_option(call: CallbackQuery):

    keyboard = generate_input_format_internal_keyboard(call.from_user.id)
    if has_keyboard_changed(keyboard, call.message.reply_markup):
        await call.message.edit_reply_markup(reply_markup=keyboard)

    await call.answer()

@router.callback_query(F.data.startswith("set_params"))
async def callback_input_format_internal_option(call: CallbackQuery):
    type, formal_type, param = call.data.split(":")
    input_params = db.get_args(call.from_user.id)

    input_params[param] = input_params[param] ^ 1

    db.set_args(call.from_user.id, input_params)

    keyboard = generate_input_format_internal_keyboard(call.from_user.id)
    if has_keyboard_changed(keyboard, call.message.reply_markup):
        await call.message.edit_reply_markup(reply_markup=keyboard)

    await call.answer()

async def animation_process(call: CallbackQuery, task):
    count = 0
    while not task.done():
        count += 1
        if count > 3:
            count = 1
        await call.message.edit_text(text=f"Processing{"." * count}")
        await asyncio.sleep(0.2)

@router.callback_query(F.data == "processing:begin")
async def callback_processing(call: CallbackQuery):
    input_params = db.get_args(call.from_user.id)
    other_part_of_core.create_protocol(f"{RESULT_PATH}/{call.from_user.id}_{call.message.message_id}_protocol", input_params)

    await call.answer()
    await call.message.delete()
    await output_format_handler(call)


async def output_format_handler(call: CallbackQuery):
    media = [
        types.InputMediaDocument(media=types.FSInputFile(f"{RESULT_PATH}/{call.from_user.id}_{call.message.message_id}_protocol.pdf")),
        types.InputMediaDocument(media=types.FSInputFile(f"{RESULT_PATH}/{call.from_user.id}_{call.message.message_id}_protocol.docx"))
    ]
    await call.message.answer_media_group(media=media)

    await transcribtion_handler(call)

async def transcribtion_handler(call: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да ✅", callback_data="get_transcribtion:True")
        ], [
            InlineKeyboardButton(text="❌ Нет ❌", callback_data="get_transcribtion:False")
        ]
    ])

    await call.message.answer("Нужна ли вам транскрибация?", reply_markup=keyboard)

@router.callback_query(F.data.startswith("get_transcribtion"))
async def callback_transcribtion(call: CallbackQuery):
    type, value = call.data.split(":")
    result = value == "True"

    await call.message.delete()

    if result:
        media = [
            types.InputMediaDocument(media=types.FSInputFile(f"{RESULT_PATH}/{call.from_user.id}_{call.message.message_id}_protocol.txt"))
        ]
        await call.message.answer_document(
            document=media[0].media,
            caption="Вот ваша транскрибация"
        )


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
