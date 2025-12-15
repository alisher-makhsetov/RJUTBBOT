# bot/buttons/inline.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from typing import List

from db.models import Group, TestCategory, TestAnswer, ConspectCategory, Conspect, VideoCategory, Video
from bot.utils.constants import ANSWER_LETTERS

# ============================== group_events.py ==============================

def channel_join_keyboard(channels: List[Group]) -> InlineKeyboardMarkup:
    """Guruh/kanallarga qo'shilish uchun inline tugmalar"""
    builder = InlineKeyboardBuilder()

    for channel in channels:
        if channel.link:
            emoji = "🏢" if "guruh" in channel.title.lower() else "📢"
            builder.button(
                text=f"{emoji} {channel.title or 'Guruh/Kanal'}",
                url=channel.link
            )

    builder.adjust(1)
    return builder.as_markup()


# ============================== test_handler.py ==============================

def test_category_keyboard(categories: List[TestCategory]) -> InlineKeyboardMarkup:
    """Test kategoriyalari"""
    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.button(
            text=category.name,
            callback_data=f"test_category:{category.id}"
        )

    builder.adjust(2)

    # ✅ Asosiy Menyu (MM/SX menyusiga qaytish)
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="back_to_section"
        )
    )

    return builder.as_markup()


def answer_keyboard(answers: List[TestAnswer], question_id: int) -> InlineKeyboardMarkup:
    """Javob tugmalari - A, B, C, D"""
    buttons = []
    row = []

    for i in range(min(len(answers), 4)):
        button = InlineKeyboardButton(
            text=ANSWER_LETTERS[i],
            callback_data=f"answer:{question_id}:{answers[i].id}"
        )
        row.append(button)

    buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def disable_answer_keyboard(
        answers: List[TestAnswer],
        question_id: int,
        selected_id: int,
        correct_id: int
) -> InlineKeyboardMarkup:
    """Javob ko'rsatish"""
    buttons = []
    row = []

    for i in range(min(len(answers), 4)):
        letter = ANSWER_LETTERS[i]

        if answers[i].id == correct_id:
            text = f"✅ {letter}"
        elif answers[i].id == selected_id and selected_id != correct_id:
            text = f"❌ {letter}"
        else:
            text = letter

        button = InlineKeyboardButton(text=text, callback_data="disabled")
        row.append(button)

    buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_with_next_question_keyboard(
        answers: List[TestAnswer],
        question_id: int,
        selected_id: int,
        correct_id: int,
        result_text: str
) -> InlineKeyboardMarkup:
    """Rasmli: Natija + javoblar"""
    buttons = []

    buttons.append([
        InlineKeyboardButton(text=result_text, callback_data="disabled")
    ])

    answer_row = []
    for i in range(min(len(answers), 4)):
        letter = ANSWER_LETTERS[i]

        if answers[i].id == correct_id:
            text = f"✅ {letter}"
        elif answers[i].id == selected_id and selected_id != correct_id:
            text = f"❌ {letter}"
        else:
            text = letter

        button = InlineKeyboardButton(text=text, callback_data="disabled")
        answer_row.append(button)

    buttons.append(answer_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_with_only_next_question_keyboard(result_text: str) -> InlineKeyboardMarkup:
    """Rasmli: Natija + keyingi savol"""
    buttons = []

    buttons.append([
        InlineKeyboardButton(text=result_text, callback_data="disabled")
    ])

    buttons.append([
        InlineKeyboardButton(text=_("👉 Keyingi savol"), callback_data="next_question")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def timeout_result_keyboard(
        answers: List[TestAnswer],
        question_id: int,
        selected_id: int,
        correct_id: int
) -> InlineKeyboardMarkup:
    """Rasmli: Vaqt tugadi"""
    buttons = []

    buttons.append([
        InlineKeyboardButton(text=_("⏰ Vaqt tugadi!"), callback_data="disabled")
    ])

    answer_row = []
    for i in range(min(len(answers), 4)):
        letter = ANSWER_LETTERS[i]
        text = f"✅ {letter}" if answers[i].id == correct_id else letter
        button = InlineKeyboardButton(text=text, callback_data="disabled")
        answer_row.append(button)

    buttons.append(answer_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def timeout_with_next_question_keyboard() -> InlineKeyboardMarkup:
    """Rasmli: Vaqt tugadi + keyingi savol"""
    buttons = []

    buttons.append([
        InlineKeyboardButton(text=_("⏰ Vaqt tugadi!"), callback_data="disabled")
    ])

    buttons.append([
        InlineKeyboardButton(text=_("👉 Keyingi savol"), callback_data="next_question")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def next_question_keyboard() -> InlineKeyboardMarkup:
    """Keyingi savol"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("👉 Keyingi savol"), callback_data="next_question")]
    ])


def back_to_categories_keyboard() -> InlineKeyboardMarkup:
    """Orqaga va Asosiy menyu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=_("↩️ Orqaga"), callback_data="back_to_categories"),
            InlineKeyboardButton(text=_("🏠 Asosiy Menyu"), callback_data="back_to_section")
        ]
    ])


def test_result_keyboard(score: int, total: int) -> InlineKeyboardMarkup:
    """Natija tugmalari"""
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    buttons = []

    if percentage >= 70:
        share_text = _(
            "📢 Men Test topshirdim:\n"
            "✅ Natija: {score}/{total}\n"
            "📈 Foiz: {percentage}%\n\n"
            "🎯 Siz ham bilim darajangizni tekshirib ko'ring:"
        ).format(score=score, total=total, percentage=percentage)

        buttons.append([
            InlineKeyboardButton(
                text=_("📤 Natijani ulashish"),
                switch_inline_query=share_text
            )
        ])

    buttons.append([
        InlineKeyboardButton(text=_("🔄 Qayta Test"), callback_data="back_to_categories")
    ])

    buttons.append([
        InlineKeyboardButton(text=_("🏠 Asosiy Menyu"), callback_data="back_to_section")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================ conspect_handler.py ============================

def conspect_category_keyboard(
        categories: list,
        page: int = 1,
        total_pages: int = 1
) -> InlineKeyboardMarkup:
    """Konspekt kategoriyalari keyboard'i - pagination bilan"""
    builder = InlineKeyboardBuilder()

    # Kategoriyalar (2 qatorda 2 ta)
    for category in categories:
        builder.button(
            text=f"📂 {category.name}",
            callback_data=f"conspect_category:{category.id}:1"
        )

    builder.adjust(2)  # ✅ 2 buttons per row (o'zgartirildi)

    # ✅ PAGINATION tugmalari
    if total_pages > 1:
        nav_buttons = []

        # Oldingi sahifa
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=_("⬅️ Oldingi"),
                    callback_data=f"conspect_categories_page:{page - 1}"
                )
            )

        # Keyingi sahifa
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=_("Keyingi ➡️"),
                    callback_data=f"conspect_categories_page:{page + 1}"
                )
            )

        if nav_buttons:
            builder.row(*nav_buttons)

    # Statistika
    builder.row(
        InlineKeyboardButton(
            text=_("📊 Statistika"),
            callback_data="conspect_statistics"
        )
    )

    # Asosiy menyu
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="conspect_back_to_section"
        )
    )

    return builder.as_markup()

