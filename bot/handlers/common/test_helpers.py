# bot/handlers/common/test_helpers.py
"""
Test uchun yordamchi funksiyalar
MM va SX uchun umumiy
"""
import asyncio
import time
from collections import defaultdict, deque
from typing import List, Optional
from random import sample, shuffle

from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import TestCategory, Test, TestAnswer, test_category_association
from bot.utils.constants import ANSWER_LETTERS

# 📂 MESSAGE STORE CONSTANTS
MAX_MESSAGES_PER_USER = 5
CLEANUP_INTERVAL = 3600
DELETE_CHUNK_SIZE = 10
MAX_RETRIES = 3
RETRY_DELAY = 0.5


class OptimizedMessageStore:
    """Optimallashtirilgan xabar saqlash tizimi"""

    def __init__(self):
        self.user_messages = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=MAX_MESSAGES_PER_USER))
        )
        self.last_cleanup = time.time()

    def store_message(self, user_id: int, message_id: int, category: str = "test"):
        """Xabarni saqlash"""
        self.user_messages[user_id][category].append(message_id)
        self._periodic_cleanup()

    def get_messages(self, user_id: int, category: str = "test") -> list[int]:
        """User xabarlarini olish"""
        return list(self.user_messages[user_id][category])

    def clear_user_messages(self, user_id: int, category: str = "test"):
        """User xabarlarini tozalash"""
        self.user_messages[user_id][category].clear()

    def _periodic_cleanup(self):
        """Davriy tozalash"""
        current_time = time.time()
        if current_time - self.last_cleanup > CLEANUP_INTERVAL:
            empty_users = [
                user_id for user_id, categories in self.user_messages.items()
                if not any(messages for messages in categories.values())
            ]
            for user_id in empty_users:
                del self.user_messages[user_id]
            self.last_cleanup = current_time


# Global instance
message_store = OptimizedMessageStore()


# 🔧 MESSAGE MANAGEMENT FUNCTIONS

async def store_message(user_id: int, category: str, message_id: int):
    """Xabarni saqlash"""
    try:
        message_store.store_message(user_id, message_id, category)
    except Exception:
        pass


async def delete_user_messages(bot: Bot, user_id: int, category: str, exclude_ids: Optional[list[int]] = None):
    """User xabarlarini parallel o'chirish"""
    msg_ids = message_store.get_messages(user_id, category)

    if exclude_ids:
        msg_ids = [msg_id for msg_id in msg_ids if msg_id not in exclude_ids]

    # Chunking - katta ro'yxatlarni bo'laklarga bo'lish
    for i in range(0, len(msg_ids), DELETE_CHUNK_SIZE):
        chunk = msg_ids[i:i + DELETE_CHUNK_SIZE]
        tasks = [_safe_delete(bot, user_id, msg_id) for msg_id in chunk]
        await asyncio.gather(*tasks, return_exceptions=True)

    if not exclude_ids:
        message_store.clear_user_messages(user_id, category)


async def _safe_delete(bot: Bot, chat_id: int, msg_id: int):
    """Xavfsiz xabar o'chirish with retry"""
    for attempt in range(MAX_RETRIES):
        try:
            await bot.delete_message(chat_id, msg_id)
            return True
        except Exception:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                return False


async def send_clean_message(message: Message, text: str, reply_markup=None, category="test"):
    """Tozalab xabar yuborish"""
    await delete_user_messages(message.bot, message.chat.id, category)
    sent = await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await store_message(message.chat.id, category, sent.message_id)
    return sent


# 📊 DATABASE FUNCTIONS

async def get_test_categories(session: AsyncSession, section: str) -> List[TestCategory]:
    """
    Section bo'yicha test kategoriyalarini olish

    Args:
        session: Database session
        section: 'MM' yoki 'SX'

    Returns:
        List[TestCategory]: Kategoriyalar ro'yxati
    """
    result = await session.execute(
        select(TestCategory)
        .where(TestCategory.section == section)
        .order_by(TestCategory.created_at)
    )
    return list(result.scalars().all())


async def get_category_tests(session: AsyncSession, category_id: int, limit: int = 10) -> List[Test]:
    """
    Kategoriya bo'yicha testlarni olish (Many-to-Many)
    Random tartibda, takrorlanmaydigan

    Args:
        session: Database session
        category_id: Kategoriya ID
        limit: Maksimal savol soni (default: 10)

    Returns:
        List[Test]: Random testlar ro'yxati
    """
    result = await session.execute(
        select(Test)
        .join(test_category_association)
        .where(test_category_association.c.category_id == category_id)
    )
    all_tests = list(result.scalars().all())

    # Random tanlash
    if len(all_tests) > limit:
        return sample(all_tests, limit)
    return all_tests


