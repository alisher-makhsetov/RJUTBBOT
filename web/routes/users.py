# web/routes/users.py
"""
Users Routes - Bot foydalanuvchilari
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timedelta

from db import get_sync_session
from db.models import User, UserActivity

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/list')
@login_required
def list_users():
    """User ro'yxati"""
    with get_sync_session() as session:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)  # ← DEFAULT 20

        # Filter
        search = request.args.get('search', '')
        language = request.args.get('language', '')
        is_active = request.args.get('is_active', '')

        # Query
        query = session.query(User)

        if search:
            query = query.filter(
                (User.full_name.ilike(f'%{search}%')) |
                (User.phone_number.ilike(f'%{search}%')) |
                (User.username.ilike(f'%{search}%'))
            )

        if language:
            query = query.filter(User.language_code == language)

        if is_active:
            query = query.filter(User.is_active == (is_active == 'true'))

        # Total
        total = query.count()

        # Paginate
        users = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        # Statistics
        stats = {
            'total': session.query(User).count(),
            'active': session.query(User).filter(User.is_active == True).count(),
            'uz': session.query(User).filter(User.language_code == 'uz').count(),
            'ru': session.query(User).filter(User.language_code == 'ru').count(),
            'kk': session.query(User).filter(User.language_code == 'kk').count(),
            'today': session.query(User).filter(
                User.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
            ).count(),
        }

        return render_template(
            'users/list.html',
            users=users,
            stats=stats,
            page=page,
            per_page=per_page,
            total=total,
            search=search,
            language=language,
            is_active=is_active
        )


@users_bp.route('/toggle_active/<int:user_id>', methods=['POST'])
@login_required
def toggle_active(user_id):
    """User active/inactive almashtirish"""
    with get_sync_session() as session:
        user = session.query(User).filter(User.id == user_id).first()

        if not user:
            flash('Foydalanuvchi topilmadi!', 'error')
            return redirect(url_for('users.list_users'))

        # Toggle
        user.is_active = not user.is_active
        session.commit()

        status = 'blokdan chiqarildi' if user.is_active else 'bloklandi'
        flash(f'{user.full_name} {status}!', 'success')

        return redirect(url_for('users.list_users'))


@users_bp.route('/view/<int:user_id>')
@login_required
def view_user(user_id):
    """User tafsilotlari"""
    with get_sync_session() as session:
        user = session.query(User).filter(User.id == user_id).first()

        if not user:
            flash('Foydalanuvchi topilmadi!', 'error')
            return redirect(url_for('users.list_users'))

        # Activity
        activities = session.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(UserActivity.created_at.desc()).limit(50).all()

        # Statistics
        activity_stats = {
            'total': session.query(UserActivity).filter(UserActivity.user_id == user_id).count(),
            'tests': session.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == 'test_start'
            ).count(),
            'conspects': session.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == 'conspect_view'
            ).count(),
            'videos': session.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == 'video_view'
            ).count(),
        }

        return render_template(
            'users/view.html',
            user=user,
            activities=activities,
            activity_stats=activity_stats
        )