def conspect_files_keyboard(
        files: list,
        category_id: int,
        current_page: int,
        total_pages: int
) -> InlineKeyboardMarkup:
    """Konspekt fayllari keyboard'i - pagination bilan"""
    builder = InlineKeyboardBuilder()

    # Fayllar (1 qatorda 1 ta)
    for file in files:
        builder.button(
            text=f"📄 {file.name}",
            callback_data=f"conspect_file:{file.id}"
        )

    builder.adjust(1)  # 1 button per row

    # Navigation tugmalari
    nav_buttons = []

    # Oldingi sahifa
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("⬅️ Oldingi"),
                callback_data=f"conspect_category:{category_id}:{current_page - 1}"
            )
        )

    # Orqaga (har doim)
    nav_buttons.append(
        InlineKeyboardButton(
            text=_("↩️ Orqaga"),
            callback_data="conspect_back_to_categories"
        )
    )

    # Keyingi sahifa
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("Keyingi ➡️"),
                callback_data=f"conspect_category:{category_id}:{current_page + 1}"
            )
        )

    # Navigation qatorini qo'shish
    if nav_buttons:
        builder.row(*nav_buttons)

    # Asosiy menyu (alohida)
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="conspect_back_to_section"
        )
    )

    return builder.as_markup()


def conspect_file_sent_keyboard(category_id: int) -> InlineKeyboardMarkup:
    """Fayl yuborilgandan keyin keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data=f"conspect_back_to_files:{category_id}"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="conspect_back_to_section"
            )
        ]
    ])


def conspect_statistics_keyboard() -> InlineKeyboardMarkup:
    """Konspekt statistika keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data="conspect_back_to_categories"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="conspect_back_to_section"
            )
        ]
    ])


