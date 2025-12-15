# bot/utils/message_helpers.py
"""
Xabarlarni saqlash va o'chirish uchun umumiy funksiyalar
MM, SX va boshqa handlerlar uchun
"""
import asyncio
from aiogram import Bot
from aiogram.types import Message

# 📂 GLOBAL xabar saqlash
user_section_messages = {}  # MM/SX xabarlari
user_main_messages = {}  # Bosh sahifa xabarlari


def store_section_message(user_id: int, msg_id: int):
    """Bo'lim xabarini saqlash (MM yoki SX)"""
    if user_id not in user_section_messages:
        user_section_messages[user_id] = []
    user_section_messages[user_id].append(msg_id)


def store_main_message(user_id: int, msg_id: int):
    """Bosh sahifa xabarini saqlash"""
    user_main_messages[user_id] = [msg_id]  # Faqat 1 ta


async def delete_section_messages(bot: Bot, chat_id: int, user_id: int):
    """Bo'lim xabarlarini parallel o'chirish"""
    if user_id in user_section_messages:
        tasks = []
        for msg_id in user_section_messages[user_id]:
            tasks.append(safe_delete(bot, chat_id, msg_id))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        user_section_messages[user_id].clear()


async def delete_main_messages(bot: Bot, chat_id: int, user_id: int):
    """Bosh sahifa xabarlarini parallel o'chirish"""
    if user_id in user_main_messages:
        tasks = []
        for msg_id in user_main_messages[user_id]:
            tasks.append(safe_delete(bot, chat_id, msg_id))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        user_main_messages[user_id].clear()


async def safe_delete(bot: Bot, chat_id: int, msg_id: int):
    """Xavfsiz xabar o'chirish"""
    try:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except:
        pass