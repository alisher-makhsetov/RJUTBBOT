# bot/handlers/common/folder_handler.py
"""
Folder handler - MM va SX uchun umumiy
BARCHA TILLAR UCHUN ISHLAYDI - EMOJI BO'YICHA
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

from bot.states import FolderState
from bot.buttons.inline import (
    folder_list_keyboard,
    folder_files_keyboard,
    folder_file_sent_keyboard,
    folder_empty_keyboard,
    folder_no_folders_keyboard,
    folder_statistics_keyboard
)
from bot.handlers.common.folder_helpers import (
    store_message,
    delete_user_messages,
    get_folders,
    get_folder_with_files,
    get_file_by_id,
    increment_file_views,
    paginate_items,
    get_parent_type_display_name,
    get_parent_type_emoji,
    get_folder_statistics
)
from bot.utils.stats import log_activity
from bot.utils.texts import (
    folder_main_text,
    folder_no_folders_text,
    folder_files_header,
    folder_empty_text,
    folder_file_detail_text,
    folder_file_error_text,
    folder_error_text,
    folder_statistics_text,
    folder_no_statistics_text,
    get_section_menu_text
)

folder_router = Router()
logger = logging.getLogger(__name__)

# ✅ CONSTANTS
FOLDERS_PER_PAGE = 10
FILES_PER_PAGE = 8

# ==================== EMOJI → PARENT_TYPE MAPPING ====================
EMOJI_TO_PARENT_TYPE = {
    # MM
    "📋": ("nizomlar", "MM"),
    "🦺": ("himoya_vositalari", "MM"),
    "🎓": ("oquv_texnik", "MM"),

    # SX
    "🏗️": ("kranlar", "SX"),
    "🏭": ("qozonxonalar", "SX"),
    "⚙️": ("bosim_idishlari", "SX"),
    "🛠️": ("toliq_texnik", "SX"),
}


def get_parent_type_from_text(text: str) -> tuple[str | None, str | None]:
    """
    ✅ FAQAT EMOJI TEKSHIRISH - BARCHA TILLAR UCHUN

    Args:
        text: Button text (har qanday tilda)

    Returns:
        (parent_type, section) yoki (None, None)
    """
    # Har bir emoji tekshirish
    for emoji, (parent_type, section) in EMOJI_TO_PARENT_TYPE.items():
        if text.startswith(emoji):
            return parent_type, section

    return None, None


# ==================== FOLDER ENTRY HANDLER ====================
@folder_router.message(F.text.regexp(r"^(📋|🦺|🎓|🏗️|🏭|⚙️|🛠️)"))
async def folder_entry(message: Message, state: FSMContext, session: AsyncSession):
    """
    ✅ FOLDER BO'LIMLARIGA KIRISH (BARCHA TILLAR)

    Ishlaydi:
    - O'zbek: "📋 Nizomlar"
    - Qoraqalpaq: "📋 Нызамлар"
    - Rus: "📋 Нормативы"

    Faqat emoji tekshiriladi!
    """

    # Parent type va section aniqlash
    parent_type, section = get_parent_type_from_text(message.text)

    if not parent_type or not section:
        logger.warning(f"Unknown folder button: {message.text}")
        return

    logger.info(f"Folder entry: {message.text} → {parent_type} ({section})")

    # State'ga saqlash
    await state.update_data(parent_type=parent_type, section=section)

    # Show folders
    await show_folders(message, state, session)


# ==================== FOLDER HANDLERS ====================

async def show_folders(message: Message, state: FSMContext, session: AsyncSession):
    """Folderlarni ko'rsatish"""
    await store_message(message.from_user.id, "folder", message.message_id)

    # Reply keyboard'ni yashirish
    temp_msg = await message.answer("...", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.1)
    await temp_msg.delete()

    # STATE'DAN MA'LUMOTLAR
    data = await state.get_data()
    section = data.get('section', 'MM')
    parent_type = data.get('parent_type')

    logger.info(f"Show folders: section={section}, parent_type={parent_type}")

    # YANGI STATE BOSHLASH
    await state.clear()
    await state.set_state(FolderState.choosing_folder)
    await state.update_data(
        section=section,
        parent_type=parent_type
    )

    # Folderlarni olish
    folders = await get_folders(session, section, parent_type)
    logger.info(f"Found {len(folders)} folders")

    # Parent type display name VA EMOJI
    parent_name = get_parent_type_display_name(parent_type)
    parent_emoji = get_parent_type_emoji(parent_type)

    if not folders:
        text = folder_no_folders_text(parent_name, parent_emoji)
        reply_markup = folder_no_folders_keyboard()
    else:
        # Pagination
        current_folders, total_pages, _ = paginate_items(
            folders, 1, FOLDERS_PER_PAGE
        )

        text = folder_main_text(parent_name, parent_emoji)
        reply_markup = folder_list_keyboard(
            current_folders,
            page=1,
            total_pages=total_pages
        )

    sent = await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await store_message(message.chat.id, "folder", sent.message_id)

    # Parallel o'chirish
    await asyncio.gather(
        delete_user_messages(message.bot, message.from_user.id, "menu"),
        delete_user_messages(message.bot, message.from_user.id, "folder", exclude_ids=[sent.message_id])
    )


