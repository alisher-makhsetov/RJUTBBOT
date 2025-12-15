# bot/handlers/mm/mm_accident_handler.py
"""
MM Baxtsiz Hodisalar handler
Optimized with pagination, chunked deletion, logging, and views counter
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

from bot.states import AccidentState
from bot.buttons.inline import (
    accident_years_keyboard,
    accident_list_keyboard,
    accident_detail_keyboard,
    accident_empty_year_keyboard,
    accident_statistics_main_keyboard,
    accident_statistics_year_keyboard
)
from bot.handlers.mm.mm_accident_helpers import (
    store_message,
    delete_user_messages,
    get_accident_years,
    get_year_with_accidents,
    get_accident_by_id,
    increment_accident_views,
    get_main_statistics,
    get_year_statistics,
    paginate_items
)
from bot.utils.stats import log_activity
from bot.utils.texts import (
    accident_main_text,
    accident_no_years_text,
    accident_year_header_text,
    accident_no_accidents_text,
    accident_detail_text,
    accident_file_error_text,
    accident_statistics_main_text,
    accident_statistics_year_text,
    accident_no_statistics_text,
    accident_error_text,
    get_section_menu_text
)

accident_router = Router()
logger = logging.getLogger(__name__)

# ✅ CONSTANTS
ACCIDENTS_PER_PAGE = 15


# ⚠️ BAXTSIZ HODISALAR ASOSIY MENYU
@accident_router.message(F.text == __("⚠️ Baxtsiz Hodisalar"))
async def show_accident_years(message: Message, state: FSMContext, session: AsyncSession):
    """Baxtsiz hodisa yillarini ko'rsatish"""
    await store_message(message.from_user.id, "accident", message.message_id)

    # Reply keyboard'ni yashirish
    temp_msg = await message.answer("...", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.1)
    await temp_msg.delete()

    # State o'rnatish
    await state.set_state(AccidentState.viewing_years)

    # Yillarni olish
    years = await get_accident_years(session)

    if not years:
        text = accident_no_years_text()
        reply_markup = None
    else:
        text = accident_main_text()
        reply_markup = accident_years_keyboard(years)

    sent = await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await store_message(message.chat.id, "accident", sent.message_id)

    # Parallel o'chirish
    await asyncio.gather(
        delete_user_messages(message.bot, message.from_user.id, "menu"),
        delete_user_messages(message.bot, message.from_user.id, "accident", exclude_ids=[sent.message_id])
    )


# 📆 YIL HODISALARINI KO'RSATISH
@accident_router.callback_query(F.data.startswith("accident_year:"))
async def show_year_accidents(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Yil bo'yicha hodisalarni ko'rsatish"""
    await callback.answer()

    try:
        parts = callback.data.split(":")
        year_id = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 1
    except (ValueError, IndexError):
        await callback.answer(accident_error_text())
        return

    # State o'rnatish
    await state.set_state(AccidentState.viewing_accidents)

    # Yilni olish
    year = await get_year_with_accidents(session, year_id)

    if not year:
        await callback.answer(accident_error_text(), show_alert=True)
        return

    if not year.accidents:
        return await callback.message.edit_text(
            accident_no_accidents_text(year.name),
            reply_markup=accident_empty_year_keyboard(),
            parse_mode="HTML"
        )

    # Eng yangi birinchi
    accidents = sorted(year.accidents, key=lambda x: x.id, reverse=True)

    # Pagination
    current_accidents, total_pages, page = paginate_items(
        accidents, page, ACCIDENTS_PER_PAGE
    )

    # Matn va tugmalar
    text = accident_year_header_text(
        year.name,
        len(accidents),
        page,
        total_pages
    )
    markup = accident_list_keyboard(
        current_accidents,
        year_id,
        page,
        total_pages
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# 📋 HODISA DETALLARI
@accident_router.callback_query(F.data.startswith("accident_detail:"))
async def show_accident_detail(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Hodisa detallarini ko'rsatish"""
    await callback.answer()

    try:
        accident_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(accident_error_text())
        return

    # State o'rnatish
    await state.set_state(AccidentState.viewing_detail)

    # Hodisani olish
    accident = await get_accident_by_id(session, accident_id)

    if not accident:
        await callback.answer(accident_error_text(), show_alert=True)
        return

    # Ma'lumotlarni saqlash
    year_id = accident.year_id
    accident_title = accident.title
    accident_file = accident.file_pdf
    year_name = accident.year.name
    category_name = accident.category.name
    accident_description = accident.description
    views_count = accident.views_count  # ✅ VIEWS COUNT

    # Faollikni saqlash
    await log_activity(session, callback.from_user.id, 'accident_view', 'MM')

    # ✅ KO'RILGANLAR SONINI OSHIRISH (USER UNIQUE)
    await increment_accident_views(session, accident_id, callback.from_user.id)

    # Barcha xabarlarni o'chirish
    await delete_user_messages(callback.bot, callback.from_user.id, "accident")

    # ✅ PDF FAYLNI YUBORISH
    try:
        doc_msg = await callback.bot.send_document(
            chat_id=callback.from_user.id,
            document=accident_file
        )
        await store_message(callback.from_user.id, "accident", doc_msg.message_id)
        success = True
    except Exception as e:
        logger.error(f"PDF yuborishda xatolik: {e}", exc_info=True)
        success = False

    # ✅ PASTDA TO'LIQ MA'LUMOT
    if success:
        info_text = accident_detail_text(
            accident_title,
            year_name,
            category_name,
            accident_description,
            views_count + 1  # ✅ YANGI VIEW QO'SHILDI
        )
    else:
        info_text = accident_file_error_text()

    info_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=info_text,
        reply_markup=accident_detail_keyboard(year_id),
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "accident", info_msg.message_id)


