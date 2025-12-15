# bot/handlers/common/test_handler.py
"""
Test handler - MM va SX uchun umumiy
Section-aware test tizimi
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio

from bot.states import TestState
from bot.buttons.inline import (
    test_category_keyboard,
    answer_keyboard,
    next_question_keyboard,
    back_to_categories_keyboard,
    test_result_keyboard,
    disable_answer_keyboard,
    result_with_next_question_keyboard,
    result_with_only_next_question_keyboard,
    timeout_result_keyboard,
    timeout_with_next_question_keyboard
)
from bot.handlers.common.test_helpers import (
    store_message,
    delete_user_messages,
    send_clean_message,
    get_test_categories,
    get_category_tests,
    get_test_answers,
    format_question_text,
    format_result_text_for_text_message,
    format_timeout_text_for_text_message,
    cleanup_timer
)
from bot.utils.constants import QUESTION_TIME_LIMIT, MAX_QUESTIONS
from bot.utils.texts import (
    test_no_categories_text,
    test_categories_prompt,
    test_category_empty,
    test_starting_text,
    test_time_remaining,
    test_invalid_format_text,
    test_answer_not_found_text,
    test_time_expired_text,
    test_error_occurred,
    test_default_user_name,
    test_correct_response_short,
    test_incorrect_response_short,
    test_finished_header,
    test_participant_label,
    test_result_label,
    test_percentage_label,
    test_grade_label,
    test_correct_answers_count,
    test_incorrect_answers_count,
    test_grade_excellent,
    test_grade_good,
    test_grade_satisfactory,
    test_grade_average,
    test_grade_unsatisfactory,
    test_congratulation_excellent,
    test_congratulation_good,
    test_congratulation_satisfactory,
    test_congratulation_average,
    test_congratulation_unsatisfactory
)
from db.models import Test, TestAnswer, User
from bot.utils.stats import log_activity

test_router = Router()

# CONSTANTS
TIMER_UPDATE_INTERVAL = 5
ANSWER_DISPLAY_TIME = 3
TEST_START_DELAY = 4


# 🧠 TEST KATEGORIYALARINI KO'RSATISH
@test_router.message(F.text == __("📝 Test"))
async def show_test_categories(message: Message, state: FSMContext, session: AsyncSession):
    """Test kategoriyalarini ko'rsatish"""
    await store_message(message.from_user.id, "test", message.message_id)

    # Reply keyboard'ni yashirish
    temp_msg = await message.answer("...", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.1)
    await temp_msg.delete()

    # ✅ STATE'DAN SECTION OLISH (AVVAL!)
    data = await state.get_data()
    section = data.get('section', 'MM')

    # ✅ YANGI STATE BOSHLASH (ESKI MA'LUMOTLARNI TOZALASH)
    await state.clear()
    await state.set_state(TestState.choosing_category)
    await state.update_data(
        section=section,  # ← SECTION'NI QAYTA SAQLASH!
        user_telegram_id=message.from_user.id
    )

    # Kategoriyalarni olish
    categories = await get_test_categories(session, section)

    if not categories:
        text = test_no_categories_text()
        reply_markup = None
    else:
        text = test_categories_prompt()
        reply_markup = test_category_keyboard(categories)

    sent = await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")
    await store_message(message.chat.id, "test", sent.message_id)

    # Eski xabarlarni o'chirish
    await asyncio.gather(
        delete_user_messages(message.bot, message.from_user.id, "menu"),
        delete_user_messages(message.bot, message.from_user.id, "test", exclude_ids=[sent.message_id])
    )


