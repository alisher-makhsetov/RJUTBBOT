# bot/utils/stats.py
"""
Foydalanuvchi faolligi statistikasini saqlash
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User, UserActivity


async def log_activity(
        session: AsyncSession,
        telegram_id: int,  # ✅ O'ZGARDI: user_id → telegram_id
        activity_type: str,
        section: str = None,
        parent_type: str = None
):
    """
    Foydalanuvchi faolligini saqlash

    Args:
        session: Database session
        telegram_id: Telegram user ID (from callback.from_user.id)
        activity_type: Faollik turi ('test_start', 'conspect_view', ...)
        section: 'MM' yoki 'SX'
        parent_type: 'nizomlar', 'kranlar', ... (agar folder bo'lsa)

    Examples:
        # Test boshlandi
        await log_activity(session, telegram_id, 'test_start', 'MM')

        # Konspekt ko'rildi
        await log_activity(session, telegram_id, 'conspect_view', 'SX')

        # Nizomlar ochildi
        await log_activity(session, telegram_id, 'folder_open', 'MM', 'nizomlar')
    """
    try:
        # ✅ YANGI: Telegram ID orqali User topish
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            # User topilmasa, log qilmaymiz
            return

        # ✅ TO'G'RI: Database User.id ni ishlatish
        activity = UserActivity(
            user_id=user.id,  # ← Database User.id
            activity_type=activity_type,
            section=section,
            parent_type=parent_type
        )
        session.add(activity)
        await session.commit()

    except Exception as e:
        # Xatolik bo'lsa ham bot to'xtamaydi
        print(f"Log activity error: {e}")
        await session.rollback()