# bot/handlers/common/video_handler.py
"""
Video handler - MM va SX uchun umumiy
Section-aware video tizimi - Optimized
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

from bot.states import VideoState
from bot.buttons.inline import (
    video_category_keyboard,
    video_list_keyboard,
    video_sent_keyboard,
    video_statistics_keyboard,
    video_empty_category_keyboard
)
from bot.handlers.common.video_helpers import (
    store_message,
    delete_user_messages,
    get_video_categories,
    get_category_with_videos,
    get_video_by_id,
    get_video_statistics,
    paginate_items
)
from bot.utils.stats import log_activity
from bot.utils.texts import (
    video_no_categories_text,
    video_categories_prompt,
    video_category_empty,
    video_list_header,
    video_detail_text,  # ✅ YANGI
    video_file_error_text,
    video_statistics_text,
    video_no_statistics_text,
    video_error_text,
    get_section_menu_text
)

video_router = Router()
logger = logging.getLogger(__name__)

# ✅ CONSTANTS
CATEGORIES_PER_PAGE = 10
VIDEOS_PER_PAGE = 8


# 🎬 VIDEO KATEGORIYALARINI KO'RSATISH
@video_router.message(F.text == __("🎬 Video Materiallar"))
async def show_video_categories(message: Message, state: FSMContext, session: AsyncSession):
    """Video kategoriyalarini ko'rsatish - pagination bilan"""
    await store_message(message.from_user.id, "video", message.message_id)

    # Reply keyboard'ni yashirish
    temp_msg = await message.answer("...", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.1)
    await temp_msg.delete()

    # ✅ STATE'DAN SECTION OLISH (AVVAL!)
    data = await state.get_data()
    section = data.get('section', 'MM')

    # ✅ YANGI STATE BOSHLASH
    await state.clear()
    await state.set_state(VideoState.choosing_category)
    await state.update_data(section=section)  # ← SECTION'NI QAYTA SAQLASH!

    # Kategoriyalarni olish
    categories = await get_video_categories(session, section)

    if not categories:
        text = video_no_categories_text()
        reply_markup = None
    else:
        # Pagination
        current_categories, total_pages, _ = paginate_items(
            categories, 1, CATEGORIES_PER_PAGE
        )

        text = video_categories_prompt()
        reply_markup = video_category_keyboard(
            current_categories,
            page=1,
            total_pages=total_pages
        )

    sent = await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await store_message(message.chat.id, "video", sent.message_id)

    # Parallel o'chirish
    await asyncio.gather(
        delete_user_messages(message.bot, message.from_user.id, "menu"),
        delete_user_messages(message.bot, message.from_user.id, "video", exclude_ids=[sent.message_id])
    )

