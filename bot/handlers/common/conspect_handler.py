# bot/handlers/common/conspect_handler.py
"""
Konspekt handler - MM va SX uchun umumiy
Section-aware konspekt tizimi - Optimized
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

from bot.states import ConspectState
from bot.buttons.inline import (
    conspect_category_keyboard,
    conspect_files_keyboard,
    conspect_file_sent_keyboard,
    conspect_statistics_keyboard,
    conspect_empty_category_keyboard
)
from bot.handlers.common.conspect_helpers import (
    store_message,
    delete_user_messages,
    get_conspect_categories,
    get_category_with_conspects,
    get_conspect_by_id,
    get_conspect_statistics,
    paginate_items  # ✅ ISHLATAMIZ
)
from bot.utils.stats import log_activity
from bot.utils.texts import (
    conspect_no_categories_text,
    conspect_categories_prompt,
    conspect_category_empty,
    conspect_files_header,
    conspect_file_sent_text,
    conspect_file_error_text,
    conspect_statistics_text,
    conspect_no_statistics_text,
    conspect_error_text,
    get_section_menu_text,
)

conspect_router = Router()
logger = logging.getLogger(__name__)  # ✅ LOGGING

# ✅ CONSTANTS - OPTIMALLASHTIRILDI
CATEGORIES_PER_PAGE = 10  # 2x3 grid optimal
FILES_PER_PAGE = 8  # 10 ta yetarli


# 📚 KONSPEKT KATEGORIYALARINI KO'RSATISH
@conspect_router.message(F.text == __("📚 Konspektlar"))
async def show_conspect_categories(message: Message, state: FSMContext, session: AsyncSession):
    """Konspekt kategoriyalarini ko'rsatish - pagination bilan"""
    await store_message(message.from_user.id, "conspect", message.message_id)

    # Reply keyboard'ni yashirish
    temp_msg = await message.answer("...", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.1)
    await temp_msg.delete()

    # ✅ STATE'DAN SECTION OLISH (AVVAL!)
    data = await state.get_data()
    section = data.get('section', 'MM')

    # ✅ YANGI STATE BOSHLASH
    await state.clear()
    await state.set_state(ConspectState.choosing_category)
    await state.update_data(section=section)  # ← SECTION'NI QAYTA SAQLASH!

    # Kategoriyalarni olish
    categories = await get_conspect_categories(session, section)

    if not categories:
        text = conspect_no_categories_text()
        reply_markup = None
    else:
        # ✅ PAGINATION HELPER ISHLATISH
        current_categories, total_pages, _ = paginate_items(
            categories, 1, CATEGORIES_PER_PAGE
        )

        text = conspect_categories_prompt()
        reply_markup = conspect_category_keyboard(
            current_categories,
            page=1,
            total_pages=total_pages
        )

    sent = await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await store_message(message.chat.id, "conspect", sent.message_id)

    # Parallel o'chirish
    await asyncio.gather(
        delete_user_messages(message.bot, message.from_user.id, "menu"),
        delete_user_messages(message.bot, message.from_user.id, "conspect", exclude_ids=[sent.message_id])
    )


