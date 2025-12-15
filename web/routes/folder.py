# web/routes/folder.py
"""
Folder Routes - CRUD Operations with Pagination
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from db import get_sync_session
from db.models import Folder
from sqlalchemy import func

folder_bp = Blueprint('folder', __name__, url_prefix='/folder')


@folder_bp.route('/')
@folder_bp.route('/list')
@login_required
def list():
    """List all folders with pagination"""
    session = get_sync_session()

    try:
        # Get parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        section_filter = request.args.get('section', '')

        # Query
        query = session.query(Folder)

        if search:
            query = query.filter(Folder.name.ilike(f'%{search}%'))

        if section_filter:
            query = query.filter(Folder.section == section_filter)

        # Order by
        query = query.order_by(Folder.order_index.asc(), Folder.created_at.desc())

        # Total count
        total = query.count()

        # Pagination
        offset = (page - 1) * per_page
        folders = query.limit(per_page).offset(offset).all()

        # Count files for each folder
        for folder in folders:
            folder.files_count = len(folder.files) if folder.files else 0

        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

    except Exception as e:
        print(f"Folder list error: {e}")
        folders = []
        total = 0
        total_pages = 0
        has_prev = False
        has_next = False
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template(
        'folder/list.html',
        folders=folders,
        search=search,
        section_filter=section_filter,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next
    )


@folder_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new folder"""
    if request.method == 'POST':
        session = get_sync_session()

        try:
            # Get form data
            name = request.form.get('name', '').strip()
            section = request.form.get('section', '').strip()
            parent_type = request.form.get('parent_type', '').strip()
            order_index = request.form.get('order_index', 0)

            # Validate
            if not name:
                flash('Papka nomi kiritilishi shart!', 'error')
                return redirect(url_for('folder.create'))

            if not section or section not in ['MM', 'SX']:  # ✅ QO'SHILDI
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('folder.create'))

            if not parent_type:
                flash('Papka turi tanlanishi shart!', 'error')
                return redirect(url_for('folder.create'))

            # ✅ YANGI VALIDATION - Papka turi to'g'ri ekanligini tekshirish
            valid_parent_types = [choice[0] for choice in Folder.PARENT_TYPE_CHOICES]
            if parent_type not in valid_parent_types:
                flash('Noto\'g\'ri papka turi tanlandi!', 'error')
                return redirect(url_for('folder.create'))

            # ✅ YANGI VALIDATION - Section va parent_type mos ekanligini tekshirish
            # MM bo'limlari
            mm_types = ['himoya_vositalari', 'nizomlar', 'oquv_texnik']
            # SX bo'limlari
            sx_types = ['kranlar', 'qozonxonalar', 'bosim_idishlari', 'toliq_texnik']

            if section == 'MM' and parent_type not in mm_types:
                flash('Tanlangan papka turi MM bo\'limiga mos kelmaydi!', 'error')
                return redirect(url_for('folder.create'))

            if section == 'SX' and parent_type not in sx_types:
                flash('Tanlangan papka turi SX bo\'limiga mos kelmaydi!', 'error')
                return redirect(url_for('folder.create'))

            # Create folder
            folder = Folder(
                name=name,
                section=section,
                parent_type=parent_type,
                order_index=int(order_index) if order_index else 0
            )

            session.add(folder)
            session.commit()

            flash(f'"{name}" papkasi muvaffaqiyatli yaratildi!', 'success')
            return redirect(url_for('folder.list'))

        except Exception as e:
            session.rollback()
            print(f"Folder create error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Xatolik: {str(e)}', 'error')
            return redirect(url_for('folder.create'))
        finally:
            session.close()

    # GET request - show form
    return render_template('folder/create.html')


@folder_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit folder"""
    session = get_sync_session()

    try:
        folder = session.query(Folder).get(id)

        if not folder:
            flash('Papka topilmadi!', 'error')
            return redirect(url_for('folder.list'))

        if request.method == 'POST':
            # Get form data
            name = request.form.get('name', '').strip()
            section = request.form.get('section', '').strip()
            parent_type = request.form.get('parent_type', '').strip()
            order_index = request.form.get('order_index', 0)

            # Validate
            if not name:
                flash('Papka nomi kiritilishi shart!', 'error')
                return redirect(url_for('folder.edit', id=id))

            # Update folder
            folder.name = name
            folder.section = section
            folder.parent_type = parent_type
            folder.order_index = int(order_index) if order_index else 0

            session.commit()

            flash(f'"{name}" papkasi yangilandi!', 'success')
            return redirect(url_for('folder.list'))

        # GET request - show form
        return render_template('folder/edit.html', folder=folder)

    except Exception as e:
        session.rollback()
        print(f"Folder edit error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('folder.list'))
    finally:
        session.close()


@folder_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete folder"""
    session = get_sync_session()

    try:
        folder = session.query(Folder).get(id)

        if not folder:
            flash('Papka topilmadi!', 'error')
            return redirect(url_for('folder.list'))

        # Check if folder has files
        if folder.files and len(folder.files) > 0:
            flash('Bu papkada fayllar bor! Avval fayllarni o\'chiring.', 'warning')
            return redirect(url_for('folder.list'))

        name = folder.name
        session.delete(folder)
        session.commit()

        flash(f'"{name}" papkasi o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Folder delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('folder.list'))


@folder_bp.route('/<int:id>/view')
@login_required
def view(id):
    """View folder details"""
    session = get_sync_session()

    try:
        folder = session.query(Folder).get(id)

        if not folder:
            flash('Papka topilmadi!', 'error')
            return redirect(url_for('folder.list'))

        # Get files
        files = folder.files if folder.files else []

        return render_template(
            'folder/view.html',
            folder=folder,
            files=files
        )

    except Exception as e:
        print(f"Folder view error: {e}")
        flash('Xatolik yuz berdi!', 'error')
        return redirect(url_for('folder.list'))
    finally:
        session.close()