def conspect_empty_category_keyboard() -> InlineKeyboardMarkup:
    """Bo'sh kategoriya keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data="conspect_back_to_categories"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="conspect_back_to_section"
            )
        ]
    ])

# ============================ video_handler.py ============================

def video_category_keyboard(
    categories: list,
    page: int = 1,
    total_pages: int = 1
) -> InlineKeyboardMarkup:
    """Video kategoriyalari keyboard'i - pagination bilan"""
    builder = InlineKeyboardBuilder()

    # Kategoriyalar (2 qatorda 2 ta)
    for category in categories:
        builder.button(
            text=f"📂 {category.name}",
            callback_data=f"video_category:{category.id}:1"
        )

    builder.adjust(2)  # 2 buttons per row

    # ✅ PAGINATION tugmalari
    if total_pages > 1:
        nav_buttons = []

        # Oldingi sahifa
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=_("⬅️ Oldingi"),
                    callback_data=f"video_categories_page:{page-1}"
                )
            )

        # Keyingi sahifa
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=_("Keyingi ➡️"),
                    callback_data=f"video_categories_page:{page+1}"
                )
            )

        if nav_buttons:
            builder.row(*nav_buttons)

    # Statistika
    builder.row(
        InlineKeyboardButton(
            text=_("📊 Statistika"),
            callback_data="video_statistics"
        )
    )

    # Asosiy menyu
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="video_back_to_section"
        )
    )

    return builder.as_markup()


def video_list_keyboard(
    videos: list,
    category_id: int,
    current_page: int,
    total_pages: int
) -> InlineKeyboardMarkup:
    """Video ro'yxati keyboard'i - pagination bilan"""
    builder = InlineKeyboardBuilder()

    # Videolar (1 qatorda 1 ta)
    for video in videos:
        builder.button(
            text=f"🎬 {video.name}",
            callback_data=f"video_file:{video.id}"
        )

    builder.adjust(1)  # 1 button per row

    # Navigation tugmalari
    nav_buttons = []

    # Oldingi sahifa
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("⬅️ Oldingi"),
                callback_data=f"video_category:{category_id}:{current_page-1}"
            )
        )

    # Orqaga (har doim)
    nav_buttons.append(
        InlineKeyboardButton(
            text=_("↩️ Orqaga"),
            callback_data="video_back_to_categories"
        )
    )

    # Keyingi sahifa
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("Keyingi ➡️"),
                callback_data=f"video_category:{category_id}:{current_page+1}"
            )
        )

    # Navigation qatorini qo'shish
    if nav_buttons:
        builder.row(*nav_buttons)

    # Asosiy menyu (alohida)
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="video_back_to_section"
        )
    )

    return builder.as_markup()


def video_sent_keyboard(category_id: int) -> InlineKeyboardMarkup:
    """Video yuborilgandan keyin keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data=f"video_back_to_list:{category_id}"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="video_back_to_section"
            )
        ]
    ])


def video_statistics_keyboard() -> InlineKeyboardMarkup:
    """Video statistika keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data="video_back_to_categories"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="video_back_to_section"
            )
        ]
    ])


def video_empty_category_keyboard() -> InlineKeyboardMarkup:
    """Bo'sh kategoriya keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data="video_back_to_categories"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="video_back_to_section"
            )
        ]
    ])


# ============================ mm_accident_handler.py ============================

def accident_years_keyboard(years: list) -> InlineKeyboardMarkup:
    """Baxtsiz hodisa yillari keyboard'i"""
    builder = InlineKeyboardBuilder()

    # Yillar (2 qatorda 2 ta)
    for year in years:
        count = len(year.accidents)
        builder.button(
            text=f"📆 {year.name} ({count})",
            callback_data=f"accident_year:{year.id}:1"
        )

    builder.adjust(2)  # 2 buttons per row

    # Statistika
    builder.row(
        InlineKeyboardButton(
            text=_("📊 Umumiy Statistika"),
            callback_data="accident_statistics_main"
        )
    )

    # Asosiy menyu
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="accident_back_to_section"
        )
    )

    return builder.as_markup()


def accident_list_keyboard(
    accidents: list,
    year_id: int,
    current_page: int,
    total_pages: int
) -> InlineKeyboardMarkup:
    """Hodisalar ro'yxati keyboard'i - pagination bilan"""
    builder = InlineKeyboardBuilder()

    # Hodisalar (1 qatorda 3 ta)
    for accident in accidents:
        builder.button(
            text=f"📋 {accident.title}",
            callback_data=f"accident_detail:{accident.id}"
        )

    builder.adjust(3)  # 3 button per row

    # Navigation tugmalari
    nav_buttons = []

    # Oldingi sahifa
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("⬅️ Oldingi"),
                callback_data=f"accident_year:{year_id}:{current_page-1}"
            )
        )

    # Orqaga (har doim)
    nav_buttons.append(
        InlineKeyboardButton(
            text=_("↩️ Orqaga"),
            callback_data="accident_back_to_years"
        )
    )

    # Keyingi sahifa
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("Keyingi ➡️"),
                callback_data=f"accident_year:{year_id}:{current_page+1}"
            )
        )

    # Navigation qatorini qo'shish
    if nav_buttons:
        builder.row(*nav_buttons)

    # Yil statistikasi
    builder.row(
        InlineKeyboardButton(
            text=_("📊 Yil Statistikasi"),
            callback_data=f"accident_statistics_year:{year_id}"
        )
    )

    # Asosiy menyu (alohida)
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="accident_back_to_section"
        )
    )

    return builder.as_markup()


