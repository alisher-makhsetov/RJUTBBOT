# bot/handlers/common/video_helpers.py
"""
Video handler uchun yordamchi funksiyalar
Optimallashtirilgan - Chunked deletion bilan
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Tuple, Optional
from collections import defaultdict, deque
import asyncio

from db.models import VideoCategory, Video

# ==================== CONSTANTS ====================
DELETE_CHUNK_SIZE = 10
MAX_MESSAGES_PER_USER = 10


# ==================== MESSAGE STORE ====================

class VideoMessageStore:
    """Video uchun message store"""

    def __init__(self):
        self.user_messages = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=MAX_MESSAGES_PER_USER))
        )

    def store_message(self, user_id: int, message_id: int, category: str = "video"):
        """Xabarni saqlash"""
        self.user_messages[user_id][category].append(message_id)

    def get_messages(self, user_id: int, category: str = "video") -> list[int]:
        """User xabarlarini olish"""
        return list(self.user_messages[user_id][category])

    def clear_user_messages(self, user_id: int, category: str = "video"):
        """User xabarlarini tozalash"""
        self.user_messages[user_id][category].clear()


# Global instance
video_message_store = VideoMessageStore()


# ==================== MESSAGE MANAGEMENT ====================

async def store_message(user_id: int, category: str, message_id: int):
    """Xabar saqlash"""
    try:
        video_message_store.store_message(user_id, message_id, category)
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
    """
    Xabarlarni parallel o'chirish (chunked)
    """
    msg_ids = video_message_store.get_messages(user_id, category)

    if exclude_ids:
        msg_ids = [msg_id for msg_id in msg_ids if msg_id not in exclude_ids]

    # Chunking - 10 tadan parallel o'chirish
    for i in range(0, len(msg_ids), DELETE_CHUNK_SIZE):
        chunk = msg_ids[i:i + DELETE_CHUNK_SIZE]
        tasks = [_safe_delete(bot, user_id, msg_id) for msg_id in chunk]
        await asyncio.gather(*tasks, return_exceptions=True)

    # Store tozalash
    if not exclude_ids:
        video_message_store.clear_user_messages(user_id, category)


# ==================== DATABASE QUERIES ====================

async def get_video_categories(session: AsyncSession, section: str) -> List[VideoCategory]:
    """
    Section bo'yicha video kategoriyalarini olish

    Args:
        session: Database session
        section: 'MM' yoki 'SX'

    Returns:
        Kategoriyalar ro'yxati (created_at bo'yicha tartiblangan)
    """
    result = await session.execute(
        select(VideoCategory)
        .options(selectinload(VideoCategory.videos))
        .where(VideoCategory.section == section)
        .order_by(VideoCategory.created_at)
    )
    return list(result.scalars().all())


async def get_category_with_videos(
        session: AsyncSession,
        category_id: int
) -> VideoCategory | None:
    """
    Kategoriyani videolar bilan birga olish

    Args:
        session: Database session
        category_id: Kategoriya ID

    Returns:
        Kategoriya yoki None
    """
    result = await session.execute(
        select(VideoCategory)
        .options(selectinload(VideoCategory.videos))
        .where(VideoCategory.id == category_id)
    )
    return result.scalar_one_or_none()


async def get_video_by_id(
        session: AsyncSession,
        video_id: int
) -> Video | None:
    """
    Videoni ID bo'yicha olish

    Args:
        session: Database session
        video_id: Video ID

    Returns:
        Video yoki None
    """
    result = await session.execute(
        select(Video)
        .options(selectinload(Video.category))
        .where(Video.id == video_id)
    )
    return result.scalar_one_or_none()


async def get_video_statistics(
        session: AsyncSession,
        section: str
) -> Tuple[int, List[Tuple]]:
    """
    Video statistikasini olish

    Args:
        session: Database session
        section: 'MM' yoki 'SX'

    Returns:
        (jami_videolar_soni, kategoriyalar_statistikasi)
    """
    # Jami videolar soni
    total_result = await session.execute(
        select(func.count(Video.id))
        .join(VideoCategory)
        .where(VideoCategory.section == section)
    )
    total_videos = total_result.scalar() or 0

    # Kategoriyalar bo'yicha statistika
    stats_result = await session.execute(
        select(
            VideoCategory.name,
            func.count(Video.id).label('count')
        )
        .join(Video, VideoCategory.id == Video.category_id, isouter=True)
        .where(VideoCategory.section == section)
        .group_by(VideoCategory.id, VideoCategory.name)
        .order_by(func.count(Video.id).desc())
    )
    category_stats = stats_result.all()

    return total_videos, category_stats


# ==================== PAGINATION HELPER ====================

def paginate_items(
        items: List,
        page: int,
        per_page: int
) -> Tuple[List, int, int]:
    """
    Elementlarni sahifalash

    Args:
        items: Elementlar ro'yxati
        page: Joriy sahifa
        per_page: Sahifadagi elementlar soni

    Returns:
        (joriy_sahifa_elementlari, jami_sahifalar, validlangan_sahifa)
    """
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1

    # Sahifani validatsiya qilish
    page = max(1, min(page, total_pages))

    # Joriy sahifa elementlari
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    current_items = items[start_idx:end_idx]

    return current_items, total_pages, page