async def get_test_answers(session: AsyncSession, test_id: int) -> List[TestAnswer]:
    """
    Test javoblarini olish va aralashtirib berish

    Args:
        session: Database session
        test_id: Test ID

    Returns:
        List[TestAnswer]: Aralashtirilgan javoblar
    """
    result = await session.execute(
        select(TestAnswer)
        .where(TestAnswer.test_id == test_id)
    )
    answers = list(result.scalars().all())
    shuffle(answers)
    return answers


# 🎨 TEXT FORMATTING FUNCTIONS

def format_question_text(question: Test, answers: List[TestAnswer], current_num: int, total_num: int) -> str:
    """
    Savol matnini formatlash

    Args:
        question: Test savoli
        answers: Javoblar ro'yxati
        current_num: Joriy savol raqami
        total_num: Jami savollar soni

    Returns:
        str: Formatlangan savol matni
    """
    from bot.utils.texts import test_question_header, test_answer_variants_header

    header = test_question_header(current_num, total_num)
    separator1 = "➖" * 15
    separator2 = "━" * 25

    text = f"<b>{header}</b>\n{separator1}\n"
    text += f"<b>{question.text}</b>\n{separator2}\n"

    # Javob variantlari
    text += test_answer_variants_header()
    text += "\n"
    for i, ans in enumerate(answers):
        if i < len(ANSWER_LETTERS):
            letter = ANSWER_LETTERS[i]
            text += f"<b>{letter})</b> {ans.text}\n"

    return text


def format_result_text_for_text_message(
        question: Test,
        selected_answer: TestAnswer,
        answers: List[TestAnswer],
        current_num: int,
        total_num: int
) -> str:
    """
    Rasmsiz savollar uchun javob natijasini formatlash

    Args:
        question: Test savoli
        selected_answer: Tanlangan javob
        answers: Barcha javoblar
        current_num: Joriy savol raqami
        total_num: Jami savollar soni

    Returns:
        str: Formatlangan natija matni
    """
    from bot.utils.texts import (
        test_question_header,
        test_correct_response,
        test_incorrect_response,
        test_answer_variants_header
    )

    header = test_question_header(current_num, total_num)
    separator1 = "➖" * 15
    separator2 = "━" * 25

    text = f"<b>{header}</b>\n{separator1}\n"
    text += f"<b>{question.text}</b>\n{separator2}\n"

    # Natija
    if selected_answer.is_correct:
        text += test_correct_response()
    else:
        text += test_incorrect_response()

    # Javoblar
    text += test_answer_variants_header()
    text += "\n"
    for i, ans in enumerate(answers):
        if i < len(ANSWER_LETTERS):
            letter = ANSWER_LETTERS[i]

            if ans.id == selected_answer.id and selected_answer.is_correct:
                emoji = "✅"
            elif ans.id == selected_answer.id and not selected_answer.is_correct:
                emoji = "❌"
            elif ans.is_correct:
                emoji = "✅"
            else:
                emoji = ""

            text += f"{emoji} <b>{letter})</b> {ans.text}\n"

    return text


def format_timeout_text_for_text_message(
        question: Test,
        answers: List[TestAnswer],
        current_num: int,
        total_num: int
) -> str:
    """
    Rasmsiz savollar uchun vaqt tugaganda ko'rsatiladigan matn

    Args:
        question: Test savoli
        answers: Barcha javoblar
        current_num: Joriy savol raqami
        total_num: Jami savollar soni

    Returns:
        str: Formatlangan timeout matni
    """
    from bot.utils.texts import (
        test_question_header,
        test_time_up_result,
        test_answer_variants_header
    )

    header = test_question_header(current_num, total_num)
    separator1 = "➖" * 15
    separator2 = "━" * 25

    text = f"<b>{header}</b>\n{separator1}\n"
    text += f"<b>{question.text}</b>\n{separator2}\n"

    text += test_time_up_result()
    text += test_answer_variants_header()
    text += "\n"

    for i, ans in enumerate(answers):
        if i < len(ANSWER_LETTERS):
            letter = ANSWER_LETTERS[i]
            emoji = "✅" if ans.is_correct else ""
            text += f"{emoji} <b>{letter})</b> {ans.text}\n"

    return text


# ⏱️ TIMER MANAGEMENT

async def cleanup_timer(state: FSMContext):
    """
    Timer task'ni to'xtatish

    Args:
        state: FSMContext
    """
    data = await state.get_data()
    timer_task = data.get("current_timer_task")

    if timer_task and not timer_task.done():
        timer_task.cancel()
        try:
            await timer_task
        except asyncio.CancelledError:
            pass