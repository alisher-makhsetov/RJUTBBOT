#bot/buttons/reply.py
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _


async def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text=_("👷 Mehnat Muhofazasi")),
        KeyboardButton(text=_("⚠️ Sanoat Xavfsizligi")),
        KeyboardButton(text=_("🌐 Tilni O'zgartirish")),
    ]
    builder.add(*buttons)
    builder.adjust(2,1)
    return builder.as_markup(resize_keyboard=True)


async def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text=_("📱 Telefon raqamimni yuborish"), request_contact=True)
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def get_language_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text=_("🇺🇿 Uzbek")),
        KeyboardButton(text=_("🇷🇺 Rus")),
        KeyboardButton(text=_("🇺🇿 Qoraqalpoq")),
        KeyboardButton(text=_("↩️ Orqaga")),
    ]
    builder.add(*buttons)
    builder.adjust(2, 1, 1)
    # return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    return builder.as_markup(resize_keyboard=True)

# bot/buttons/reply.py ga qo'shing (oxiriga)

# ============================ MM KEYBOARD ============================

async def get_mm_menu_keyboard() -> ReplyKeyboardMarkup:
    """MM bo'limlari klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text=_("📝 Test")),
        KeyboardButton(text=_("📚 Konspektlar")),
        KeyboardButton(text=_("📋 Nizomlar")),
        KeyboardButton(text=_("🦺 Himoya Vositalari")),
        KeyboardButton(text=_("⚠️ Baxtsiz Hodisalar")),
        KeyboardButton(text=_("🎬 Video Materiallar")),
        KeyboardButton(text=_("🎓 O'quv Texnik Mashg'ulot")),
        KeyboardButton(text=_("🏠 Bosh Sahifa")),
    ]
    builder.add(*buttons)
    builder.adjust(2, 2, 2, 1, 1)  # 2-2-2-1-1 tartibda
    return builder.as_markup(resize_keyboard=True)


# ============================ SX KEYBOARD ============================

async def get_sx_menu_keyboard() -> ReplyKeyboardMarkup:
    """SX bo'limlari klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text=_("📝 Test")),
        KeyboardButton(text=_("📚 Konspektlar")),
        KeyboardButton(text=_("🏭 Qozonxonalar")),
        KeyboardButton(text=_("🏗️ Kranlar")),
        KeyboardButton(text=_("⚙️ Bosim Ostidagi Ichlovchi Sig'im")),
        KeyboardButton(text=_("🎬 Video Materiallar")),
        KeyboardButton(text=_("🛠️ To‘liq Texnik Ko‘rik")),
        KeyboardButton(text=_("🏠 Bosh Sahifa")),
    ]
    builder.add(*buttons)
    builder.adjust(2, 2, 2, 1, 1)  # 2-2-2-1-1 tartibda
    return builder.as_markup(resize_keyboard=True)