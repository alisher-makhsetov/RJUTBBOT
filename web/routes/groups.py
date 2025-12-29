"""
Groups Management Routes
Telegram guruhlarini boshqarish (CRUD)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func

from db import get_sync_session
from db.models import Group

groups_bp = Blueprint('groups', __name__, url_prefix='/groups')


@groups_bp.route('/')
@login_required
def list_groups():
    """Guruhlar ro'yxati"""
    session = get_sync_session()

    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Search
        search = request.args.get('search', '').strip()

        # Query
        query = session.query(Group).order_by(Group.created_at.desc())

        if search:
            query = query.filter(Group.title.ilike(f'%{search}%'))

        # Total count
        total = query.count()

        # Paginate
        offset = (page - 1) * per_page
        groups = query.limit(per_page).offset(offset).all()

        # Stats
        required_total = session.query(func.count(Group.id)).filter(
            Group.is_required == True
        ).scalar() or 0

        optional_total = session.query(func.count(Group.id)).filter(
            Group.is_required == False
        ).scalar() or 0

        # Pagination info
        total_pages = (total + per_page - 1) // per_page

    except Exception as e:
        print(f"Groups list error: {e}")
        groups = []
        total = 0
        total_pages = 0
        required_total = 0
        optional_total = 0
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template(
        'groups/list.html',
        groups=groups,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        required_total=required_total,
        optional_total=optional_total,
        search=search
    )


@groups_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_group():
    """Yangi guruh qo'shish"""
    if request.method == 'POST':
        session = get_sync_session()

        try:
            chat_id = request.form.get('chat_id', '').strip()
            title = request.form.get('title', '').strip()
            link = request.form.get('link', '').strip()
            is_required = request.form.get('is_required') == 'on'

            # Validation
            if not chat_id:
                flash('Guruh ID majburiy!', 'error')
                return render_template('groups/form.html')

            try:
                chat_id_int = int(chat_id)
            except ValueError:
                flash('Guruh ID raqam bo\'lishi kerak! (Masalan: -1001234567890)', 'error')
                return render_template('groups/form.html',
                                       chat_id=chat_id, title=title, link=link)

            # Check duplicate
            existing = session.query(Group).filter(
                Group.chat_id == chat_id_int
            ).first()

            if existing:
                flash('Bu guruh allaqachon qo\'shilgan!', 'warning')
                return render_template('groups/form.html',
                                       chat_id=chat_id, title=title, link=link)

            # Create
            group = Group(
                chat_id=chat_id_int,
                title=title or None,
                link=link or None,
                is_required=is_required
            )

            session.add(group)
            session.commit()

            flash(f'Guruh "{title or chat_id}" qo\'shildi!', 'success')
            return redirect(url_for('groups.list_groups'))

        except Exception as e:
            session.rollback()
            print(f"Group add error: {e}")
            flash(f'Xatolik: {str(e)}', 'error')
            return redirect(url_for('groups.add_group'))
        finally:
            session.close()

    return render_template('groups/form.html')


@groups_bp.route('/edit/<int:group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    """Guruhni tahrirlash"""
    session = get_sync_session()

    try:
        group = session.query(Group).get(group_id)

        if not group:
            flash('Guruh topilmadi!', 'error')
            return redirect(url_for('groups.list_groups'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            link = request.form.get('link', '').strip()
            is_required = request.form.get('is_required') == 'on'

            group.title = title or None
            group.link = link or None
            group.is_required = is_required

            session.commit()

            flash(f'Guruh "{title or group.chat_id}" tahrirlandi!', 'success')
            return redirect(url_for('groups.list_groups'))

        return render_template('groups/form.html', group=group)

    except Exception as e:
        session.rollback()
        print(f"Group edit error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('groups.list_groups'))
    finally:
        session.close()


@groups_bp.route('/delete/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    """Guruhni o'chirish"""
    session = get_sync_session()

    try:
        group = session.query(Group).get(group_id)

        if not group:
            flash('Guruh topilmadi!', 'error')
            return redirect(url_for('groups.list_groups'))

        title = group.title or str(group.chat_id)

        session.delete(group)
        session.commit()

        flash(f'"{title}" o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Group delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('groups.list_groups'))


@groups_bp.route('/toggle-required/<int:group_id>', methods=['POST'])
@login_required
def toggle_required(group_id):
    """Majburiy/Ixtiyoriy o'zgartirish"""
    session = get_sync_session()

    try:
        group = session.query(Group).get(group_id)

        if not group:
            flash('Guruh topilmadi!', 'error')
            return redirect(url_for('groups.list_groups'))

        group.is_required = not group.is_required
        session.commit()

        status = 'Majburiy' if group.is_required else 'Ixtiyoriy'
        title = group.title or str(group.chat_id)

        flash(f'"{title}" {status} holatiga o\'tkazildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Group toggle error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('groups.list_groups'))