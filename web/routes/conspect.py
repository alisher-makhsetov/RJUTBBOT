# web/routes/conspect.py
"""
Conspect Routes - Categories and Conspects CRUD
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from db import get_sync_session
from db.models import ConspectCategory, Conspect
from sqlalchemy import func
from sqlalchemy.orm import joinedload

conspect_bp = Blueprint('conspect', __name__, url_prefix='/conspect')


# ==================== CATEGORIES ====================

@conspect_bp.route('/categories')
@login_required
def categories():
    """List all conspect categories"""
    session = get_sync_session()

    try:
        categories_list = session.query(ConspectCategory).order_by(
            ConspectCategory.section.asc(),
            ConspectCategory.name.asc()
        ).all()

        for category in categories_list:
            category.conspects_count = session.query(func.count(Conspect.id)).filter(
                Conspect.category_id == category.id
            ).scalar() or 0

    except Exception as e:
        print(f"Categories list error: {e}")
        categories_list = []
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template('conspect/categories.html', categories=categories_list)


@conspect_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def categories_create():
    """Create new category"""
    if request.method == 'POST':
        session = get_sync_session()

        try:
            name = request.form.get('name', '').strip()
            section = request.form.get('section', '').strip()

            if not name:
                flash('Kategoriya nomi kiritilishi shart!', 'error')
                return redirect(url_for('conspect.categories_create'))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('conspect.categories_create'))

            category = ConspectCategory(
                name=name,
                section=section
            )

            session.add(category)
            session.commit()

            flash(f'"{name}" kategoriyasi qo\'shildi!', 'success')
            return redirect(url_for('conspect.categories'))

        except Exception as e:
            session.rollback()
            print(f"Category create error: {e}")
            flash(f'Xatolik: {str(e)}', 'error')
            return redirect(url_for('conspect.categories_create'))
        finally:
            session.close()

    return render_template('conspect/categories_create.html')


@conspect_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def categories_edit(id):
    """Edit category"""
    session = get_sync_session()

    try:
        category = session.query(ConspectCategory).get(id)

        if not category:
            flash('Kategoriya topilmadi!', 'error')
            return redirect(url_for('conspect.categories'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            section = request.form.get('section', '').strip()

            if not name:
                flash('Kategoriya nomi kiritilishi shart!', 'error')
                return redirect(url_for('conspect.categories_edit', id=id))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('conspect.categories_edit', id=id))

            category.name = name
            category.section = section
            session.commit()

            flash(f'"{name}" kategoriyasi yangilandi!', 'success')
            return redirect(url_for('conspect.categories'))

        return render_template('conspect/categories_edit.html', category=category)

    except Exception as e:
        session.rollback()
        print(f"Category edit error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('conspect.categories'))
    finally:
        session.close()


@conspect_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def categories_delete(id):
    """Delete category"""
    session = get_sync_session()

    try:
        category = session.query(ConspectCategory).get(id)

        if not category:
            flash('Kategoriya topilmadi!', 'error')
            return redirect(url_for('conspect.categories'))

        conspects_count = session.query(func.count(Conspect.id)).filter(
            Conspect.category_id == id
        ).scalar()

        if conspects_count > 0:
            flash(f'Bu kategoriyada {conspects_count} ta konspekt bor!', 'warning')
            return redirect(url_for('conspect.categories'))

        name = category.name
        session.delete(category)
        session.commit()

        flash(f'"{name}" kategoriyasi o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Category delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('conspect.categories'))


# ==================== CONSPECTS ====================

@conspect_bp.route('/')
@conspect_bp.route('/list')
@login_required
def list():
    """List all conspects with pagination"""
    session = get_sync_session()

    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        section_filter = request.args.get('section', '').strip()
        category_filter = request.args.get('category', '', type=int)
        search = request.args.get('search', '').strip()

        query = session.query(Conspect).options(
            joinedload(Conspect.category)
        )

        if search:
            query = query.filter(
                (Conspect.name.ilike(f'%{search}%')) |
                (Conspect.description.ilike(f'%{search}%'))
            )

        if section_filter:
            query = query.join(ConspectCategory).filter(
                ConspectCategory.section == section_filter
            )

        if category_filter:
            query = query.filter(Conspect.category_id == category_filter)

        query = query.order_by(Conspect.created_at.desc())

        total = query.count()

        offset = (page - 1) * per_page
        conspects = query.limit(per_page).offset(offset).all()

        categories_list = session.query(ConspectCategory).order_by(
            ConspectCategory.section.asc(),
            ConspectCategory.name.asc()
        ).all()

        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

    except Exception as e:
        print(f"Conspects list error: {e}")
        import traceback
        traceback.print_exc()
        conspects = []
        categories_list = []
        total = 0
        total_pages = 0
        has_prev = False
        has_next = False
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template(
        'conspect/list.html',
        conspects=conspects,
        categories=categories_list,
        search=search,
        section_filter=section_filter,
        category_filter=category_filter,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next
    )


@conspect_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new conspect"""
    session = get_sync_session()

    try:
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            file = request.form.get('file', '').strip()
            section = request.form.get('section', '').strip()
            category_id = request.form.get('category_id')

            if not name or not file or not category_id:
                flash('Barcha majburiy maydonlarni to\'ldiring!', 'error')
                return redirect(url_for('conspect.create'))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'limni tanlang!', 'error')
                return redirect(url_for('conspect.create'))

            category = session.query(ConspectCategory).filter_by(id=category_id).first()
            if not category:
                flash('Kategoriya topilmadi!', 'error')
                return redirect(url_for('conspect.create'))

            if category.section != section:
                flash('Kategoriya tanlangan bo\'limga mos kelmaydi!', 'error')
                return redirect(url_for('conspect.create'))

            conspect = Conspect(
                category_id=category_id,
                name=name,
                description=description,
                file=file
            )

            session.add(conspect)
            session.commit()

            flash('Konspekt muvaffaqiyatli qo\'shildi!', 'success')
            return redirect(url_for('conspect.list'))

        categories_list = session.query(ConspectCategory).order_by(
            ConspectCategory.section.asc(),
            ConspectCategory.name.asc()
        ).all()

        return render_template(
            'conspect/create.html',
            categories=categories_list
        )

    except Exception as e:
        session.rollback()
        print(f"Conspect create error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('conspect.create'))
    finally:
        session.close()


@conspect_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit conspect"""
    session = get_sync_session()

    try:
        conspect = session.query(Conspect).options(
            joinedload(Conspect.category)
        ).get(id)

        if not conspect:
            flash('Konspekt topilmadi!', 'error')
            return redirect(url_for('conspect.list'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            file = request.form.get('file', '').strip()
            section = request.form.get('section', '').strip()
            category_id = request.form.get('category_id', type=int)

            if not name:
                flash('Nom kiritilishi shart!', 'error')
                return redirect(url_for('conspect.edit', id=id))

            if not description:
                flash('Tavsif kiritilishi shart!', 'error')
                return redirect(url_for('conspect.edit', id=id))

            if not file:
                flash('Fayl ID kiritilishi shart!', 'error')
                return redirect(url_for('conspect.edit', id=id))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'limni tanlang!', 'error')
                return redirect(url_for('conspect.edit', id=id))

            if not category_id:
                flash('Kategoriyani tanlang!', 'error')
                return redirect(url_for('conspect.edit', id=id))

            category = session.query(ConspectCategory).filter_by(id=category_id).first()
            if not category:
                flash('Kategoriya topilmadi!', 'error')
                return redirect(url_for('conspect.edit', id=id))

            if category.section != section:
                flash('Kategoriya tanlangan bo\'limga mos kelmaydi!', 'error')
                return redirect(url_for('conspect.edit', id=id))

            conspect.category_id = category_id
            conspect.name = name
            conspect.description = description
            conspect.file = file

            session.commit()

            flash('Konspekt yangilandi!', 'success')
            return redirect(url_for('conspect.list'))

        categories_list = session.query(ConspectCategory).order_by(
            ConspectCategory.section.asc(),
            ConspectCategory.name.asc()
        ).all()

        current_section = conspect.category.section if conspect.category else ''

        return render_template(
            'conspect/edit.html',
            conspect=conspect,
            categories=categories_list,
            current_section=current_section
        )

    except Exception as e:
        session.rollback()
        print(f"Conspect edit error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('conspect.list'))
    finally:
        session.close()


@conspect_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete conspect"""
    session = get_sync_session()

    try:
        conspect = session.query(Conspect).get(id)

        if not conspect:
            flash('Konspekt topilmadi!', 'error')
            return redirect(url_for('conspect.list'))

        session.delete(conspect)
        session.commit()

        flash('Konspekt o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Conspect delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('conspect.list'))


@conspect_bp.route('/<int:id>/view')
@login_required
def view(id):
    """View conspect details"""
    session = get_sync_session()

    try:
        conspect = session.query(Conspect).options(
            joinedload(Conspect.category)
        ).get(id)

        if not conspect:
            flash('Konspekt topilmadi!', 'error')
            return redirect(url_for('conspect.list'))

        return render_template('conspect/view.html', conspect=conspect)

    except Exception as e:
        print(f"Conspect view error: {e}")
        flash('Xatolik yuz berdi!', 'error')
        return redirect(url_for('conspect.list'))
    finally:
        session.close()