# 📄 FOLDER SAHIFALASH
@folder_router.callback_query(F.data.startswith("folder_page:"))
async def show_folders_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Folderlar sahifasini ko'rsatish"""
    await callback.answer()

    try:
        page = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(folder_error_text())
        return

    # State'dan ma'lumotlar
    data = await state.get_data()
    section = data.get('section', 'MM')
    parent_type = data.get('parent_type')

    # Folderlarni olish
    folders = await get_folders(session, section, parent_type)

    if not folders:
        await callback.answer(folder_error_text(), show_alert=True)
        return

    # Pagination
    current_folders, total_pages, page = paginate_items(
        folders, page, FOLDERS_PER_PAGE
    )

    # Parent type display name VA EMOJI
    parent_name = get_parent_type_display_name(parent_type)
    parent_emoji = get_parent_type_emoji(parent_type)

    # Matn va tugmalar
    text = folder_main_text(parent_name, parent_emoji)
    markup = folder_list_keyboard(
        current_folders,
        page=page,
        total_pages=total_pages
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# 📂 FOLDER FAYLLARINI KO'RSATISH
@folder_router.callback_query(F.data.startswith("folder:"))
async def show_folder_files(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Folder fayllarini ko'rsatish"""
    await callback.answer()

    try:
        parts = callback.data.split(":")
        folder_id = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 1
    except (ValueError, IndexError):
        await callback.answer(folder_error_text())
        return

    # State o'rnatish
    await state.set_state(FolderState.viewing_files)

    # Folderni olish
    folder = await get_folder_with_files(session, folder_id)

    if not folder:
        await callback.answer(folder_error_text(), show_alert=True)
        return

    if not folder.files:
        return await callback.message.edit_text(
            folder_empty_text(folder.name),
            reply_markup=folder_empty_keyboard(),
            parse_mode="HTML"
        )

    # Fayllar (order_index bo'yicha)
    files = sorted(folder.files, key=lambda x: (x.order_index, x.id))

    # Pagination
    current_files, total_pages, page = paginate_items(
        files, page, FILES_PER_PAGE
    )

    # Matn va tugmalar
    text = folder_files_header(
        folder.name,
        len(files),
        page,
        total_pages
    )
    markup = folder_files_keyboard(
        current_files,
        folder_id,
        page,
        total_pages
    )

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# 📄 FAYL YUBORISH
@folder_router.callback_query(F.data.startswith("folder_file:"))
async def send_file(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Faylni yuborish"""
    await callback.answer()

    try:
        file_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(folder_error_text())
        return

    # State o'rnatish
    await state.set_state(FolderState.viewing_detail)

    # Faylni olish
    file = await get_file_by_id(session, file_id)

    if not file:
        await callback.answer(folder_error_text(), show_alert=True)
        return

    # Ma'lumotlarni saqlash
    folder_id = file.folder_id
    file_name = file.name
    file_telegram_id = file.file_id
    folder_name = file.folder.name
    file_description = file.description
    views_count = file.views_count

    # Faollikni saqlash
    data = await state.get_data()
    section = data.get('section', 'MM')
    parent_type = data.get('parent_type')

    await log_activity(
        session,
        callback.from_user.id,
        'folder_open',
        section,
        parent_type
    )

    # Ko'rilganlar sonini oshirish
    await increment_file_views(session, file_id, callback.from_user.id)

    # Xabarni o'chirish
    await callback.message.delete()

    # FAYLNI YUBORISH
    try:
        doc_msg = await callback.bot.send_document(
            chat_id=callback.from_user.id,
            document=file_telegram_id
        )
        await store_message(callback.from_user.id, "folder", doc_msg.message_id)
        success = True
    except Exception as e:
        logger.error(f"Fayl yuborishda xatolik: {e}", exc_info=True)
        success = False

    # PASTDA TO'LIQ MA'LUMOT
    if success:
        info_text = folder_file_detail_text(
            file_name,
            folder_name,
            file_description,
            views_count + 1
        )
    else:
        info_text = folder_file_error_text()

    info_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=info_text,
        reply_markup=folder_file_sent_keyboard(folder_id),
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "folder", info_msg.message_id)


# 📊 STATISTIKA
@folder_router.callback_query(F.data == "folder_statistics")
async def show_statistics(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Folder statistikasini ko'rsatish"""
    await callback.answer()

    # State o'rnatish
    await state.set_state(FolderState.viewing_statistics)

    # State'dan ma'lumotlar
    data = await state.get_data()
    section = data.get('section', 'MM')
    parent_type = data.get('parent_type')

    # Parent name VA EMOJI
    parent_name = get_parent_type_display_name(parent_type)
    parent_emoji = get_parent_type_emoji(parent_type)

    # Statistika olish
    total_folders, total_files, folder_stats = await get_folder_statistics(
        session, section, parent_type
    )

    if total_folders == 0:
        text = folder_no_statistics_text(parent_name, parent_emoji)
    else:
        text = folder_statistics_text(
            parent_name,
            parent_emoji,
            total_folders,
            total_files,
            folder_stats
        )

    markup = folder_statistics_keyboard()

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


# ↩️ FOLDER RO'YXATIGA QAYTISH
@folder_router.callback_query(F.data == "folder_back_to_list")
async def back_to_list(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Folderlar ro'yxatiga qaytish"""
    await callback.answer()

    # State o'rnatish
    await state.set_state(FolderState.choosing_folder)

    # Barcha xabarlarni o'chirish
    await delete_user_messages(callback.bot, callback.from_user.id, "folder")

    # State'dan ma'lumotlar
    data = await state.get_data()
    section = data.get('section', 'MM')
    parent_type = data.get('parent_type')

    # Folderlarni olish
    folders = await get_folders(session, section, parent_type)

    # Parent type display name VA EMOJI
    parent_name = get_parent_type_display_name(parent_type)
    parent_emoji = get_parent_type_emoji(parent_type)

    if not folders:
        new_msg = await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=folder_no_folders_text(parent_name, parent_emoji),
            reply_markup=folder_no_folders_keyboard(),
            parse_mode="HTML"
        )
        await store_message(callback.from_user.id, "folder", new_msg.message_id)
        return

    # Pagination
    current_folders, total_pages, _ = paginate_items(
        folders, 1, FOLDERS_PER_PAGE
    )

    text = folder_main_text(parent_name, parent_emoji)
    markup = folder_list_keyboard(current_folders, 1, total_pages)

    new_msg = await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    await store_message(callback.from_user.id, "folder", new_msg.message_id)


# 🏠 MM/SX MENYUSIGA QAYTISH
@folder_router.callback_query(F.data == "folder_back_to_section")
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
        delete_user_messages(callback.bot, callback.from_user.id, "folder"),
        delete_user_messages(callback.bot, callback.from_user.id, "menu")
    )

    # STATE NI TOZALASH VA SECTION NI SAQLASH
    await state.clear()
    await state.update_data(section=section)

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