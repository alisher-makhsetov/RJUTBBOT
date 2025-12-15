# bot/handlers/mm/mm_accident_helpers.py
"""
MM Baxtsiz Hodisalar uchun yordamchi funksiyalar
Optimallashtirilgan - Chunked deletion bilan
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Tuple, Optional
from collections import defaultdict, deque
import asyncio

from db.models import AccidentYear, Accident, AccidentCategory, AccidentView

# ==================== CONSTANTS ====================
DELETE_CHUNK_SIZE = 10
MAX_MESSAGES_PER_USER = 10
EXCLUDED_CATEGORY = "Xisobat"  # Statistikadan chiqarib tashlanadigan kategoriya


# ==================== MESSAGE STORE ====================

class AccidentMessageStore:
    """Accident uchun message store"""

    def __init__(self):
        self.user_messages = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=MAX_MESSAGES_PER_USER))
        )

    def store_message(self, user_id: int, message_id: int, category: str = "accident"):
        """Xabarni saqlash"""
        self.user_messages[user_id][category].append(message_id)

    def get_messages(self, user_id: int, category: str = "accident") -> list[int]:
        """User xabarlarini olish"""
        return list(self.user_messages[user_id][category])

    def clear_user_messages(self, user_id: int, category: str = "accident"):
        """User xabarlarini tozalash"""
        self.user_messages[user_id][category].clear()


# Global instance
accident_message_store = AccidentMessageStore()


# ==================== MESSAGE MANAGEMENT ====================

async def store_message(user_id: int, category: str, message_id: int):
    """Xabar saqlash"""
    try:
        accident_message_store.store_message(user_id, message_id, category)
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
    msg_ids = accident_message_store.get_messages(user_id, category)

    if exclude_ids:
        msg_ids = [msg_id for msg_id in msg_ids if msg_id not in exclude_ids]

    # Chunking - 10 tadan parallel o'chirish
    for i in range(0, len(msg_ids), DELETE_CHUNK_SIZE):
        chunk = msg_ids[i:i + DELETE_CHUNK_SIZE]
        tasks = [_safe_delete(bot, user_id, msg_id) for msg_id in chunk]
        await asyncio.gather(*tasks, return_exceptions=True)

    # Store tozalash
    if not exclude_ids:
        accident_message_store.clear_user_messages(user_id, category)


# ==================== DATABASE QUERIES ====================

async def get_accident_years(session: AsyncSession) -> List[AccidentYear]:
    """
    Baxtsiz hodisa yillarini olish

    Returns:
        Yillar ro'yxati (eng yangi birinchi)
    """
    result = await session.execute(
        select(AccidentYear)
        .options(selectinload(AccidentYear.accidents))
        .order_by(AccidentYear.created_at.desc())
    )
    years = list(result.scalars().all())
    # year_number bo'yicha tartiblash
    return sorted(years, key=lambda y: y.year_number, reverse=True)


async def get_year_with_accidents(
        session: AsyncSession,
        year_id: int
) -> AccidentYear | None:
    """
    Yilni hodisalar bilan birga olish

    Args:
        session: Database session
        year_id: Yil ID

    Returns:
        Yil yoki None
    """
    result = await session.execute(
        select(AccidentYear)
        .options(selectinload(AccidentYear.accidents))
        .where(AccidentYear.id == year_id)
    )
    return result.scalar_one_or_none()


async def get_accident_by_id(
        session: AsyncSession,
        accident_id: int
) -> Accident | None:
    """
    Hodisani ID bo'yicha olish (views bilan)

    Args:
        session: Database session
        accident_id: Hodisa ID

    Returns:
        Hodisa yoki None
    """
    result = await session.execute(
        select(Accident)
        .options(
            selectinload(Accident.year),
            selectinload(Accident.category),
            selectinload(Accident.views)
        )
        .where(Accident.id == accident_id)
    )
    return result.scalar_one_or_none()


async def increment_accident_views(
        session: AsyncSession,
        accident_id: int,
        user_id: int
):
    """
    Hodisa ko'rilganlar sonini oshirish (user bo'yicha unique)

    Args:
        session: Database session
        accident_id: Hodisa ID
        user_id: Telegram user ID
    """
    try:
        # Tekshirish - user oldin ko'rganmi?
        result = await session.execute(
            select(AccidentView).where(
                AccidentView.accident_id == accident_id,
                AccidentView.user_id == user_id
            )
        )
        existing_view = result.scalar_one_or_none()

        # Agar ko'rmagan bo'lsa - qo'shish
        if not existing_view:
            new_view = AccidentView(accident_id=accident_id, user_id=user_id)
            session.add(new_view)
            await session.commit()
    except Exception:
        await session.rollback()


async def get_main_statistics(
        session: AsyncSession
) -> Tuple[int, List[Tuple]]:
    """
    Umumiy statistika (Xisobat kategoriyasi chiqarilgan)

    Returns:
        (jami_hodisalar, yillar_statistikasi)
    """
    # Jami hodisalar (Xisobat'siz)
    total_result = await session.execute(
        select(func.count(Accident.id))
        .join(AccidentCategory)
        .where(AccidentCategory.name != EXCLUDED_CATEGORY)
    )
    total_count = total_result.scalar() or 0

    # Yillar bo'yicha (Xisobat'siz)
    stats_result = await session.execute(
        select(
            AccidentYear.name,
            func.count(Accident.id).label('count')
        )
        .join(Accident)
        .join(AccidentCategory)
        .where(AccidentCategory.name != EXCLUDED_CATEGORY)
        .group_by(AccidentYear.id, AccidentYear.name)
        .order_by(AccidentYear.name.desc())
    )
    year_stats = stats_result.all()

    return total_count, year_stats


async def get_year_statistics(
        session: AsyncSession,
        year_id: int
) -> Tuple[int, List[Tuple]]:
    """
    Yil statistikasi (Xisobat kategoriyasi chiqarilgan)

    Args:
        session: Database session
        year_id: Yil ID

    Returns:
        (jami_hodisalar, kategoriyalar_statistikasi)
    """
    # Kategoriyalar bo'yicha (Xisobat'siz)
    result = await session.execute(
        select(
            AccidentCategory.name,
            func.count(Accident.id).label('count')
        )
        .join(Accident)
        .where(
            and_(
                Accident.year_id == year_id,
                AccidentCategory.name != EXCLUDED_CATEGORY
            )
        )
        .group_by(AccidentCategory.id, AccidentCategory.name)
        .order_by(func.count(Accident.id).desc())
    )
    category_stats = result.all()

    # Jami
    total = sum(stat.count for stat in category_stats)

    return total, category_stats


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