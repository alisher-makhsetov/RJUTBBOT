# bot/utils/texts.py
from aiogram.utils.i18n import gettext as _
from typing import List, Tuple


# ============================ middlewares.py ============================

def get_blocked_message() -> str:
    """User bloklangan xabari"""
    return _(
        "🚫 <b>KIRISH TAQIQLANDI</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ <b>Sizning hisobingiz bloklangan</b>\n\n"
        "Botdan foydalanish huquqingiz vaqtincha "
        "yoki doimiy cheklandi.\n\n"
        "━━━━━━━━━━━━━━━━━━━\n\n"
        "📞 <b>Aloqa uchun:</b>\n"
        "👤 Admin: @Islam_Melsovich\n\n"
        "💬 Sabab va ma'lumot olish uchun "
        "admin bilan bog'laning."
    )


# ============================ start_handler ============================

def full_name_example() -> str:
    return _("📝 Ism va Familyangizni to'liq kiriting.\n {example}").format(
        example=_("👉 Masalan : ") + "<i>Alisher Maxsetov</i>"
    )


def full_name_error() -> str:
    return _("❌ Iltimos, Ism va Familyangizni to'liq kiriting.\n {example}").format(
        example=_("👉 Masalan : ") + "<i>Alisher Maxsetov</i>"
    )


def phone_number_prompt() -> str:
    return _("📱 Telefon raqamingizni yuborish uchun, iltimos, pastdagi tugmani bosing.")


def phone_number_error() -> str:
    return _("❌ Iltimos, '📱 Raqamni yuborish' tugmasidan foydalaning.")


def get_main_menu_text_once(name: str) -> str:
    return f"{_('✋ Assalomu alaykum, Xush kelibsiz!')}\n<b>👤 {name}</b>"


def get_main_text() -> str:
    return _("🏠 <b>Bosh Sahifa</b>")


def phone_number_prompt_with_name(name: str) -> str:
    return _(
        "✅ Rahmat, <b>{name}</b>!\n\n"
        "📱 Telefon raqamingizni yuborish uchun, iltimos, pastdagi tugmani bosing."
    ).format(name=name)

# --------------------- /help ---------------------

def get_help_text(admin_link="@admin"):
    """Help komandasi uchun matn"""
    return _(
        f"""🤖 <b>BOT IMKONIYATLARI:</b>
━━━━━━━━━━━━━━━━━━━━━━━━━
🦺 <b>Mehnat muhofazasi</b>
    • Malaka darajasi bo'yicha bilim sinovlari

⚠️ <b>Sanoat xavfsizligi</b>
    • Himoya vositalarining holati    
      va sinov muddatlari
━━━━━━━━━━━━━━━━━━━━━━━━━
💬 <b>Murojaat uchun:</b> <a href="{admin_link}"><b>Admin bilan bog'lanish</b></a>""")


# ============================ language_handler ============================

def language_prompt_text() -> str:
    return _("👇 Iltimos, tilni tanlang")

def language_invalid_text() -> str:
    return _("❗️ Iltimos, tugmalardan birini tanlang")

def language_updated_text() -> str:
    return _("✅ Til muvaffaqiyatli o'zgartirildi")

def language_error_text() -> str:
    return _("❌ Tilni o'zgartirishda xatolik yuz berdi")


# ============================ MM va SX MAIN MENU ============================

def get_mm_main_text() -> str:
    return _("👷 <b>Mehnat Muhofazasi</b>\n\n👇 <i>Quyidagi bo'limlardan birini tanlang:</i>")

def get_sx_main_text() -> str:
    return _("⚠️ <b>Sanoat Xavfsizligi</b>\n\n👇 <i>Quyidagi bo'limlardan birini tanlang:</i>")


# ============================ TEST HANDLER ============================