def accident_detail_keyboard(year_id: int) -> InlineKeyboardMarkup:
    """Hodisa detallari keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data=f"accident_year:{year_id}:1"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="accident_back_to_section"
            )
        ]
    ])


def accident_empty_year_keyboard() -> InlineKeyboardMarkup:
    """Bo'sh yil keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data="accident_back_to_years"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="accident_back_to_section"
            )
        ]
    ])


def accident_statistics_main_keyboard() -> InlineKeyboardMarkup:
    """Umumiy statistika keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data="accident_back_to_years"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="accident_back_to_section"
            )
        ]
    ])


def accident_statistics_year_keyboard(year_id: int) -> InlineKeyboardMarkup:
    """Yil statistikasi keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data=f"accident_year:{year_id}:1"
            ),
            InlineKeyboardButton(
                text=_("📊 Umumiy Statistika"),
                callback_data="accident_statistics_main"
            )
        ],
        [
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="accident_back_to_section"
            )
        ]
    ])


# ============================ FOLDER KEYBOARDS (MM + SX uchun umumiy) ============================

def folder_list_keyboard(
        folders: list,
        page: int = 1,
        total_pages: int = 1
) -> InlineKeyboardMarkup:
    """Folderlar ro'yxati keyboard'i - pagination bilan"""
    builder = InlineKeyboardBuilder()

    # Folderlar (2 qatorda 2 ta)
    for folder in folders:
        builder.button(
            text=f"📂 {folder.name}",  # ✅ QAVS O'CHIRILDI
            callback_data=f"folder:{folder.id}:1"
        )

    builder.adjust(2)  # 2 buttons per row

    # Pagination tugmalari
    if total_pages > 1:
        nav_buttons = []

        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=_("⬅️ Oldingi"),
                    callback_data=f"folder_page:{page-1}"
                )
            )

        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=_("Keyingi ➡️"),
                    callback_data=f"folder_page:{page+1}"
                )
            )

        if nav_buttons:
            builder.row(*nav_buttons)

    # Statistika tugmasi
    builder.row(
        InlineKeyboardButton(
            text=_("📊 Statistika"),
            callback_data="folder_statistics"
        )
    )

    # Asosiy menyu
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="folder_back_to_section"
        )
    )

    return builder.as_markup()


def folder_files_keyboard(
        files: list,
        folder_id: int,
        current_page: int,
        total_pages: int
) -> InlineKeyboardMarkup:
    """Folder fayllari keyboard'i - pagination bilan"""
    builder = InlineKeyboardBuilder()

    # Fayllar (1 qatorda 1 ta)
    for file in files:
        builder.button(
            text=f"📄 {file.name}",
            callback_data=f"folder_file:{file.id}"
        )

    builder.adjust(1)  # 1 button per row

    # Navigation tugmalari
    nav_buttons = []

    # Oldingi sahifa
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("⬅️ Oldingi"),
                callback_data=f"folder:{folder_id}:{current_page - 1}"
            )
        )

    # Orqaga (har doim)
    nav_buttons.append(
        InlineKeyboardButton(
            text=_("↩️ Orqaga"),
            callback_data="folder_back_to_list"
        )
    )

    # Keyingi sahifa
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text=_("Keyingi ➡️"),
                callback_data=f"folder:{folder_id}:{current_page + 1}"
            )
        )

    # Navigation qatorini qo'shish
    if nav_buttons:
        builder.row(*nav_buttons)

    # Asosiy menyu (alohida)
    builder.row(
        InlineKeyboardButton(
            text=_("🏠 Asosiy Menyu"),
            callback_data="folder_back_to_section"
        )
    )

    return builder.as_markup()


def folder_file_sent_keyboard(folder_id: int) -> InlineKeyboardMarkup:
    """Fayl yuborilgandan keyin keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data=f"folder:{folder_id}:1"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="folder_back_to_section"
            )
        ]
    ])


def folder_empty_keyboard() -> InlineKeyboardMarkup:
    """Bo'sh folder keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data="folder_back_to_list"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="folder_back_to_section"
            )
        ]
    ])


def folder_no_folders_keyboard() -> InlineKeyboardMarkup:
    """Folderlar yo'q keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="folder_back_to_section"
            )
        ]
    ])


def folder_statistics_keyboard() -> InlineKeyboardMarkup:
    """Statistika keyboard'i"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("↩️ Orqaga"),
                callback_data="folder_back_to_list"
            ),
            InlineKeyboardButton(
                text=_("🏠 Asosiy Menyu"),
                callback_data="folder_back_to_section"
            )
        ]
    ])