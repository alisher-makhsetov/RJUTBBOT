# web/routes/dashboard.py
from flask import Blueprint, render_template, session, flash
from flask_login import login_required
from db import get_sync_session
from db.models import (
    Folder, File, Accident, User,
    ConspectCategory, Conspect,
    VideoCategory, Video,
    TestCategory, Test,
    AccidentYear, AccidentCategory, test_category_association,
    UserActivity, AccidentView
)
from sqlalchemy import func, desc, extract, distinct
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard index page with statistics"""

    # ✅ LOGIN SUCCESS FLASH MESSAGE
    if session.pop('just_logged_in', False):
        flash('Tizimga muvaffaqiyatli kirdingiz!', 'success')

    db_session = get_sync_session()

    try:
        # ==================== JORIY OY VA YIL ====================
        current_month = datetime.now().month
        current_year = datetime.now().year

        # ========== ASOSIY STATISTIKA ==========
        folder_count = db_session.query(func.count(Folder.id)).scalar() or 0
        file_count = db_session.query(func.count(File.id)).scalar() or 0
        accident_count = db_session.query(func.count(Accident.id)).scalar() or 0
        user_count = db_session.query(func.count(User.id)).scalar() or 0

        # ========== QO'SHIMCHA STATISTIKA ==========
        accident_years_count = db_session.query(func.count(AccidentYear.id)).scalar() or 0
        accident_categories_count = db_session.query(func.count(AccidentCategory.id)).scalar() or 0
        conspect_categories_count = db_session.query(func.count(ConspectCategory.id)).scalar() or 0
        conspect_count = db_session.query(func.count(Conspect.id)).scalar() or 0
        video_categories_count = db_session.query(func.count(VideoCategory.id)).scalar() or 0
        video_count = db_session.query(func.count(Video.id)).scalar() or 0
        test_categories_count = db_session.query(func.count(TestCategory.id)).scalar() or 0
        test_count = db_session.query(func.count(Test.id)).scalar() or 0

        # ========== BO'LIMLAR BO'YICHA ==========
        mm_folders = db_session.query(func.count(Folder.id)).filter(Folder.section == 'MM').scalar() or 0
        sx_folders = db_session.query(func.count(Folder.id)).filter(Folder.section == 'SX').scalar() or 0

        mm_conspects = db_session.query(func.count(Conspect.id)).join(ConspectCategory).filter(
            ConspectCategory.section == 'MM'
        ).scalar() or 0
        sx_conspects = db_session.query(func.count(Conspect.id)).join(ConspectCategory).filter(
            ConspectCategory.section == 'SX'
        ).scalar() or 0

        mm_videos = db_session.query(func.count(Video.id)).join(VideoCategory).filter(
            VideoCategory.section == 'MM'
        ).scalar() or 0
        sx_videos = db_session.query(func.count(Video.id)).join(VideoCategory).filter(
            VideoCategory.section == 'SX'
        ).scalar() or 0

        mm_tests = db_session.query(func.count(Test.id)).join(
            test_category_association, Test.id == test_category_association.c.test_id
        ).join(
            TestCategory, TestCategory.id == test_category_association.c.category_id
        ).filter(
            TestCategory.section == 'MM'
        ).distinct().scalar() or 0

        sx_tests = db_session.query(func.count(Test.id)).join(
            test_category_association, Test.id == test_category_association.c.test_id
        ).join(
            TestCategory, TestCategory.id == test_category_association.c.category_id
        ).filter(
            TestCategory.section == 'SX'
        ).distinct().scalar() or 0

        # ========== GRAFIKLAR UCHUN MA'LUMOTLAR ==========

        # 1. OYLIK FAOLLIK - UMUMIY (5 ta asosiy)
        monthly_activity_stats = db_session.query(
            UserActivity.activity_type,
            func.count(UserActivity.id).label('count')
        ).filter(
            extract('month', UserActivity.created_at) == current_month,
            extract('year', UserActivity.created_at) == current_year
        ).group_by(UserActivity.activity_type).all()

        activity_labels = []
        activity_counts = []

        activity_names = {
            'test_start': 'Test Boshlash',
            'conspect_view': 'Konspekt Ko\'rish',
            'video_view': 'Video Ko\'rish',
            'folder_open': 'Papka Ochish',
            'accident_view': 'Hodisa Ko\'rish'
        }

        # Tartib: test, conspect, video, folder, accident
        ordered_types = ['test_start', 'conspect_view', 'video_view', 'folder_open', 'accident_view']
        activity_dict = {item[0]: item[1] for item in monthly_activity_stats}

        for activity_type in ordered_types:
            activity_labels.append(activity_names[activity_type])
            activity_counts.append(activity_dict.get(activity_type, 0))

        # 2. PAPKALAR BO'YICHA FAOLLIK - BATAFSIL (7 ta papka)
        folder_activity_stats = db_session.query(
            UserActivity.parent_type,
            func.count(UserActivity.id).label('count')
        ).filter(
            UserActivity.activity_type == 'folder_open',
            UserActivity.parent_type.isnot(None),
            extract('month', UserActivity.created_at) == current_month,
            extract('year', UserActivity.created_at) == current_year
        ).group_by(UserActivity.parent_type).all()

        folder_labels = []
        folder_counts = []

        folder_names = {
            'nizomlar': 'Nizomlar',
            'himoya_vositalari': 'Himoya Vositalari',
            'oquv_texnik': 'O\'quv Texnik Mashg\'ulot',
            'kranlar': 'Kranlar',
            'qozonxonalar': 'Qozonxonalar',
            'bosim_idishlari': 'Bosim Ostidagi Sig\'im',
            'toliq_texnik': 'To\'liq Texnik Ko\'rik'
        }

        if folder_activity_stats:
            # Countga ko'ra tartiblash (eng ko'p birinchi)
            sorted_folders = sorted(folder_activity_stats, key=lambda x: x[1], reverse=True)
            for parent_type, count in sorted_folders:
                folder_labels.append(folder_names.get(parent_type, parent_type))
                folder_counts.append(count)
        else:
            folder_labels = ['Ma\'lumot yo\'q']
            folder_counts = [0]

        # 3. BO'LIMLAR BO'YICHA FAOLLIK (MM vs SX)

        # 3.1 Jami Harakatlar (Oylik)
        section_total_stats = db_session.query(
            UserActivity.section,
            func.count(UserActivity.id).label('count')
        ).filter(
            UserActivity.section.isnot(None),
            extract('month', UserActivity.created_at) == current_month,
            extract('year', UserActivity.created_at) == current_year
        ).group_by(UserActivity.section).all()

        section_total_labels = []
        section_total_counts = []

        if section_total_stats:
            for section_name, count in section_total_stats:
                if section_name:
                    section_total_labels.append(
                        'MM (Mehnat Muhofazasi)' if section_name == 'MM' else 'SX (Sanoat Xavfsizligi)')
                    section_total_counts.append(count)
        else:
            section_total_labels = ['MM (Mehnat Muhofazasi)', 'SX (Sanoat Xavfsizligi)']
            section_total_counts = [0, 0]

        # 3.2 Unique Foydalanuvchilar (Oylik)
        section_unique_stats = db_session.query(
            UserActivity.section,
            func.count(distinct(UserActivity.user_id)).label('count')
        ).filter(
            UserActivity.section.isnot(None),
            extract('month', UserActivity.created_at) == current_month,
            extract('year', UserActivity.created_at) == current_year
        ).group_by(UserActivity.section).all()

        section_unique_labels = []
        section_unique_counts = []

        if section_unique_stats:
            for section_name, count in section_unique_stats:
                if section_name:
                    section_unique_labels.append(
                        'MM (Mehnat Muhofazasi)' if section_name == 'MM' else 'SX (Sanoat Xavfsizligi)')
                    section_unique_counts.append(count)
        else:
            section_unique_labels = ['MM (Mehnat Muhofazasi)', 'SX (Sanoat Xavfsizligi)']
            section_unique_counts = [0, 0]

        # 4. OXIRGI 7 KUN FAOLLIGI (UNIQUE USERLAR)
        seven_days_ago = datetime.now() - timedelta(days=7)

        daily_unique_stats = db_session.query(
            func.date(UserActivity.created_at).label('date'),
            func.count(distinct(UserActivity.user_id)).label('count')
        ).filter(
            UserActivity.created_at >= seven_days_ago
        ).group_by(func.date(UserActivity.created_at)).all()

        daily_labels = []
        daily_counts = []

        # So'nggi 7 kunni to'ldirish
        for i in range(7):
            day = datetime.now() - timedelta(days=6 - i)
            daily_labels.append(day.strftime('%d.%m'))

            found = False
            for date, count in daily_unique_stats:
                if date == day.date():
                    daily_counts.append(count)
                    found = True
                    break
            if not found:
                daily_counts.append(0)

        # 5. MM VS SX TESTLAR
        test_comparison_labels = ['MM Testlari', 'SX Testlari']
        test_comparison_counts = [mm_tests, sx_tests]

        # 6. MM VS SX KONSPEKTLAR
        conspect_comparison_labels = ['MM Konspektlari', 'SX Konspektlari']
        conspect_comparison_counts = [mm_conspects, sx_conspects]

        # 7. BAXTSIZ HODISALAR YILLAR BO'YICHA ✅ YANGI!
        accidents_by_year = db_session.query(
            AccidentYear.name,
            func.count(Accident.id).label('count')
        ).join(Accident).group_by(AccidentYear.id, AccidentYear.name).order_by(AccidentYear.name).all()

        accident_year_labels = []
        accident_year_counts = []

        if accidents_by_year:
            for year_name, count in accidents_by_year:
                accident_year_labels.append(year_name)
                accident_year_counts.append(count)
        else:
            # Demo data - yillar
            accident_year_labels = [f'{current_year - 4 + i}-yil' for i in range(5)]
            accident_year_counts = [0] * 5

        # 8. MM VS SX VIDEOLAR
        video_comparison_labels = ['MM Videolari', 'SX Videolari']
        video_comparison_counts = [mm_videos, sx_videos]

    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()

        # Default values
        folder_count = file_count = accident_count = user_count = 0
        accident_years_count = accident_categories_count = 0
        conspect_categories_count = conspect_count = 0
        video_categories_count = video_count = 0
        test_categories_count = test_count = 0
        mm_folders = sx_folders = 0
        mm_conspects = sx_conspects = 0
        mm_videos = sx_videos = 0
        mm_tests = sx_tests = 0

        # Demo data
        activity_labels = ['Test Boshlash', 'Konspekt Ko\'rish', 'Video Ko\'rish', 'Papka Ochish', 'Hodisa Ko\'rish']
        activity_counts = [0, 0, 0, 0, 0]
        folder_labels = ['Ma\'lumot yo\'q']
        folder_counts = [0]
        section_total_labels = ['MM (Mehnat Muhofazasi)', 'SX (Sanoat Xavfsizligi)']
        section_total_counts = [0, 0]
        section_unique_labels = ['MM (Mehnat Muhofazasi)', 'SX (Sanoat Xavfsizligi)']
        section_unique_counts = [0, 0]
        daily_labels = [(datetime.now() - timedelta(days=6 - i)).strftime('%d.%m') for i in range(7)]
        daily_counts = [0] * 7
        test_comparison_labels = ['MM Testlari', 'SX Testlari']
        test_comparison_counts = [0, 0]
        conspect_comparison_labels = ['MM Konspektlari', 'SX Konspektlari']
        conspect_comparison_counts = [0, 0]
        accident_year_labels = [f'{datetime.now().year - 4 + i}-yil' for i in range(5)]
        accident_year_counts = [0] * 5
        video_comparison_labels = ['MM Videolari', 'SX Videolari']
        video_comparison_counts = [0, 0]

    finally:
        db_session.close()

    return render_template(
        'dashboard/index.html',
        now=datetime.now(),
        # Asosiy
        folder_count=folder_count,
        file_count=file_count,
        accident_count=accident_count,
        user_count=user_count,
        # Qo'shimcha
        accident_years_count=accident_years_count,
        accident_categories_count=accident_categories_count,
        conspect_categories_count=conspect_categories_count,
        conspect_count=conspect_count,
        video_categories_count=video_categories_count,
        video_count=video_count,
        test_categories_count=test_categories_count,
        test_count=test_count,
        # Bo'limlar
        mm_folders=mm_folders,
        sx_folders=sx_folders,
        mm_conspects=mm_conspects,
        sx_conspects=sx_conspects,
        mm_videos=mm_videos,
        sx_videos=sx_videos,
        mm_tests=mm_tests,
        sx_tests=sx_tests,
        # Grafiklar (JSON)
        activity_labels=json.dumps(activity_labels),
        activity_counts=json.dumps(activity_counts),
        folder_labels=json.dumps(folder_labels),
        folder_counts=json.dumps(folder_counts),
        section_labels=json.dumps(section_total_labels),
        section_counts=json.dumps(section_total_counts),
        section_unique_labels=json.dumps(section_unique_labels),
        section_unique_counts=json.dumps(section_unique_counts),
        daily_labels=json.dumps(daily_labels),
        daily_counts=json.dumps(daily_counts),
        test_comparison_labels=json.dumps(test_comparison_labels),
        test_comparison_counts=json.dumps(test_comparison_counts),
        conspect_comparison_labels=json.dumps(conspect_comparison_labels),
        conspect_comparison_counts=json.dumps(conspect_comparison_counts),
        accident_year_labels=json.dumps(accident_year_labels),
        accident_year_counts=json.dumps(accident_year_counts),
        video_comparison_labels=json.dumps(video_comparison_labels),
        video_comparison_counts=json.dumps(video_comparison_counts),
    )