def test_no_categories_text() -> str:
    return _(
        "📂 <b>Hozircha hech qanday Test Bo'limi mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    )


def test_categories_prompt() -> str:
    return _(
        "🧠 <b>TEST BO'LIMI</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        "👇 <b>Test Bo'limini tanlang:</b>\n\n"
    )


def test_category_empty() -> str:
    return _("❌ <b>Bu Bo'limda Testlar mavjud emas</b>\n\n")


def test_starting_text(total_questions: int) -> str:
    return _(
        "🎯 <b>Test boshlanmoqda!</b>\n\n"
        "🔢 Jami savollar: <b>{total}</b> ta\n"
        "⏱ Har bir savolga: <b>60 soniya</b>\n\n"
        "💡 <i>Tayyor bo'lsangiz, boshlaymiz...</i>"
    ).format(total=total_questions)


def test_question_header(current: int, total: int) -> str:
    return _("📝 Savol - {current}/{total}").format(current=current, total=total)


def test_time_remaining(seconds: int) -> str:
    return _("⏳ <i>Qolgan vaqt: <b>{seconds}</b> soniya</i>").format(seconds=seconds)


def test_time_up_result() -> str:
    return _("⏰ <b>Vaqt tugadi!</b>\n\n")


def test_answer_variants_header() -> str:
    return _("📝 <b>Javob variantlari:</b>\n")


def test_correct_response() -> str:
    return _("✅ <b>To'g'ri javob!</b>\n\n")


def test_incorrect_response() -> str:
    return _("❌ <b>Noto'g'ri javob!</b>\n\n")


def test_correct_response_short() -> str:
    return _("✅ To'g'ri!")


def test_incorrect_response_short() -> str:
    return _("❌ Noto'g'ri!")


def test_finished_header() -> str:
    return _("🏁 <b>TEST YAKUNLANDI!</b>\n")


def test_participant_label(name: str) -> str:
    return _("👤 <b>Ishtirokchi: {name}</b>\n\n").format(name=name)


def test_result_label(correct: int, total: int) -> str:
    return _("📊 <b>Natija:</b> {correct}/{total}\n\n").format(correct=correct, total=total)


def test_percentage_label(percentage: float) -> str:
    return _("📈 <b>Foiz:</b> <i>{percentage}%</i>\n\n").format(percentage=percentage)


def test_grade_label(grade_text: str) -> str:
    return _("<b>Baho: {grade}</b>\n\n").format(grade=grade_text)


def test_correct_answers_count(correct: int) -> str:
    return _("✅ To'g'ri javoblar: {correct}\n\n").format(correct=correct)


def test_incorrect_answers_count(incorrect: int) -> str:
    return _("❌ Noto'g'ri javoblar: {incorrect}\n\n").format(incorrect=incorrect)


# Baholar
def test_grade_excellent() -> str:
    return _("A'lo darajada!")


def test_grade_good() -> str:
    return _("Yaxshi!")


def test_grade_satisfactory() -> str:
    return _("Qoniqarli!")


def test_grade_average() -> str:
    return _("O'rtacha!")


def test_grade_unsatisfactory() -> str:
    return _("Qoniqarsiz!")


# Tabriklar
def test_congratulation_excellent() -> str:
    return _("🎊 Ajoyib natija! Siz haqiqiy bilimdon ekansiz!")


def test_congratulation_good() -> str:
    return _("👏 Yaxshi natija! Biroz ko'proq mashq qilsangiz a'lo bo'ladi!")


def test_congratulation_satisfactory() -> str:
    return _("💪 Yaxshi harakat! Davom eting!")


def test_congratulation_average() -> str:
    return _("📖 Yaxshi boshlanish! Ko'proq o'qish kerak!")


def test_congratulation_unsatisfactory() -> str:
    return _("💡 Bilimlaringizni oshirish uchun ko'proq harakat qiling!")


# Xatoliklar
def test_invalid_format_text() -> str:
    return _("❌ Noto'g'ri format!")


def test_answer_not_found_text() -> str:
    return _("❌ Javob yoki savol topilmadi!")


def test_time_expired_text() -> str:
    return _("⏰ Kechikdingiz, vaqt tugagan!")


def test_error_occurred() -> str:
    return _(
        "❌ <b>Xatolik yuz berdi</b>\n\n"
        "🔄 Iltimos, qaytadan urinib ko'ring."
    )


def test_default_user_name() -> str:
    return _("Foydalanuvchi")


def get_section_menu_text() -> str:
    """MM/SX ichidan Asosiy Menyuga qaytganda"""
    return _("🏠 <b>Asosiy Menyu</b>")


# ============================ KONSPEKT TEXTS ============================

def conspect_no_categories_text() -> str:
    """Kategoriyalar yo'q"""
    return _(
        "❌ <b>Hozircha hech qanday Konspekt Bo'limi mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    )


def conspect_categories_prompt() -> str:
    """Kategoriyalar header"""
    return _(
        "📚 <b>KONSPEKTLAR BO'LIMI</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        "📂 <b>Kategoriyani tanlang:</b>"
    )


def conspect_category_empty(category_name: str) -> str:
    """Bo'sh kategoriya"""
    return _(
        "📂 <b>{category_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❌ <b>Hozircha bu Bo'limda Konspektlar mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    ).format(category_name=category_name.upper())


def conspect_files_header(category_name: str, total: int, page: int, total_pages: int) -> str:
    """Fayllar ro'yxati header"""
    text = _(
        "📂 <b>{category_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📚 <b>Jami konspektlar:</b> <i>{total} ta</i>"
    ).format(category_name=category_name.upper(), total=total)

    if total_pages > 1:
        text += _(" ┃ 📄 <b>Sahifa:</b> <i>{page}/{total_pages}</i>").format(
            page=page,
            total_pages=total_pages
        )

    text += _("\n\n📄 <b>Batafsil ma'lumot uchun konspektni tanlang:</b>")

    return text


def conspect_file_sent_text(
        file_name: str,
        category_name: str,
        description: str = None
) -> str:
    """Fayl yuborildi - to'liq ma'lumot"""
    text = _(
        "📄 <b>{file}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📂 <b>Kategoriya:</b> {category}"
    ).format(file=file_name, category=category_name)

    if description:
        text += _("\n\n📝 <b>Tavsif:</b> {desc}").format(desc=description)

    text += _("\n\n✅ <i>Yuqoridagi faylni ko'rishingiz mumkin</i>")

    return text


def conspect_file_error_text() -> str:
    """Fayl yuborishda xatolik"""
    return _(
        "❌ <b>Faylni yuborishda xatolik yuz berdi.</b>\n\n"
        "🙏 <i>Iltimos, Admin bilan bog'laning yoki qayta urinib ko'ring.</i>"
    )


def conspect_statistics_text(total_files: int, category_stats: list) -> str:
    """Konspekt statistika"""
    text = _(
        "📊 <b>KONSPEKTLAR STATISTIKASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📚 <b>Jami konspektlar:</b> <i>{total} ta</i>\n"
    ).format(total=total_files)

    if category_stats and total_files > 0:
        text += _("📂 <b>Bo'limlar bo'yicha taqsimot:</b>\n")
        text += "━━━━━━━━━━━━━━━━━━━━\n"

        for stat in category_stats:
            if stat.count > 0:
                percentage = (stat.count / total_files * 100) if total_files > 0 else 0

                # Progress bar
                filled = int(percentage / 5)
                empty = 20 - filled
                progress_bar = "█" * filled + "░" * empty

                text += _(
                    "\n🔹 <b>{name}</b>\n"
                    "      {progress} {percentage:.1f}%\n"
                    "      <i>Konspektlar: {count} ta</i>\n"
                ).format(
                    name=stat.name,
                    progress=progress_bar,
                    percentage=percentage,
                    count=stat.count
                )

    return text


def conspect_no_statistics_text() -> str:
    """Statistika yo'q"""
    return _(
        "📊 <b>KONSPEKTLAR STATISTIKASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❌ <b>Hozircha statistika ma'lumotlari mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi"
    )


def conspect_error_text() -> str:
    """Umumiy xatolik"""
    return _(
        "❌ <b>Xatolik yuz berdi.</b>\n"
        "🙏 <i>Iltimos, qayta urinib ko'ring</i>"
    )


# ============================ VIDEO HANDLER ============================

def video_no_categories_text() -> str:
    """Kategoriyalar yo'q"""
    return _(
        "📂 <b>Hozircha hech qanday Video Bo'limi mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    )


def video_categories_prompt() -> str:
    """Kategoriyalar tanlash"""
    return _(
        "🎬 <b>VIDEO ROLIKLAR BO'LIMI</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        "📂 <b>Kategoriyani tanlang:</b>"
    )


def video_category_empty(category_name: str) -> str:
    """Bo'sh kategoriya"""
    return _(
        "📂 <b>{category}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❌ <b>Hozircha bu Bo'limda Video Roliklar mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    ).format(category=category_name.upper())


def video_list_header(
    category_name: str,
    total: int,
    page: int,
    total_pages: int
) -> str:
    """Video ro'yxati sarlavhasi"""
    text = _(
        "📂 <b>{category}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎬 <b>Jami videolar:</b> <i>{total} ta</i>"
    ).format(category=category_name.upper(), total=total)

    if total_pages > 1:
        text += _(" ┃ 📄 <b>Sahifa:</b> <i>{page}/{total_pages}</i>").format(
            page=page,
            total_pages=total_pages
        )

    text += _("\n\n🎥 <b>Batafsil ma'lumot uchun videoni tanlang:</b>")

    return text


def video_detail_text(
    video_name: str,
    category_name: str,
    description: str = None
) -> str:
    """Video yuborilgandan keyingi to'liq ma'lumot"""
    text = _(
        "🎬 <b>{video}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📂 <b>Kategoriya:</b> {category}"
    ).format(video=video_name, category=category_name)

    if description:
        text += _("\n\n📝 <b>Tavsif:</b> {desc}").format(desc=description)

    text += _("\n\n✅ <i>Yuqoridagi videoni ko'rishingiz mumkin</i>")

    return text


def video_file_error_text() -> str:
    """Video yuborishda xatolik"""
    return _(
        "❌ <b>Videoni yuborishda xatolik yuz berdi.</b>\n\n"
        "🙏 <i>Iltimos, Admin bilan bog'laning yoki qayta urinib ko'ring.</i>"
    )


def video_statistics_text(total_videos: int, category_stats: List[Tuple]) -> str:
    """Statistika matni"""
    text = _(
        "📊 <b>VIDEO MATERIALLAR STATISTIKASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎬 <b>Jami videolar:</b> <i>{total} ta</i>\n"
    ).format(total=total_videos)

    if category_stats and total_videos > 0:
        text += _("📂 <b>Bo'limlar bo'yicha taqsimot:</b>\n")
        text += "━━━━━━━━━━━━━━━━━━━━\n"

        for stat in category_stats:
            if stat.count > 0:
                percentage = (stat.count / total_videos * 100) if total_videos > 0 else 0

                # Progress bar
                filled = int(percentage / 5)
                empty = 20 - filled
                progress_bar = "█" * filled + "░" * empty

                text += _(
                    "\n🔹 <b>{name}</b>\n"
                    "      {progress} {percentage:.1f}%\n"
                    "      <i>Videolar: {count} ta</i>\n"
                ).format(
                    name=stat.name,
                    progress=progress_bar,
                    percentage=percentage,
                    count=stat.count
                )

    return text


def video_no_statistics_text() -> str:
    """Ma'lumot yo'q statistika"""
    return _(
        "📊 <b>VIDEO MATERIALLAR STATISTIKASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❌ <b>Hozircha statistika ma'lumotlari mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi"
    )


def video_error_text() -> str:
    """Umumiy xatolik"""
    return _(
        "❌ <b>Xatolik yuz berdi.</b>\n"
        "🙏 <i>Iltimos, qayta urinib ko'ring</i>"
    )


# ============================ MM ACCIDENT TEXTS ============================

import re
from typing import List, Tuple


def _extract_year_number(year_name: str) -> int:
    """
    Yil nomidan raqamni ajratib olish

    Examples:
        "2024 yil" -> 2024
        "2023" -> 2023
    """
    match = re.search(r'(\d{4})', year_name)
    return int(match.group(1)) if match else 0


def accident_main_text() -> str:
    """Baxtsiz hodisalar asosiy menyu"""
    return _(
        "⚠️ <b>BAXTSIZ HODISALAR BO'LIMI</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        "📆 <b>Quyidagi yillardan birini tanlang:</b>\n"
        "ℹ️ <i>(qavsda shu yildagi malumotlar soni)</i>"
    )


def accident_no_years_text() -> str:
    """Yillar yo'q"""
    return _(
        "❌ <b>Hozircha hech qanday Baxtsiz Hodisa ma'lumotlari mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    )


def accident_year_header_text(year_name: str, total: int, page: int, total_pages: int) -> str:
    """Yil bo'yicha hodisalar header"""
    text = _(
        "📆 <b>{year_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔢 <b>Jami malumotlar soni:</b> <i>{total} ta</i>"
    ).format(year_name=year_name.upper(), total=total)

    if total_pages > 1:
        text += _(" ┃ 📄 <b>Sahifa:</b> <i>{page}/{total_pages}</i>").format(
            page=page,
            total_pages=total_pages
        )

    text += _("\n\n📋 <b>Batafsil ma'lumot uchun tanlang:</b>")

    return text


def accident_no_accidents_text(year_name: str) -> str:
    """Yilda hodisa yo'q"""
    return _(
        "📆 <b>{year_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❌ <b>Hozircha bu bo'limdagi baxtsiz hodisalar ma'lumotlari mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    ).format(year_name=year_name.upper())


def accident_detail_text(
        title: str,
        year: str,
        category: str,
        description: str = None,
        views_count: int = 0
) -> str:
    """Hodisa detallari"""
    text = _(
        "📋 <b>{title}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📆 <b>Yil:</b> {year}\n"
        "📂 <b>Kategoriya:</b> {category}\n"
        "👁 <b>Ko'rishlar:</b> {views} marta"
    ).format(title=title, year=year, category=category, views=views_count)

    if description:
        text += _("\n\n📝 <b>Tavsif:</b> {desc}").format(desc=description)

    text += _("\n\n✅ <i>Yuqoridagi faylni ko'rishingiz mumkin</i>")

    return text


def accident_file_error_text() -> str:
    """Fayl yuborishda xatolik"""
    return _(
        "❌ <b>Faylni yuborishda xatolik yuz berdi.</b>\n\n"
        "🙏 <i>Iltimos, Admin bilan bog'laning yoki qayta urinib ko'ring.</i>"
    )


def accident_statistics_main_text(total: int, year_stats: List[Tuple]) -> str:
    """Umumiy statistika teksti (Xisobat kategoriyasi chiqarilgan + taqqoslash)"""
    text = _(
        "📊 <b>UMUMIY STATISTIKA</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    # Jami hodisalar (Xisobat kategoriyasiz)
    text += _("📈 <b>Jami Baxtsiz Hodisalar:</b> <i>{total}</i> <b>ta</b>\n").format(total=total)
    text += _("ℹ️ <i>(Xisobat hujjatlari hisobga olinmagan)</i>\n\n")

    # Yillar bo'yicha trend (oxirgi 5 yil)
    if year_stats and len(year_stats) >= 1:
        text += _("📅 <b>Yillik dinamika:</b>\n")
        text += "━━━━━━━━━━━━━━━━━━━━\n"

        # Sort years by year number for proper comparison
        sorted_years = sorted(year_stats, key=lambda x: _extract_year_number(x.name), reverse=True)

        for i, stat in enumerate(sorted_years[:5]):  # Show only last 5 years
            current_year_num = _extract_year_number(stat.name)

            # Display current year
            text += _("🔹 <b>{name} - Baxtsiz hodisalar soni:</b> <i>{count}</i> <b>ta</b>").format(
                name=stat.name,
                count=stat.count
            )

            # Find previous year for comparison (year before current)
            prev_year_data = None
            for prev_stat in sorted_years:
                prev_year_num = _extract_year_number(prev_stat.name)
                if prev_year_num == current_year_num - 1:  # Previous year
                    prev_year_data = prev_stat
                    break

            if prev_year_data and prev_year_data.count > 0:
                # Calculate change (current - previous)
                change_abs = stat.count - prev_year_data.count
                change_percent = (change_abs / prev_year_data.count * 100)

                prev_year_short = str(current_year_num - 1) + " yil"

                if change_abs > 0:
                    emoji = "📈"
                    text += _(
                        "\n{emoji} <b>{prev_year} ga Nisbatan:</b>\n"
                        "      <i>+{change_abs}</i> <b>taga yani</b> <i>(+{change_percent:.1f}%)</i> <b>ga oshgan</b>"
                    ).format(
                        emoji=emoji,
                        prev_year=prev_year_short,
                        change_abs=change_abs,
                        change_percent=change_percent
                    )
                elif change_abs < 0:
                    emoji = "📉"
                    text += _(
                        "\n{emoji} <b>{prev_year} ga Nisbatan:</b>\n"
                        "      <i>{change_abs}</i> <b>taga yani</b> <i>({change_percent:.1f}%)</i> <b>ga kamaygan</b>"
                    ).format(
                        emoji=emoji,
                        prev_year=prev_year_short,
                        change_abs=change_abs,
                        change_percent=change_percent
                    )
                else:
                    emoji = "➡️"
                    text += _("\n{emoji} <b>{prev_year} ga Nisbatan o'zgarmagan</b>").format(
                        emoji=emoji,
                        prev_year=prev_year_short
                    )

            # Add separator line after each year (except last)
            if i < len(sorted_years[:5]) - 1:
                text += "\n━━━━━━━━━━━━━━━━━━━━\n"
            else:
                text += "\n"

    return text


def accident_statistics_year_text(year_name: str, total: int, category_stats: list) -> str:
    """Yil bo'yicha statistika"""
    text = _(
        "📊 <b>{year_name} STATISTIKASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📈 <b>Jami Baxtsiz Hodisalar soni:</b> <i>{total} ta</i>\n"
        "ℹ️ <i>(Xisobat hujjatlari hisobga olinmagan)</i>\n\n"
    ).format(year_name=year_name.upper(), total=total)

    if category_stats and total > 0:
        text += _("📂 <b>Kategoriyalar bo'yicha taqsimot:</b>\n")
        text += "━━━━━━━━━━━━━━━━━━━━\n"

        for stat in category_stats:
            percentage = (stat.count / total * 100) if total > 0 else 0

            # Progress bar
            filled = int(percentage / 5)
            empty = 20 - filled
            progress_bar = "█" * filled + "░" * empty

            text += _(
                "\n🔹 <b>{name}</b>\n"
                "      {progress} {percentage:.1f}%\n"
                "      Baxtsiz hodisalar soni: <b>{count} ta</b>\n"
            ).format(
                name=stat.name,
                progress=progress_bar,
                percentage=percentage,
                count=stat.count
            )
    else:
        text += _("❌ <i>Bu yilda baxtsiz hodisalar qayd etilmagan</i>")

    return text


def accident_no_statistics_text() -> str:
    """Statistika yo'q"""
    return _(
        "📊 <b>UMUMIY STATISTIKA</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❌ <b>Hozircha statistika ma'lumotlari mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi"
    )


def accident_error_text() -> str:
    """Umumiy xatolik"""
    return _(
        "❌ <b>Xatolik yuz berdi.</b>\n"
        "🙏 <i>Iltimos, qayta urinib ko'ring</i>"
    )


# ============================ FOLDER TEXTS (MM + SX uchun umumiy) ============================

# bot/utils/texts.py

def _translate_parent_name(parent_name: str) -> str:
    """
    ✅ PARENT NAME'NI TARJIMA QILISH VA KATTA HARFGA O'TKAZISH
    """
    # 🔍 DEBUG 1: Kiruvchi qiymat
    print(f"🔍 DEBUG 1: parent_name = '{parent_name}'")

    translations = {
        "Nizomlar": _("Nizomlar"),
        "Himoya Vositalari": _("Himoya Vositalari"),
        "O'quv Texnik Mashg'ulot": _("O'quv Texnik Mashg'ulot"),
        "Kranlar": _("Kranlar"),
        "Qozonxonalar": _("Qozonxonalar"),
        "Bosim Ostidagi Ichlovchi Sig'im": _("Bosim Ostidagi Ichlovchi Sig'im"),
        "To'liq Texnik Ko'rik": _("To'liq Texnik Ko'rik"),
    }

    # 🔍 DEBUG 2: Dictionary ichidagi qiymatlar
    print(f"🔍 DEBUG 2: translations = {translations}")

    # ✅ TARJIMA
    translated = translations.get(parent_name, parent_name)

    # 🔍 DEBUG 3: Tarjima qilingan qiymat
    print(f"🔍 DEBUG 3: translated (before upper) = '{translated}'")

    # ✅ KATTA HARF
    result = translated.upper()

    # 🔍 DEBUG 4: Oxirgi natija
    print(f"🔍 DEBUG 4: result (after upper) = '{result}'")

    return result


def folder_main_text(parent_name: str, parent_emoji: str) -> str:
    """Folder asosiy matn"""
    translated_name = _translate_parent_name(parent_name)  # ← Allaqachon UPPER

    return _(
        "{emoji} <b>{parent_name} BO'LIMI</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "\n"
        "📂 <b>Papkani tanlang:</b>\n"
        "ℹ️ <i>(Statistikada batafsil ma'lumot)</i>"
    ).format(
        emoji=parent_emoji,
        parent_name=translated_name
    )


def folder_no_folders_text(parent_name: str, parent_emoji: str) -> str:
    """Folderlar yo'q matni"""
    translated_name = _translate_parent_name(parent_name)  # ← Allaqachon UPPER

    return _(
        "{emoji} <b>{parent_name} BO'LIMI</b>\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "\n"
        "❌ <b>Hozircha hech qanday papka mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n"
        "\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    ).format(
        emoji=parent_emoji,
        parent_name=translated_name
    )

def folder_files_header(
    folder_name: str,
    total: int,
    page: int,
    total_pages: int
) -> str:
    """Folder fayllari header"""
    text = _(
        "📂 <b>{folder_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📄 <b>Jami fayllar:</b> <i>{total} ta</i>"
    ).format(folder_name=folder_name.upper(), total=total)

    if total_pages > 1:
        text += _(" ┃ 📄 <b>Sahifa:</b> <i>{page}/{total_pages}</i>").format(
            page=page,
            total_pages=total_pages
        )

    text += _("\n\n📋 <b>Batafsil ma'lumot uchun faylni tanlang:</b>")

    return text


def folder_empty_text(folder_name: str) -> str:
    """Folder bo'sh"""
    return _(
        "📂 <b>{folder_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "❌ <b>Hozircha bu papkada fayllar mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi\n\n"
        "🙏 <i>Iltimos, keyinroq qayta urinib ko'ring</i>"
    ).format(folder_name=folder_name.upper())


def folder_file_detail_text(
    file_name: str,
    folder_name: str,
    description: str = None,
    views_count: int = 0
) -> str:
    """Fayl detallari"""
    text = _(
        "📄 <b>{file_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📂 <b>Papka:</b> {folder_name}\n"
        "👁 <b>Ko'rishlar:</b> {views} marta"
    ).format(
        file_name=file_name,
        folder_name=folder_name,
        views=views_count
    )

    if description:
        text += _("\n\n📝 <b>Tavsif:</b> {desc}").format(desc=description)

    text += _("\n\n✅ <i>Yuqoridagi faylni ko'rishingiz mumkin</i>")

    return text


def folder_file_error_text() -> str:
    """Fayl yuborishda xatolik"""
    return _(
        "❌ <b>Faylni yuborishda xatolik yuz berdi.</b>\n\n"
        "🙏 <i>Iltimos, Admin bilan bog'laning yoki qayta urinib ko'ring.</i>"
    )


def folder_error_text() -> str:
    """Umumiy xatolik"""
    return _(
        "❌ <b>Xatolik yuz berdi.</b>\n"
        "🙏 <i>Iltimos, qayta urinib ko'ring</i>"
    )


def folder_statistics_text(
        parent_name: str,
        parent_emoji: str,
        total_folders: int,
        total_files: int,
        folder_stats: list
) -> str:
    """Statistika matni"""
    translated_name = _translate_parent_name(parent_name)  # ← Allaqachon UPPER

    text = _(
        "{emoji} <b>{parent_name} STATISTIKASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "📂 <b>Jami papkalar:</b> <i>{total_folders} ta</i>\n"
        "📄 <b>Jami fayllar:</b> <i>{total_files} ta</i>\n"
        "\n"
    ).format(
        emoji=parent_emoji,
        parent_name=translated_name,
        total_folders=total_folders,
        total_files=total_files
    )

    if folder_stats and total_files > 0:
        text += _("📊 <b>Papkalar bo'yicha:</b>\n")
        text += "━━━━━━━━━━━━━━━━━━━━\n"

        for folder_name, file_count in folder_stats:
            percentage = (file_count / total_files * 100) if total_files > 0 else 0
            filled = int(percentage / 5)
            empty = 20 - filled
            progress_bar = "█" * filled + "░" * empty

            text += _(
                "\n📂 <b>{name}</b>\n"
                "      {progress} {percentage:.1f}%\n"
                "      <i>Fayllar: {count} ta</i>\n"
            ).format(
                name=folder_name,
                progress=progress_bar,
                percentage=percentage,
                count=file_count
            )
    else:
        text += _("❌ <i>Bu bo'limda hozircha fayllar mavjud emas</i>")

    return text


def folder_no_statistics_text(parent_name: str, parent_emoji: str) -> str:
    """Statistika yo'q"""
    translated_name = _translate_parent_name(parent_name)  # ← Allaqachon UPPER

    return _(
        "{emoji} <b>{parent_name} STATISTIKASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "❌ <b>Hozircha statistika ma'lumotlari mavjud emas.</b>\n"
        "📥 Tez orada ma'lumotlar qo'shiladi"
    ).format(
        emoji=parent_emoji,
        parent_name=translated_name
    )
