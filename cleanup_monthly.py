# cleanup_monthly.py
"""
Oylik Database tozalash
Faqat joriy oyning ma'lumotlarini saqlaydi
O'tgan oylar avtomatik o'chiriladi
"""

from datetime import datetime
from sqlalchemy import delete
import sys
import os

# Project root'ni PATH'ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_sync_session
from db.models import UserActivity


def cleanup_keep_current_month():
    """
    Faqat joriy oyning ma'lumotlarini saqlab qolish
    O'tgan oylarning hammasi o'chiriladi

    Returns:
        tuple: (o'chirilgan_soni, qolgan_soni)
    """
    session = get_sync_session()

    try:
        # Joriy oyning 1-sanasi
        today = datetime.now()
        first_day_of_month = today.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        current_month_name = today.strftime('%B %Y')  # "Dekabr 2024"

        print("\n" + "=" * 60)
        print("🗑️  OYLIK DATABASE TOZALASH")
        print("=" * 60)
        print(f"📅 Joriy oy: {current_month_name}")
        print(f"🔍 O'chirish: {first_day_of_month.strftime('%Y-%m-%d')} dan oldingi")
        print("=" * 60 + "\n")

        # O'chirishdan OLDIN statistika
        total_before = session.query(UserActivity).count()
        old_count = session.query(UserActivity).filter(
            UserActivity.created_at < first_day_of_month
        ).count()
        current_count = session.query(UserActivity).filter(
            UserActivity.created_at >= first_day_of_month
        ).count()

        print(f"📊 O'chirishdan OLDIN:")
        print(f"   • Jami ma'lumotlar: {total_before} ta")
        print(f"   • O'chiriladi: {old_count} ta (eski oylar)")
        print(f"   • Qoladi: {current_count} ta (joriy oy)\n")

        # O'CHIRISH
        if old_count > 0:
            print(f"🔄 O'chirish jarayoni boshlandi...\n")

            result = session.execute(
                delete(UserActivity).where(
                    UserActivity.created_at < first_day_of_month
                )
            )

            deleted_count = result.rowcount
            session.commit()

            print(f"✅ {deleted_count} ta eski ma'lumot o'chirildi!")

        else:
            deleted_count = 0
            print(f"ℹ️  O'chirish kerak emas (eski ma'lumot yo'q)")

        # O'chirishdan KEYIN statistika
        total_after = session.query(UserActivity).count()

        # Eng eski va eng yangi ma'lumot
        oldest = session.query(UserActivity).order_by(
            UserActivity.created_at.asc()
        ).first()

        newest = session.query(UserActivity).order_by(
            UserActivity.created_at.desc()
        ).first()

        print(f"\n📊 O'chirishdan KEYIN:")
        print(f"   • Jami ma'lumotlar: {total_after} ta")

        if oldest:
            print(f"   • Eng eski: {oldest.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   • Eng eski: (ma'lumot yo'q)")

        if newest:
            print(f"   • Eng yangi: {newest.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   • Eng yangi: (ma'lumot yo'q)")

        # Database hajmi (taxminiy)
        db_size_mb = (total_after * 100) / (1024 * 1024)  # 1 yozuv ≈ 100 byte
        print(f"   • Taxminiy hajm: {db_size_mb:.2f} MB")

        print("\n" + "=" * 60)
        print("✅ TOZALASH MUVAFFAQIYATLI TUGADI!")
        print("=" * 60 + "\n")

        return deleted_count, total_after

    except Exception as e:
        session.rollback()
        print(f"\n❌ XATOLIK: {e}\n")
        import traceback
        traceback.print_exc()
        return 0, 0

    finally:
        session.close()


def show_monthly_statistics():
    """
    Oylik statistikani ko'rsatish (qo'shimcha)
    """
    session = get_sync_session()

    try:
        today = datetime.now()
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Joriy oyda activity type bo'yicha
        from sqlalchemy import func

        stats = session.query(
            UserActivity.activity_type,
            func.count(UserActivity.id).label('count')
        ).filter(
            UserActivity.created_at >= first_day
        ).group_by(UserActivity.activity_type).all()

        if stats:
            print("\n" + "=" * 60)
            print(f"📊 {today.strftime('%B %Y').upper()} STATISTIKASI")
            print("=" * 60)

            activity_names = {
                'test_start': 'Test Boshlash',
                'conspect_view': 'Konspekt Ko\'rish',
                'video_view': 'Video Ko\'rish',
                'folder_open': 'Papka Ochish',
                'accident_view': 'Hodisa Ko\'rish'
            }

            for activity_type, count in sorted(stats, key=lambda x: x[1], reverse=True):
                name = activity_names.get(activity_type, activity_type)
                print(f"   • {name}: {count} ta")

            print("=" * 60 + "\n")

    except Exception as e:
        print(f"❌ Statistika xatoligi: {e}")
    finally:
        session.close()


def main():
    """
    Main funksiyasi
    """
    # Tozalash
    deleted, remaining = cleanup_keep_current_month()

    # Qo'shimcha statistika
    if remaining > 0:
        show_monthly_statistics()


if __name__ == "__main__":
    main()