# 📄 KATEGORIYA SAHIFALASH
@video_router.callback_query(F.data.startswith("video_categories_page:"))
async def show_categories_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Kategoriyalar sahifasini ko'rsatish"""
    await callback.answer()

    try:
        page = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(video_error_text())
        return

    # State'dan section olish
    data = await state.get_data()
    section = data.get('section', 'MM')

    # Kategoriyalarni olish
    categories = await get_video_categories(session, section)

    if not categories:
        await callback.answer(video_error_text(), show_alert=True)
        return

    # Pagination
    current_categories, total_pages, page = paginate_items(
        categories, page, CATEGORIES_PER_PAGE
    )

    # Matn va tugmalar
    text = video_categories_prompt()
    markup = video_category_keyboard(
        current_categories,
        page=page,
        total_pages=total_pages
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# 📂 KATEGORIYA VIDEOLARINI KO'RSATISH
@video_router.callback_query(F.data.startswith("video_category:"))
async def show_category_videos(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Kategoriya tanlanganda videolarni ko'rsatish"""
    await callback.answer()

    try:
        parts = callback.data.split(":")
        category_id = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 1
    except (ValueError, IndexError):
        await callback.answer(video_error_text())
        return

    # State o'rnatish
    await state.set_state(VideoState.viewing_videos)

    # Kategoriyani olish
    category = await get_category_with_videos(session, category_id)

    if not category:
        await callback.answer(video_error_text(), show_alert=True)
        return

    if not category.videos:
        return await callback.message.edit_text(
            video_category_empty(category.name),
            reply_markup=video_empty_category_keyboard(),
            parse_mode="HTML"
        )

    # Eng yangi birinchi
    videos = sorted(category.videos, key=lambda x: x.id, reverse=True)

    # Pagination
    current_videos, total_pages, page = paginate_items(
        videos, page, VIDEOS_PER_PAGE
    )

    # Matn va tugmalar
    text = video_list_header(
        category.name,
        len(videos),
        page,
        total_pages
    )
    markup = video_list_keyboard(
        current_videos,
        category_id,
        page,
        total_pages
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# 🎬 VIDEO YUBORISH
@video_router.callback_query(F.data.startswith("video_file:"))
async def send_file(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Videoni yuborish"""
    await callback.answer()

    try:
        video_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(video_error_text())
        return

    # State o'rnatish
    await state.set_state(VideoState.viewing_videos)

    # Videoni olish
    video = await get_video_by_id(session, video_id)

    if not video:
        await callback.answer(video_error_text(), show_alert=True)
        return

    # Ma'lumotlarni saqlash
    category_id = video.category_id
    video_name = video.name
    video_file = video.file
    category_name = video.category.name
    video_description = video.description

    # Faollikni saqlash
    data = await state.get_data()
    section = data.get('section', 'MM')
    await log_activity(session, callback.from_user.id, 'video_view', section)

    # Xabarni o'chirish
    await callback.message.delete()

    # ✅ VIDEONI YUBORISH (caption YO'Q)
    try:
        msg = await callback.bot.send_video(
            chat_id=callback.from_user.id,
            video=video_file
        )
        await store_message(callback.from_user.id, "video", msg.message_id)
        success = True
    except Exception as e:
        logger.error(f"Video yuborishda xatolik: {e}", exc_info=True)
        success = False

    # ✅ PASTDA TO'LIQ MA'LUMOT
    if success:
        info_text = video_detail_text(
            video_name,
            category_name,
            video_description
        )
    else:
        info_text = video_file_error_text()

    info_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=info_text,
        reply_markup=video_sent_keyboard(category_id),
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "video", info_msg.message_id)


# 📊 STATISTIKA
@video_router.callback_query(F.data == "video_statistics")
async def show_statistics(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Statistikani ko'rsatish"""
    await callback.answer()

    # State o'rnatish
    await state.set_state(VideoState.viewing_statistics)

    # Section ni olish
    data = await state.get_data()
    section = data.get('section', 'MM')

    # Statistika olish
    total_videos, category_stats = await get_video_statistics(session, section)

    if total_videos == 0:
        text = video_no_statistics_text()
    else:
        text = video_statistics_text(total_videos, category_stats)

    markup = video_statistics_keyboard()

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# ↩️ KATEGORIYALARGA QAYTISH
@video_router.callback_query(F.data == "video_back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Kategoriyalarga qaytish"""
    await callback.answer()

    # State o'rnatish
    await state.set_state(VideoState.choosing_category)

    # Xabarni o'chirish
    await callback.message.delete()

    # Section olish
    data = await state.get_data()
    section = data.get('section', 'MM')

    # Kategoriyalarni olish
    categories = await get_video_categories(session, section)

    if not categories:
        new_msg = await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=video_no_categories_text(),
            parse_mode="HTML"
        )
        await store_message(callback.from_user.id, "video", new_msg.message_id)
        return

    # Pagination
    current_categories, total_pages, _ = paginate_items(
        categories, 1, CATEGORIES_PER_PAGE
    )

    text = video_categories_prompt()
    markup = video_category_keyboard(current_categories, 1, total_pages)

    new_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "video", new_msg.message_id)


# ↩️ VIDEO RO'YXATIGA QAYTISH
@video_router.callback_query(F.data.startswith("video_back_to_list:"))
async def back_to_list(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Video ro'yxatiga qaytish"""
    await callback.answer()

    try:
        category_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(video_error_text())
        return

    # State o'rnatish
    await state.set_state(VideoState.viewing_videos)

    # Barcha xabarlarni o'chirish
    await delete_user_messages(callback.bot, callback.from_user.id, "video")

    # Kategoriyani olish
    category = await get_category_with_videos(session, category_id)

    if not category:
        await callback.answer(video_error_text(), show_alert=True)
        return

    if not category.videos:
        new_msg = await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=video_category_empty(category.name),
            reply_markup=video_empty_category_keyboard(),
            parse_mode="HTML"
        )
        await store_message(callback.from_user.id, "video", new_msg.message_id)
        return

    # Eng yangi birinchi
    videos = sorted(category.videos, key=lambda x: x.id, reverse=True)

    # Pagination
    current_videos, total_pages, _ = paginate_items(
        videos, 1, VIDEOS_PER_PAGE
    )

    text = video_list_header(category.name, len(videos), 1, total_pages)
    markup = video_list_keyboard(current_videos, category_id, 1, total_pages)

    new_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "video", new_msg.message_id)


# 🏠 MM/SX MENYUSIGA QAYTISH
@video_router.callback_query(F.data == "video_back_to_section")
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
        delete_user_messages(callback.bot, callback.from_user.id, "video"),
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