# bot/handlers/common/folder_helpers.py
"""
Folder handler uchun yordamchi funksiyalar
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Tuple, Optional
from collections import defaultdict, deque
import asyncio

from db.models import Folder, File, FileView

# ==================== CONSTANTS ====================
DELETE_CHUNK_SIZE = 10
MAX_MESSAGES_PER_USER = 10


# ==================== MESSAGE STORE ====================
# ... (eski kod - o'zgarmaydi)

class FolderMessageStore:
    """Folder uchun message store"""

    def __init__(self):
        self.user_messages = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=MAX_MESSAGES_PER_USER))
        )

    def store_message(self, user_id: int, message_id: int, category: str = "folder"):
        """Xabarni saqlash"""
        self.user_messages[user_id][category].append(message_id)

    def get_messages(self, user_id: int, category: str = "folder") -> list[int]:
        """User xabarlarini olish"""
        return list(self.user_messages[user_id][category])

    def clear_user_messages(self, user_id: int, category: str = "folder"):
        """User xabarlarini tozalash"""
        self.user_messages[user_id][category].clear()


folder_message_store = FolderMessageStore()


async def store_message(user_id: int, category: str, message_id: int):
    """Xabar saqlash"""
    try:
        folder_message_store.store_message(user_id, message_id, category)
    except Exception:
        pass


async def _safe_delete(bot, chat_id: int, msg_id: int):
    """Xavfsiz xabar o'chirish"""
    try:
        await bot.delete_message(chat_id, msg_id)
        return True
    except Exception:
        return False


async def delete_user_messages(bot, user_id: int, category: str, exclude_ids: Optional[list[int]] = None):
    """Xabarlarni parallel o'chirish"""
    msg_ids = folder_message_store.get_messages(user_id, category)

    if exclude_ids:
        msg_ids = [msg_id for msg_id in msg_ids if msg_id not in exclude_ids]

    for i in range(0, len(msg_ids), DELETE_CHUNK_SIZE):
        chunk = msg_ids[i:i + DELETE_CHUNK_SIZE]
        tasks = [_safe_delete(bot, user_id, msg_id) for msg_id in chunk]
        await asyncio.gather(*tasks, return_exceptions=True)

    if not exclude_ids:
        folder_message_store.clear_user_messages(user_id, category)


# ==================== DATABASE QUERIES ====================

async def get_folders(
        session: AsyncSession,
        section: str,
        parent_type: str
) -> List[Folder]:
    """Folderlarni olish"""
    result = await session.execute(
        select(Folder)
        .options(selectinload(Folder.files))
        .where(
            Folder.section == section,
            Folder.parent_type == parent_type
        )
        .order_by(Folder.order_index, Folder.created_at)
    )
    return list(result.scalars().all())


async def get_folder_with_files(session: AsyncSession, folder_id: int) -> Folder | None:
    """Folderni fayllar bilan olish"""
    result = await session.execute(
        select(Folder)
        .options(selectinload(Folder.files))
        .where(Folder.id == folder_id)
    )
    return result.scalar_one_or_none()


async def get_file_by_id(session: AsyncSession, file_id: int) -> File | None:
    """Faylni ID bo'yicha olish"""
    result = await session.execute(
        select(File)
        .options(
            selectinload(File.folder),
            selectinload(File.views)
        )
        .where(File.id == file_id)
    )
    return result.scalar_one_or_none()


async def increment_file_views(session: AsyncSession, file_id: int, user_id: int):
    """Ko'rilganlar sonini oshirish"""
    try:
        result = await session.execute(
            select(FileView).where(
                FileView.file_id == file_id,
                FileView.user_id == user_id
            )
        )
        existing_view = result.scalar_one_or_none()

        if not existing_view:
            new_view = FileView(file_id=file_id, user_id=user_id)
            session.add(new_view)
            await session.commit()
    except Exception:
        await session.rollback()


# ==================== PAGINATION ====================

def paginate_items(items: List, page: int, per_page: int) -> Tuple[List, int, int]:
    """Sahifalash"""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    current_items = items[start_idx:end_idx]
    return current_items, total_pages, page


# ==================== PARENT TYPE HELPERS ====================

def get_parent_type_display_name(parent_type: str) -> str:
    """
    ✅ DATABASE'DAGI ASL NOMNI QAYTARISH

    Bu nom keyin _() orqali tarjima qilinadi!
    """
    name_map = {
        'nizomlar': 'Nizomlar',
        'himoya_vositalari': 'Himoya Vositalari',
        'oquv_texnik': "O'quv Texnik Mashg'ulot",
        'kranlar': 'Kranlar',
        'qozonxonalar': 'Qozonxonalar',
        'bosim_idishlari': "Bosim Ostidagi Ichlovchi Sig'im",
        'toliq_texnik': "To'liq Texnik Ko'rik",
    }
    return name_map.get(parent_type, parent_type)


async def get_folder_statistics(
        session: AsyncSession,
        section: str,
        parent_type: str
) -> Tuple[int, int, List[Tuple]]:
    """Folder statistikasi"""
    folders = await get_folders(session, section, parent_type)
    total_folders = len(folders)
    folder_stats = []
    total_files = 0

    for folder in folders:
        file_count = len(folder.files)
        total_files += file_count
        folder_stats.append((folder.name, file_count))

    folder_stats = sorted(folder_stats, key=lambda x: x[1], reverse=True)
    return total_folders, total_files, folder_stats


def get_parent_type_emoji(parent_type: str) -> str:
    """Emoji olish"""
    emoji_map = {
        'himoya_vositalari': '🦺',
        'nizomlar': '📋',
        'oquv_texnik': '🎓',
        'kranlar': '🏗️',
        'qozonxonalar': '🏭',
        'bosim_idishlari': '⚙️',
        'toliq_texnik': '🛠️',
    }
    return emoji_map.get(parent_type, '📁')