# 📊 UMUMIY STATISTIKA
@accident_router.callback_query(F.data == "accident_statistics_main")
async def show_main_statistics(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Umumiy statistikani ko'rsatish"""
    await callback.answer()

    # State o'rnatish
    await state.set_state(AccidentState.viewing_statistics)

    # Statistika olish
    total_count, year_stats = await get_main_statistics(session)

    if total_count == 0:
        text = accident_no_statistics_text()
    else:
        text = accident_statistics_main_text(total_count, year_stats)

    markup = accident_statistics_main_keyboard()

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# 📊 YIL STATISTIKASI
@accident_router.callback_query(F.data.startswith("accident_statistics_year:"))
async def show_year_statistics(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Yil bo'yicha statistikani ko'rsatish"""
    await callback.answer()

    try:
        year_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(accident_error_text())
        return

    # State o'rnatish
    await state.set_state(AccidentState.viewing_statistics)

    # Yilni olish
    year = await get_year_with_accidents(session, year_id)

    if not year:
        await callback.answer(accident_error_text(), show_alert=True)
        return

    # Statistika olish
    total, category_stats = await get_year_statistics(session, year_id)

    # Matn va tugmalar
    text = accident_statistics_year_text(year.name, total, category_stats)
    markup = accident_statistics_year_keyboard(year_id)

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# ↩️ YILLARGA QAYTISH
@accident_router.callback_query(F.data == "accident_back_to_years")
async def back_to_years(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Yillar ro'yxatiga qaytish"""
    await callback.answer()

    # State o'rnatish
    await state.set_state(AccidentState.viewing_years)

    # Barcha xabarlarni o'chirish
    await delete_user_messages(callback.bot, callback.from_user.id, "accident")

    # Yillarni olish
    years = await get_accident_years(session)

    if not years:
        new_msg = await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=accident_no_years_text(),
            parse_mode="HTML"
        )
        await store_message(callback.from_user.id, "accident", new_msg.message_id)
        return

    # Yangi xabar
    text = accident_main_text()
    keyboard = accident_years_keyboard(years)

    new_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "accident", new_msg.message_id)


# 🏠 MM MENYUSIGA QAYTISH
@accident_router.callback_query(F.data == "accident_back_to_section")
async def back_to_section(callback: CallbackQuery, state: FSMContext):
    """MM asosiy menyusiga qaytish"""
    await callback.answer()

    # Xabarni o'chirish
    await callback.message.delete()

    # Parallel o'chirish
    await asyncio.gather(
        delete_user_messages(callback.bot, callback.from_user.id, "accident"),
        delete_user_messages(callback.bot, callback.from_user.id, "menu")
    )

    # State tozalash
    await state.clear()

    from bot.utils.message_helpers import store_section_message
    from bot.buttons.reply import get_mm_menu_keyboard

    msg = await callback.message.answer(
        get_section_menu_text(),
        reply_markup=await get_mm_menu_keyboard(),
        parse_mode="HTML"
    )

    store_section_message(callback.from_user.id, msg.message_id)