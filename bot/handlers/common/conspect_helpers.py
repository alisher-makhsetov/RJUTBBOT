# bot/handlers/common/conspect_helpers.py
"""
Konspekt handler uchun yordamchi funksiyalar
Optimallashtirilgan - Chunked deletion bilan
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Tuple, Optional
from collections import defaultdict, deque
import asyncio

from db.models import ConspectCategory, Conspect

# ==================== CONSTANTS ====================
DELETE_CHUNK_SIZE = 10
MAX_MESSAGES_PER_USER = 10


# ==================== MESSAGE STORE ====================

class ConspectMessageStore:
    """Konspekt uchun message store"""

    def __init__(self):
        self.user_messages = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=MAX_MESSAGES_PER_USER))
        )

    def store_message(self, user_id: int, message_id: int, category: str = "conspect"):
        """Xabarni saqlash"""
        self.user_messages[user_id][category].append(message_id)

    def get_messages(self, user_id: int, category: str = "conspect") -> list[int]:
        """User xabarlarini olish"""
        return list(self.user_messages[user_id][category])

    def clear_user_messages(self, user_id: int, category: str = "conspect"):
        """User xabarlarini tozalash"""
        self.user_messages[user_id][category].clear()


# Global instance
conspect_message_store = ConspectMessageStore()

# ==================== MESSAGE MANAGEMENT ====================

async def store_message(user_id: int, category: str, message_id: int):
    """Xabar saqlash"""
    try:
        conspect_message_store.store_message(user_id, message_id, category)
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
    msg_ids = conspect_message_store.get_messages(user_id, category)

    if exclude_ids:
        msg_ids = [msg_id for msg_id in msg_ids if msg_id not in exclude_ids]

    # Chunking - 10 tadan parallel o'chirish
    for i in range(0, len(msg_ids), DELETE_CHUNK_SIZE):
        chunk = msg_ids[i:i + DELETE_CHUNK_SIZE]
        tasks = [_safe_delete(bot, user_id, msg_id) for msg_id in chunk]
        await asyncio.gather(*tasks, return_exceptions=True)

    # Store tozalash
    if not exclude_ids:
        conspect_message_store.clear_user_messages(user_id, category)

# ==================== DATABASE QUERIES ====================

async def get_conspect_categories(session: AsyncSession, section: str) -> List[ConspectCategory]:
    """
    Section bo'yicha konspekt kategoriyalarini olish

    Args:
        session: Database session
        section: 'MM' yoki 'SX'

    Returns:
        Kategoriyalar ro'yxati (created_at bo'yicha tartiblangan)
    """
    result = await session.execute(
        select(ConspectCategory)
        .options(selectinload(ConspectCategory.conspects))
        .where(ConspectCategory.section == section)
        .order_by(ConspectCategory.created_at)
    )
    return list(result.scalars().all())


async def get_category_conspects(
        session: AsyncSession,
        category_id: int
) -> List[Conspect]:
    """
    Kategoriya bo'yicha konspektlarni olish

    Args:
        session: Database session
        category_id: Kategoriya ID

    Returns:
        Konspektlar ro'yxati (eng yangi birinchi)
    """
    result = await session.execute(
        select(Conspect)
        .where(Conspect.category_id == category_id)
        .order_by(Conspect.created_at.desc())
    )
    return list(result.scalars().all())


async def get_category_with_conspects(
        session: AsyncSession,
        category_id: int
) -> ConspectCategory | None:
    """
    Kategoriyani konspektlar bilan birga olish

    Args:
        session: Database session
        category_id: Kategoriya ID

    Returns:
        Kategoriya yoki None
    """
    result = await session.execute(
        select(ConspectCategory)
        .options(selectinload(ConspectCategory.conspects))
        .where(ConspectCategory.id == category_id)
    )
    return result.scalar_one_or_none()


async def get_conspect_by_id(
        session: AsyncSession,
        conspect_id: int
) -> Conspect | None:
    """
    Konspektni ID bo'yicha olish

    Args:
        session: Database session
        conspect_id: Konspekt ID

    Returns:
        Konspekt yoki None
    """
    result = await session.execute(
        select(Conspect)
        .options(selectinload(Conspect.category))
        .where(Conspect.id == conspect_id)
    )
    return result.scalar_one_or_none()


async def get_conspect_statistics(
        session: AsyncSession,
        section: str
) -> Tuple[int, List[Tuple]]:
    """
    Konspekt statistikasini olish

    Args:
        session: Database session
        section: 'MM' yoki 'SX'

    Returns:
        (jami_fayllar_soni, kategoriyalar_statistikasi)
    """
    # Jami fayllar soni
    total_result = await session.execute(
        select(func.count(Conspect.id))
        .join(ConspectCategory)
        .where(ConspectCategory.section == section)
    )
    total_conspects = total_result.scalar() or 0

    # Kategoriyalar bo'yicha statistika
    stats_result = await session.execute(
        select(
            ConspectCategory.name,
            func.count(Conspect.id).label('count')
        )
        .join(Conspect, ConspectCategory.id == Conspect.category_id, isouter=True)
        .where(ConspectCategory.section == section)
        .group_by(ConspectCategory.id, ConspectCategory.name)
        .order_by(func.count(Conspect.id).desc())
    )
    category_stats = stats_result.all()

    return total_conspects, category_stats

# ==================== PAGINATION HELPER ====================
# ✅ SAQLANADI - Handler'da ishlatiladi

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