# 🎯 TESTNI BOSHLASH
@test_router.callback_query(F.data.startswith("test_category:"))
async def start_test(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Test kategoriyasi tanlanganda testni boshlash"""
    try:
        category_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer(test_invalid_format_text())
        return

    # Testlarni olish
    questions = await get_category_tests(session, category_id, limit=MAX_QUESTIONS)

    if not questions:
        return await callback.message.edit_text(
            test_category_empty(),
            reply_markup=back_to_categories_keyboard()
        )

    # ✅ STATE'DAN SECTION OLISH
    data = await state.get_data()
    section = data.get('section', 'MM')

    # ✅ log_activity'ni to'g'ri chaqirish
    try:
        await log_activity(session, callback.from_user.id, 'test_start', section)
    except Exception as e:
        print(f"Log activity error: {e}")

    # Question ID'larini olish (lazy loading oldini olish)
    question_ids = [q.id for q in questions]

    # State'ga saqlash
    await state.update_data(
        questions=question_ids,
        index=0,
        correct=0,
        category_id=category_id,
        timer_active=True,
        current_timer_task=None
    )

    await state.set_state(TestState.answering_question)
    await callback.message.delete()

    # "Test boshlanmoqda" xabari
    start_msg = await callback.message.answer(test_starting_text(len(questions)))
    await asyncio.sleep(TEST_START_DELAY)
    await start_msg.delete()

    # Birinchi savolni yuborish
    await send_question(callback.message, state, session)


# 📤 SAVOL YUBORISH
async def send_question(message: Message, state: FSMContext, session: AsyncSession):
    """Savolni yuborish va timer boshlash"""
    data = await state.get_data()
    index = data["index"]
    question_ids = data["questions"]

    # Test tugadi
    if index >= len(question_ids):
        return await show_result(message, state, session)

    # Savolni olish
    question_id = question_ids[index]
    question = await session.get(Test, question_id)

    if not question:
        await state.update_data(index=index + 1)
        return await send_question(message, state, session)

    # Javoblarni olish
    answers = await get_test_answers(session, question.id)
    markup = answer_keyboard(answers, question.id)
    countdown = QUESTION_TIME_LIMIT

    # Savol matni
    question_text = format_question_text(question, answers, index + 1, len(question_ids))
    timer_text = lambda s: f"{question_text}\n\n{test_time_remaining(s)}"

    await state.update_data(timer_active=True, current_answers=answers)

    # Savolni yuborish
    try:
        if question.image:
            sent_msg = await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=question.image,
                caption=timer_text(countdown),
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            sent_msg = await message.answer(
                timer_text(countdown),
                reply_markup=markup,
                parse_mode="HTML"
            )

        await store_message(message.chat.id, "test", sent_msg.message_id)
    except Exception:
        await state.update_data(index=index + 1)
        return await send_question(message, state, session)

    # ⏱️ TIMER TASK
    async def countdown_timer():
        for sec in range(countdown - TIMER_UPDATE_INTERVAL, 0, -TIMER_UPDATE_INTERVAL):
            await asyncio.sleep(TIMER_UPDATE_INTERVAL)

            current_data = await state.get_data()
            if not current_data.get("timer_active", False):
                return

            try:
                updated_text = timer_text(sec)
                if question.image:
                    await sent_msg.edit_caption(
                        caption=updated_text,
                        reply_markup=markup,
                        parse_mode="HTML"
                    )
                else:
                    await sent_msg.edit_text(
                        updated_text,
                        reply_markup=markup,
                        parse_mode="HTML"
                    )
            except Exception:
                break

        # VAQT TUGADI
        current_data = await state.get_data()
        if current_data.get("timer_active", False):
            await state.update_data(index=index + 1, timer_active=False)
            correct_answer = next((a for a in answers if a.is_correct), None)

            try:
                if question.image:
                    clean_caption = format_question_text(question, answers, index + 1, len(question_ids))
                    await sent_msg.edit_caption(
                        clean_caption,
                        reply_markup=timeout_result_keyboard(
                            answers, question.id, -1,
                            correct_answer.id if correct_answer else -1
                        ),
                        parse_mode="HTML"
                    )
                else:
                    timeout_text = format_timeout_text_for_text_message(
                        question, answers, index + 1, len(question_ids)
                    )
                    await sent_msg.edit_text(
                        timeout_text,
                        reply_markup=disable_answer_keyboard(
                            answers, question.id, -1,
                            correct_answer.id if correct_answer else -1
                        ),
                        parse_mode="HTML"
                    )
            except Exception:
                pass

            await asyncio.sleep(ANSWER_DISPLAY_TIME)

            if index + 1 >= len(question_ids):
                await show_result(message, state, session)
            else:
                await state.set_state(TestState.showing_answer)
                try:
                    if question.image:
                        clean_caption = format_question_text(question, answers, index + 1, len(question_ids))
                        await sent_msg.edit_caption(
                            clean_caption,
                            reply_markup=timeout_with_next_question_keyboard(),
                            parse_mode="HTML"
                        )
                    else:
                        await sent_msg.edit_reply_markup(reply_markup=next_question_keyboard())
                except Exception:
                    pass

    timer_task = asyncio.create_task(countdown_timer())
    await state.update_data(current_timer_task=timer_task)


# ✅ JAVOB HANDLE QILISH
@test_router.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """User javob tanlaganda"""
    try:
        parts = callback.data.split(":")
        if len(parts) != 3:
            return await callback.answer(test_invalid_format_text())

        _, question_id, answer_id = parts
        answer = await session.get(TestAnswer, int(answer_id))
        question = await session.get(Test, int(question_id))
    except Exception:
        return await callback.answer(test_invalid_format_text())

    if not answer or not question:
        return await callback.answer(test_answer_not_found_text())

    data = await state.get_data()
    if not data.get("timer_active", False):
        return await callback.answer(test_time_expired_text())

    await cleanup_timer(state)

    current_answers = data.get("current_answers", [])
    correct_answer = next((a for a in current_answers if a.is_correct), None)

    correct = data["correct"] + (1 if answer.is_correct else 0)
    index = data["index"] + 1
    current_num = data["index"] + 1
    total_num = len(data["questions"])

    await state.update_data(correct=correct, index=index, timer_active=False)

    try:
        if question.image:
            result_text = test_correct_response_short() if answer.is_correct else test_incorrect_response_short()
            await callback.message.edit_reply_markup(
                reply_markup=result_with_next_question_keyboard(
                    current_answers, question.id, answer.id,
                    correct_answer.id if correct_answer else -1,
                    result_text
                )
            )
        else:
            result_text = format_result_text_for_text_message(
                question, answer, current_answers, current_num, total_num
            )
            await callback.message.edit_text(
                result_text,
                reply_markup=disable_answer_keyboard(
                    current_answers, question.id, answer.id,
                    correct_answer.id if correct_answer else -1
                ),
                parse_mode="HTML"
            )
    except Exception:
        pass

    await asyncio.sleep(ANSWER_DISPLAY_TIME)

    if index >= len(data["questions"]):
        await show_result(callback.message, state, session)
        return

    try:
        if question.image:
            result_text = test_correct_response_short() if answer.is_correct else test_incorrect_response_short()
            await callback.message.edit_reply_markup(
                reply_markup=result_with_only_next_question_keyboard(result_text)
            )
        else:
            await callback.message.edit_reply_markup(reply_markup=next_question_keyboard())
    except Exception:
        pass

    await state.set_state(TestState.showing_answer)


# 👉 KEYINGI SAVOL
@test_router.callback_query(F.data == "next_question")
async def next_question(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Keyingi savolga o'tish"""
    await callback.answer()
    await callback.message.delete()
    await send_question(callback.message, state, session)
    await state.set_state(TestState.answering_question)


# ↩️ KATEGORIYALARGA QAYTISH
@test_router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Test kategoriyalariga qaytish"""
    await cleanup_timer(state)
    await callback.answer()
    await callback.message.delete()
    await show_test_categories(callback.message, state, session)


# 🏠 MM/SX MENYUSIGA QAYTISH
@test_router.callback_query(F.data == "back_to_section")
async def back_to_section(callback: CallbackQuery, state: FSMContext):
    """MM yoki SX asosiy menyusiga qaytish"""
    await cleanup_timer(state)
    await callback.answer()

    # Section ni olish
    data = await state.get_data()
    section = data.get('section', 'MM')

    from bot.utils.message_helpers import store_section_message

    # ✅ SODDA: Avval o'chirish, keyin yuborish
    await callback.message.delete()

    if section == 'MM':
        from bot.buttons.reply import get_mm_menu_keyboard
        from bot.utils.texts import get_section_menu_text

        # Test xabarlarini o'chirish (background)
        asyncio.create_task(
            delete_user_messages(callback.bot, callback.from_user.id, "test")
        )

        # Yangi xabar yuborish
        msg = await callback.message.answer(
            get_section_menu_text(),
            reply_markup=await get_mm_menu_keyboard(),
            parse_mode="HTML"
        )

    else:  # SX
        from bot.buttons.reply import get_sx_menu_keyboard
        from bot.utils.texts import get_section_menu_text

        # Test xabarlarini o'chirish (background)
        asyncio.create_task(
            delete_user_messages(callback.bot, callback.from_user.id, "test")
        )

        # Yangi xabar yuborish
        msg = await callback.message.answer(
            get_section_menu_text(),
            reply_markup=await get_sx_menu_keyboard(),
            parse_mode="HTML"
        )

    # ✅ Yangi "Asosiy Menyu" xabarini saqlash
    store_section_message(callback.from_user.id, msg.message_id)

    # ✅ STATE NI TOZALASH VA SECTION NI SAQLASH
    await state.clear()
    await state.update_data(section=section)


# 🏁 NATIJANI KO'RSATISH
async def show_result(message: Message, state: FSMContext, session: AsyncSession):
    """Test natijasini ko'rsatish"""
    try:
        data = await state.get_data()
        correct = data.get("correct", 0)
        total = len(data.get("questions", []))
        percentage = round((correct / total) * 100, 1) if total > 0 else 0

        user_telegram_id = data.get("user_telegram_id", message.from_user.id)
        result = await session.execute(
            select(User).where(User.telegram_id == user_telegram_id)
        )
        user = result.scalar_one_or_none()
        name = user.full_name if user and user.full_name else test_default_user_name()

        if percentage >= 90:
            grade_emoji = "🏆"
            grade_text = test_grade_excellent()
            congrats = test_congratulation_excellent()
        elif percentage >= 80:
            grade_emoji = "🥇"
            grade_text = test_grade_good()
            congrats = test_congratulation_good()
        elif percentage >= 70:
            grade_emoji = "🥈"
            grade_text = test_grade_satisfactory()
            congrats = test_congratulation_satisfactory()
        elif percentage >= 60:
            grade_emoji = "🥉"
            grade_text = test_grade_average()
            congrats = test_congratulation_average()
        else:
            grade_emoji = "📚"
            grade_text = test_grade_unsatisfactory()
            congrats = test_congratulation_unsatisfactory()

        header = test_finished_header()
        separator = "▬" * 18 + "\n\n"

        result_text = (
            f"{header}{separator}"
            f"{test_participant_label(name)}"
            f"{test_result_label(correct, total)}"
            f"{test_percentage_label(percentage)}"
            f"{grade_emoji} {test_grade_label(grade_text)}"
            f"{test_correct_answers_count(correct)}"
            f"{test_incorrect_answers_count(total - correct)}"
            f"{separator}"
            f"{congrats}"
        )

        await send_clean_message(
            message,
            result_text,
            reply_markup=test_result_keyboard(correct, total),
            category="test"
        )
        await state.set_state(TestState.finished)

    except Exception:
        try:
            await send_clean_message(message, test_error_occurred(), category="test")
        except Exception:
            pass