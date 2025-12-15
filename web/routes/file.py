# web/routes/file.py
"""
File Routes - CRUD Operations with Pagination
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from db import get_sync_session
from db.models import File, Folder
from sqlalchemy import func
from sqlalchemy.orm import joinedload

file_bp = Blueprint('file', __name__, url_prefix='/file')


@file_bp.route('/')
@file_bp.route('/list')
@login_required
def list():
    """List all files with pagination"""
    session = get_sync_session()

    try:
        # Get parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        folder_filter = request.args.get('folder', '', type=int)
        section_filter = request.args.get('section', '')

        # Query WITH EAGER LOADING
        query = session.query(File).options(joinedload(File.folder))

        if search:
            query = query.filter(File.name.ilike(f'%{search}%'))

        if folder_filter:
            query = query.filter(File.folder_id == folder_filter)

        if section_filter:
            # Join with Folder to filter by section
            query = query.join(Folder).filter(Folder.section == section_filter)

        # Order by
        query = query.order_by(File.order_index.asc(), File.created_at.desc())

        # Total count
        total = query.count()

        # Pagination
        offset = (page - 1) * per_page
        files = query.limit(per_page).offset(offset).all()

        # Get all folders for filter dropdown
        folders = session.query(Folder).order_by(Folder.name).all()

        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

    except Exception as e:
        print(f"File list error: {e}")
        import traceback
        traceback.print_exc()
        files = []
        folders = []
        total = 0
        total_pages = 0
        has_prev = False
        has_next = False
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template(
        'file/list.html',
        files=files,
        folders=folders,
        search=search,
        folder_filter=folder_filter,
        section_filter=section_filter,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next
    )


@file_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new file"""
    session = get_sync_session()

    try:
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name', '').strip()
            file_id = request.form.get('file_id', '').strip()
            folder_id = request.form.get('folder_id', type=int)
            order_index = request.form.get('order_index', 0)

            # Validate
            if not name:
                flash('Fayl nomi kiritilishi shart!', 'error')
                return redirect(url_for('file.create'))

            if not file_id:
                flash('Telegram File ID kiritilishi shart!', 'error')
                return redirect(url_for('file.create'))

            if not folder_id:
                flash('Papka tanlanishi shart!', 'error')
                return redirect(url_for('file.create'))

            # Create file
            file = File(
                name=name,
                file_id=file_id,
                folder_id=folder_id,
                order_index=int(order_index) if order_index else 0
            )

            session.add(file)
            session.commit()

            flash(f'"{name}" fayli muvaffaqiyatli yaratildi!', 'success')
            return redirect(url_for('file.list'))

        # GET request - show form
        # Return all folders as JSON for JavaScript filtering
        folders = session.query(Folder).order_by(Folder.section, Folder.name).all()

        # Convert to dict for JSON
        folders_data = []
        for folder in folders:
            folders_data.append({
                'id': folder.id,
                'name': folder.name,
                'section': folder.section,
                'parent_type': folder.parent_type or ''
            })

        return render_template('file/create.html', folders=folders_data)

    except Exception as e:
        session.rollback()
        print(f"File create error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('file.create'))
    finally:
        session.close()


@file_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit file"""
    session = get_sync_session()

    try:
        file = session.query(File).options(joinedload(File.folder)).get(id)

        if not file:
            flash('Fayl topilmadi!', 'error')
            return redirect(url_for('file.list'))

        if request.method == 'POST':
            # Get form data
            name = request.form.get('name', '').strip()
            file_id_form = request.form.get('file_id', '').strip()
            folder_id = request.form.get('folder_id', type=int)
            order_index = request.form.get('order_index', 0)

            # Validate
            if not name:
                flash('Fayl nomi kiritilishi shart!', 'error')
                return redirect(url_for('file.edit', id=id))

            if not file_id_form:
                flash('Telegram File ID kiritilishi shart!', 'error')
                return redirect(url_for('file.edit', id=id))

            if not folder_id:
                flash('Papka tanlanishi shart!', 'error')
                return redirect(url_for('file.edit', id=id))

            # Update file
            file.name = name
            file.file_id = file_id_form
            file.folder_id = folder_id
            file.order_index = int(order_index) if order_index else 0

            session.commit()

            flash(f'"{name}" fayli yangilandi!', 'success')
            return redirect(url_for('file.list'))

        # GET request - show form
        folders = session.query(Folder).order_by(Folder.section, Folder.name).all()
        return render_template('file/edit.html', file=file, folders=folders)

    except Exception as e:
        session.rollback()
        print(f"File edit error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('file.list'))
    finally:
        session.close()


@file_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete file"""
    session = get_sync_session()

    try:
        file = session.query(File).get(id)

        if not file:
            flash('Fayl topilmadi!', 'error')
            return redirect(url_for('file.list'))

        name = file.name
        session.delete(file)
        session.commit()

        flash(f'"{name}" fayli o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"File delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('file.list'))


@file_bp.route('/<int:id>/view')
@login_required
def view(id):
    """View file details"""
    session = get_sync_session()

    try:
        file = session.query(File).options(joinedload(File.folder)).get(id)

        if not file:
            flash('Fayl topilmadi!', 'error')
            return redirect(url_for('file.list'))

        return render_template('file/view.html', file=file)

    except Exception as e:
        print(f"File view error: {e}")
        flash('Xatolik yuz berdi!', 'error')
        return redirect(url_for('file.list'))
    finally:
        session.close()