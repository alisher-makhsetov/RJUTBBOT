# bot/middlewares.py
from typing import Callable, Awaitable, Dict, Any, List
from aiogram import BaseMiddleware, Bot
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.utils.i18n import I18n
from bot.utils.user_helpers import get_user_by_telegram_id

from db.models import Group

MAX_STORED_MESSAGES = 2
user_warn_messages: Dict[int, list[int]] = {}  # user_id -> list of warning message_ids


def create_group_join_keyboard(groups: List[Group]) -> InlineKeyboardMarkup:
    """Guruh/kanallarga qo'shilish uchun inline tugmalar"""
    builder = InlineKeyboardBuilder()

    for group in groups:
        if group.link:  # Link mavjud bo'lsa
            # Emoji tanlash - guruh yoki kanal
            emoji = "👥" if group.title and "guruh" in group.title.lower() else "📢"

            builder.button(
                text=f"{emoji} {group.title or 'Guruh/Kanal'}",
                url=group.link
            )

    builder.adjust(1)  # Har qatorda 1 tadan tugma
    return builder.as_markup()


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)


class JoinGroupMiddleware(BaseMiddleware):
    """
    Guruh/Kanal a'zoligini tekshirish middleware
    User majburiy guruh yoki kanalga a'zo ekanligini tekshiradi
    """
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            return await self.process(handler, event, data)

    async def process(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        bot: Bot = data.get("bot")
        session: AsyncSession = data.get("session")
        user = getattr(event, "from_user", None)

        if not user:
            return await handler(event, data)

        message: Message | None = None
        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message

        if not message:
            return await handler(event, data)

        # 🔥 MUHIM: Faqat private chatda tekshirish
        if message.chat.type != "private":
            return await handler(event, data)

        # Majburiy guruh/kanallarni bazadan olish
        result = await session.execute(select(Group).where(Group.is_required == True))
        required_groups = result.scalars().all()

        # A'zo bo'lmagan guruh/kanallar ro'yxati
        not_joined_groups = []

        for group in required_groups:
            try:
                member = await bot.get_chat_member(chat_id=group.chat_id, user_id=user.id)

                if member.status == ChatMemberStatus.LEFT:
                    not_joined_groups.append(group)

                elif member.status == ChatMemberStatus.KICKED:
                    await self.send_kicked_warning(bot, message, user.id)
                    return

            except TelegramBadRequest as e:
                await self.send_error_warning(bot, message, user.id)
                print(f"[JOIN CHECK ERROR] {e}")
                return

        # Agar a'zo bo'lmagan guruh/kanallar bo'lsa
        if not_joined_groups:
            await self.send_join_warning(bot, message, user.id, not_joined_groups)
            return

        # Foydalanuvchi barcha guruh/kanallarga a'zo — davom etadi
        return await handler(event, data)

    async def send_join_warning(self, bot: Bot, message: Message, user_id: int, groups: List[Group]):
        """A'zo bo'lmagan guruh/kanallar uchun warning"""
        try:
            # User /start xabarini darhol o'chirish
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except:
                pass

            # Avvalgi warning xabarlarini o'chirish
            if user_id in user_warn_messages:
                for old_msg_id in user_warn_messages[user_id]:
                    try:
                        await bot.delete_message(chat_id=message.chat.id, message_id=old_msg_id)
                    except:
                        pass
                user_warn_messages[user_id].clear()

            # Warning text
            text = (
                "🔒 Botdan foydalanish cheklangan!\n"
                "🏢 Ushbu bot Qo‘ng‘irot MTU filiali xodimlari uchun mo‘ljallangan.\n\n"
                "📋 Botdan foydalanish uchun:\n"
                "• Quyidagi rasmiy Guruh yoki Kanalga qo'shiling\n"
                "• Administrator tomonidan tasdiqlaning\n"
                "• Shundan so‘ng Botdan to‘liq foydalanishingiz mumkin\n\n"
                "👇 Qo‘shilish uchun quyidagi tugmani bosing:"
            )

            # Inline keyboard yaratish
            keyboard = create_group_join_keyboard(groups)

            # Xabar yuborish
            sent_msg = await message.answer(text, reply_markup=keyboard)

            # Store qilish
            user_warn_messages.setdefault(user_id, []).append(sent_msg.message_id)

        except Exception as e:
            print(f"[SEND JOIN WARNING ERROR] {e}")

    async def send_kicked_warning(self, bot: Bot, message: Message, user_id: int):
        """Chetlashtirilgan foydalanuvchi uchun warning"""
        try:
            # User /start xabarini darhol o'chirish
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except:
                pass

            # Avvalgi warning xabarlarini o'chirish
            if user_id in user_warn_messages:
                for old_msg_id in user_warn_messages[user_id]:
                    try:
                        await bot.delete_message(chat_id=message.chat.id, message_id=old_msg_id)
                    except:
                        pass
                user_warn_messages[user_id].clear()

            text = (
                "❌ Siz kerakli Guruh yoki Kanalga a'zo emassiz yoki chetlashtirilgansiz.\n"
                "🤖 Botdan foydalanish uchun administrator sizni guruhga qo'shishi kerak.\n"
                "📩 Iltimos, Admin bilan bog'laning."
            )

            sent_msg = await message.answer(text)
            user_warn_messages.setdefault(user_id, []).append(sent_msg.message_id)

        except Exception as e:
            print(f"[SEND KICKED WARNING ERROR] {e}")

    async def send_error_warning(self, bot: Bot, message: Message, user_id: int):
        """Xatolik uchun warning"""
        try:
            # User /start xabarini darhol o'chirish
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except:
                pass

            # Avvalgi warning xabarlarini o'chirish
            if user_id in user_warn_messages:
                for old_msg_id in user_warn_messages[user_id]:
                    try:
                        await bot.delete_message(chat_id=message.chat.id, message_id=old_msg_id)
                    except:
                        pass
                user_warn_messages[user_id].clear()

            text = "❌ Kanal yoki guruhga kirishda xatolik yuz berdi. Iltimos, Admin bilan bog'laning."

            sent_msg = await message.answer(text)
            user_warn_messages.setdefault(user_id, []).append(sent_msg.message_id)

        except Exception as e:
            print(f"[SEND ERROR WARNING ERROR] {e}")


class UserLanguageMiddleware(BaseMiddleware):
    """
    Har requestda user tilini database'dan yuklaydi va i18n'ga o'rnatadi
    """

    def __init__(self, session_pool: async_sessionmaker[AsyncSession], i18n: I18n):
        self.session_pool = session_pool
        self.i18n = i18n
        self.default_locale = "uz"

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # User telegram_id olish
        user_obj = getattr(event, 'from_user', None)
        if not user_obj:
            self.i18n.current_locale = self.default_locale
            return await handler(event, data)

        telegram_id = user_obj.id

        # Database'dan user tilini olish
        try:
            async with self.session_pool() as session:
                user = await get_user_by_telegram_id(session, telegram_id)

                if user and user.language_code:
                    self.i18n.current_locale = user.language_code
                else:
                    self.i18n.current_locale = self.default_locale

        except Exception as e:
            print(f"Error loading user language: {e}")
            self.i18n.current_locale = self.default_locale

        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Spam oldini olish uchun rate limiting middleware"""

    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit  # Soniya
        self.user_requests = {}  # user_id: timestamp

        # Admin user IDs (spam limit yo'q)
        self.admin_ids = {
            900172087,  # Sizning telegram ID
        }

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # User ID olish
        user = getattr(event, 'from_user', None)
        if not user:
            return await handler(event, data)

        user_id = user.id

        # Admin'lar uchun rate limit yo'q
        if user_id in self.admin_ids:
            return await handler(event, data)

        # Rate limit tekshiruvi
        import time
        now = time.time()

        if user_id in self.user_requests:
            time_passed = now - self.user_requests[user_id]
            if time_passed < self.rate_limit:
                # Spam - ignore qilish
                print(f"🚫 Rate limit: User {user_id}")
                return

        # Request'ni record qilish
        self.user_requests[user_id] = now

        # Memory cleanup (1000+ user bo'lganda)
        if len(self.user_requests) > 1000:
            cleanup_threshold = 3600  # 1 soat
            users_to_remove = [
                uid for uid, timestamp in self.user_requests.items()
                if now - timestamp > cleanup_threshold
            ]
            for uid in users_to_remove:
                del self.user_requests[uid]

        return await handler(event, data)


class UserBlockMiddleware(BaseMiddleware):
    """
    User bloklangan bo'lsa, blok xabari ko'rsatadi
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # Faqat Message va CallbackQuery
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        user_obj = getattr(event, 'from_user', None)
        if not user_obj:
            return await handler(event, data)

        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        # User'ni olish (DbSessionMiddleware'dan session allaqachon ochiq)
        from db.models import User
        result = await session.execute(
            select(User).where(User.telegram_id == user_obj.id)
        )
        user = result.scalar_one_or_none()

        # BLOKLANGAN BO'LSA
        if user and not user.is_active:
            # texts.py dan import
            from bot.utils.texts import get_blocked_message

            text = get_blocked_message()  # Ko'p tillikda

            if isinstance(event, Message):
                await event.answer(text, parse_mode='HTML')
            else:  # CallbackQuery
                await event.answer(
                    text.replace('<b>', '').replace('</b>', ''),
                    show_alert=True
                )

            return  # Handler'ni to'xtatish

        # Faol - davom
        return await handler(event, data)