# bot/handlers/sx/sx_main_handler.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import lazy_gettext as __
import asyncio

from bot.buttons.reply import get_sx_menu_keyboard, get_main_menu_keyboard
from bot.utils.texts import get_sx_main_text, get_main_text
from bot.utils.message_helpers import (
    store_section_message,
    store_main_message,
    delete_section_messages,
    delete_main_messages,
    safe_delete
)

sx_main_router = Router()


# ⚠️ SX asosiy menyu
@sx_main_router.message(F.text == __("⚠️ Sanoat Xavfsizligi"))
async def sx_main_menu(message: Message, state: FSMContext):
    """SX asosiy menyusi"""
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Parallel o'chirish
    await asyncio.gather(
        safe_delete(message.bot, chat_id, message.message_id),
        delete_section_messages(message.bot, chat_id, user_id),
        delete_main_messages(message.bot, chat_id, user_id),
        return_exceptions=True
    )

    # SX menyusini yuborish
    msg = await message.answer(
        get_sx_main_text(),
        reply_markup=await get_sx_menu_keyboard(),
        parse_mode="HTML"
    )

    store_section_message(user_id, msg.message_id)

    # ✅ STATE NI TOZALASH VA SECTION NI SAQLASH
    await state.clear()
    await state.update_data(section='SX')  # ← BU QATOR KERAK!


# 🏠 Bosh sahifaga qaytish (SX dan)
@sx_main_router.message(F.text == __("🏠 Bosh Sahifa"))
async def back_to_main_from_sx(message: Message, state: FSMContext):
    """SX dan bosh sahifaga qaytish"""
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Parallel o'chirish
    await asyncio.gather(
        safe_delete(message.bot, chat_id, message.message_id),
        delete_section_messages(message.bot, chat_id, user_id),
        return_exceptions=True
    )

    # Bosh sahifa xabari
    msg = await message.answer(
        get_main_text(),
        reply_markup=await get_main_menu_keyboard(),
        parse_mode="HTML"
    )

    store_main_message(user_id, msg.message_id)

    # State tozalash
    await state.clear()