# 📄 KATEGORIYA SAHIFALASH
@conspect_router.callback_query(F.data.startswith("conspect_categories_page:"))
async def show_categories_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Kategoriyalar sahifasini ko'rsatish"""
    await callback.answer()

    try:
        page = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(conspect_error_text())
        return

    # State'dan section olish
    data = await state.get_data()
    section = data.get('section', 'MM')

    # Kategoriyalarni olish
    categories = await get_conspect_categories(session, section)

    if not categories:
        await callback.answer(conspect_error_text(), show_alert=True)
        return

    # ✅ PAGINATION HELPER
    current_categories, total_pages, page = paginate_items(
        categories, page, CATEGORIES_PER_PAGE
    )

    # Matn va tugmalar
    text = conspect_categories_prompt()
    markup = conspect_category_keyboard(
        current_categories,
        page=page,
        total_pages=total_pages
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# 📂 KATEGORIYA FAYLLARINI KO'RSATISH
@conspect_router.callback_query(F.data.startswith("conspect_category:"))
async def show_category_files(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Kategoriya tanlanganda fayllarni ko'rsatish"""
    await callback.answer()

    try:
        parts = callback.data.split(":")
        category_id = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 1
    except (ValueError, IndexError):
        await callback.answer(conspect_error_text())
        return

    # State o'rnatish
    await state.set_state(ConspectState.viewing_files)

    # Kategoriyani olish
    category = await get_category_with_conspects(session, category_id)

    if not category:
        await callback.answer(conspect_error_text(), show_alert=True)
        return

    if not category.conspects:
        return await callback.message.edit_text(
            conspect_category_empty(category.name),
            reply_markup=conspect_empty_category_keyboard(),
            parse_mode="HTML"
        )

    # Eng yangi birinchi
    conspects = sorted(category.conspects, key=lambda x: x.id, reverse=True)

    # ✅ PAGINATION HELPER
    current_files, total_pages, page = paginate_items(
        conspects, page, FILES_PER_PAGE
    )

    # Matn va tugmalar
    text = conspect_files_header(
        category.name,
        len(conspects),
        page,
        total_pages
    )
    markup = conspect_files_keyboard(
        current_files,
        category_id,
        page,
        total_pages
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# 📄 FAYL YUBORISH
@conspect_router.callback_query(F.data.startswith("conspect_file:"))
async def send_file(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Faylni yuborish"""
    await callback.answer()

    try:
        conspect_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(conspect_error_text())
        return

    # State o'rnatish
    await state.set_state(ConspectState.viewing_files)

    conspect = await get_conspect_by_id(session, conspect_id)

    if not conspect:
        await callback.answer(conspect_error_text(), show_alert=True)
        return

    # Ma'lumotlarni saqlash
    category_id = conspect.category_id
    conspect_name = conspect.name
    conspect_file = conspect.file
    category_name = conspect.category.name
    conspect_description = conspect.description

    # Faollikni saqlash
    data = await state.get_data()
    section = data.get('section', 'MM')
    await log_activity(session, callback.from_user.id, 'conspect_view', section)

    # Xabarni o'chirish
    await callback.message.delete()

    # Faylni yuborish
    try:
        msg = await callback.bot.send_document(
            chat_id=callback.from_user.id,
            document=conspect_file
        )
        await store_message(callback.from_user.id, "conspect", msg.message_id)
        success = True
    except Exception as e:
        # ✅ LOGGING
        logger.error(f"Fayl yuborishda xatolik: {e}", exc_info=True)
        success = False

    # To'liq ma'lumot xabari
    if success:
        info_text = conspect_file_sent_text(
            conspect_name,
            category_name,
            conspect_description
        )
    else:
        info_text = conspect_file_error_text()

    info_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=info_text,
        reply_markup=conspect_file_sent_keyboard(category_id),
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "conspect", info_msg.message_id)


# 📊 STATISTIKA
@conspect_router.callback_query(F.data == "conspect_statistics")
async def show_statistics(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Statistikani ko'rsatish"""
    await callback.answer()

    # State o'rnatish
    await state.set_state(ConspectState.viewing_statistics)

    # Section ni olish
    data = await state.get_data()
    section = data.get('section', 'MM')

    # Statistika olish
    total_files, category_stats = await get_conspect_statistics(session, section)

    if total_files == 0:
        text = conspect_no_statistics_text()
    else:
        text = conspect_statistics_text(total_files, category_stats)

    markup = conspect_statistics_keyboard()

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# ↩️ KATEGORIYALARGA QAYTISH
@conspect_router.callback_query(F.data == "conspect_back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Kategoriyalarga qaytish"""
    await callback.answer()

    # State o'rnatish
    await state.set_state(ConspectState.choosing_category)

    # Xabarni o'chirish
    await callback.message.delete()

    # Section olish
    data = await state.get_data()
    section = data.get('section', 'MM')

    # Kategoriyalarni olish
    categories = await get_conspect_categories(session, section)

    if not categories:
        new_msg = await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=conspect_no_categories_text(),
            parse_mode="HTML"
        )
        await store_message(callback.from_user.id, "conspect", new_msg.message_id)
        return

    # ✅ PAGINATION HELPER
    current_categories, total_pages, _ = paginate_items(
        categories, 1, CATEGORIES_PER_PAGE
    )

    text = conspect_categories_prompt()
    markup = conspect_category_keyboard(current_categories, 1, total_pages)

    new_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "conspect", new_msg.message_id)


# ↩️ FAYLLAR RO'YXATIGA QAYTISH
@conspect_router.callback_query(F.data.startswith("conspect_back_to_files:"))
async def back_to_files(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Fayllar ro'yxatiga qaytish"""
    await callback.answer()

    try:
        category_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(conspect_error_text())
        return

    # State o'rnatish
    await state.set_state(ConspectState.viewing_files)

    # Barcha xabarlarni o'chirish
    await delete_user_messages(callback.bot, callback.from_user.id, "conspect")

    # Kategoriyani olish
    category = await get_category_with_conspects(session, category_id)

    if not category:
        await callback.answer(conspect_error_text(), show_alert=True)
        return

    if not category.conspects:
        new_msg = await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=conspect_category_empty(category.name),
            reply_markup=conspect_empty_category_keyboard(),
            parse_mode="HTML"
        )
        await store_message(callback.from_user.id, "conspect", new_msg.message_id)
        return

    # Eng yangi birinchi
    conspects = sorted(category.conspects, key=lambda x: x.id, reverse=True)

    # ✅ PAGINATION HELPER
    current_files, total_pages, _ = paginate_items(
        conspects, 1, FILES_PER_PAGE
    )

    text = conspect_files_header(category.name, len(conspects), 1, total_pages)
    markup = conspect_files_keyboard(current_files, category_id, 1, total_pages)

    new_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "conspect", new_msg.message_id)


# 🏠 MM/SX MENYUSIGA QAYTISH
@conspect_router.callback_query(F.data == "conspect_back_to_section")
async def back_to_section(callback: CallbackQuery, state: FSMContext):
    """MM yoki SX asosiy menyusiga qaytish"""
    await callback.answer()

    # Section ni olish
    data = await state.get_data()
    section = data.get('section', 'MM')

    # Xabarni o'chirish
    await callback.message.delete()

    # Parallel o'chirish
    await asyncio.gather(
        delete_user_messages(callback.bot, callback.from_user.id, "conspect"),
        delete_user_messages(callback.bot, callback.from_user.id, "menu")
    )

    # ✅ STATE NI TOZALASH VA SECTION NI SAQLASH
    await state.clear()
    await state.update_data(section=section)  # ← BU QATOR QO'SHILDI!

    from bot.utils.message_helpers import store_section_message

    if section == 'MM':
        from bot.buttons.reply import get_mm_menu_keyboard

        msg = await callback.message.answer(
            get_section_menu_text(),
            reply_markup=await get_mm_menu_keyboard(),
            parse_mode="HTML"
        )
    else:  # SX
        from bot.buttons.reply import get_sx_menu_keyboard

        msg = await callback.message.answer(
            get_section_menu_text(),
            reply_markup=await get_sx_menu_keyboard(),
            parse_mode="HTML"
        )

    store_section_message(callback.from_user.id, msg.message_id)