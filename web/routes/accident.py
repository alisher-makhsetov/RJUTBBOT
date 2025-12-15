# web/routes/accident.py
"""
Accident Routes - Years, Categories, Accidents CRUD
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from db import get_sync_session
from db.models import AccidentYear, AccidentCategory, Accident
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime

accident_bp = Blueprint('accident', __name__, url_prefix='/accident')


# ==================== YEARS ====================

@accident_bp.route('/years')
@login_required
def years():
    """List all accident years"""
    session = get_sync_session()

    try:
        years_list = session.query(AccidentYear).order_by(AccidentYear.name.desc()).all()

        # Count accidents for each year
        for year in years_list:
            year.accidents_count = session.query(func.count(Accident.id)).filter(
                Accident.year_id == year.id
            ).scalar() or 0

    except Exception as e:
        print(f"Years list error: {e}")
        years_list = []
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template('accident/years.html', years=years_list)


@accident_bp.route('/years/create', methods=['GET', 'POST'])
@login_required
def years_create():
    """Create new year"""
    if request.method == 'POST':
        session = get_sync_session()

        try:
            year = request.form.get('year', '').strip()

            if not year:
                flash('Yil kiritilishi shart!', 'error')
                return redirect(url_for('accident.years_create'))

            # Check if year already exists
            existing = session.query(AccidentYear).filter(AccidentYear.name == year).first()
            if existing:
                flash(f'{year}-yil allaqachon mavjud!', 'warning')
                return redirect(url_for('accident.years'))

            new_year = AccidentYear(name=year)
            session.add(new_year)
            session.commit()

            flash(f'{year}-yil muvaffaqiyatli qo\'shildi!', 'success')
            return redirect(url_for('accident.years'))

        except Exception as e:
            session.rollback()
            print(f"Year create error: {e}")
            flash(f'Xatolik: {str(e)}', 'error')
            return redirect(url_for('accident.years_create'))
        finally:
            session.close()

    return render_template('accident/years_create.html')


@accident_bp.route('/years/<int:id>/delete', methods=['POST'])
@login_required
def years_delete(id):
    """Delete year"""
    session = get_sync_session()

    try:
        year = session.query(AccidentYear).get(id)

        if not year:
            flash('Yil topilmadi!', 'error')
            return redirect(url_for('accident.years'))

        # Check if year has accidents
        accidents_count = session.query(func.count(Accident.id)).filter(
            Accident.year_id == id
        ).scalar()

        if accidents_count > 0:
            flash(f'Bu yilda {accidents_count} ta hodisa bor! Avval hodisalarni o\'chiring.', 'warning')
            return redirect(url_for('accident.years'))

        year_name = year.name
        session.delete(year)
        session.commit()

        flash(f'{year_name}-yil o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Year delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('accident.years'))


# ==================== CATEGORIES ====================

@accident_bp.route('/categories')
@login_required
def categories():
    """List all accident categories"""
    session = get_sync_session()

    try:
        categories_list = session.query(AccidentCategory).order_by(
            AccidentCategory.name.asc()
        ).all()

        # Count accidents for each category
        for category in categories_list:
            category.accidents_count = session.query(func.count(Accident.id)).filter(
                Accident.category_id == category.id
            ).scalar() or 0

    except Exception as e:
        print(f"Categories list error: {e}")
        categories_list = []
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template('accident/categories.html', categories=categories_list)


@accident_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def categories_create():
    """Create new category"""
    if request.method == 'POST':
        session = get_sync_session()

        try:
            name = request.form.get('name', '').strip()

            if not name:
                flash('Kategoriya nomi kiritilishi shart!', 'error')
                return redirect(url_for('accident.categories_create'))

            category = AccidentCategory(name=name)

            session.add(category)
            session.commit()

            flash(f'"{name}" kategoriyasi qo\'shildi!', 'success')
            return redirect(url_for('accident.categories'))

        except Exception as e:
            session.rollback()
            print(f"Category create error: {e}")
            flash(f'Xatolik: {str(e)}', 'error')
            return redirect(url_for('accident.categories_create'))
        finally:
            session.close()

    return render_template('accident/categories_create.html')


@accident_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def categories_edit(id):
    """Edit category"""
    session = get_sync_session()

    try:
        category = session.query(AccidentCategory).get(id)

        if not category:
            flash('Kategoriya topilmadi!', 'error')
            return redirect(url_for('accident.categories'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()

            if not name:
                flash('Kategoriya nomi kiritilishi shart!', 'error')
                return redirect(url_for('accident.categories_edit', id=id))

            category.name = name
            session.commit()

            flash(f'"{name}" kategoriyasi yangilandi!', 'success')
            return redirect(url_for('accident.categories'))

        return render_template('accident/categories_edit.html', category=category)

    except Exception as e:
        session.rollback()
        print(f"Category edit error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('accident.categories'))
    finally:
        session.close()


@accident_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def categories_delete(id):
    """Delete category"""
    session = get_sync_session()

    try:
        category = session.query(AccidentCategory).get(id)

        if not category:
            flash('Kategoriya topilmadi!', 'error')
            return redirect(url_for('accident.categories'))

        # Check if category has accidents
        accidents_count = session.query(func.count(Accident.id)).filter(
            Accident.category_id == id
        ).scalar()

        if accidents_count > 0:
            flash(f'Bu kategoriyada {accidents_count} ta hodisa bor!', 'warning')
            return redirect(url_for('accident.categories'))

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

    return redirect(url_for('accident.categories'))


# ==================== ACCIDENTS ====================

@accident_bp.route('/')
@accident_bp.route('/list')
@login_required
def list():
    """List all accidents with pagination"""
    session = get_sync_session()

    try:
        # Get parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        year_filter = request.args.get('year', '', type=int)
        category_filter = request.args.get('category', '', type=int)
        search = request.args.get('search', '').strip()

        # Query with eager loading
        query = session.query(Accident).options(
            joinedload(Accident.year),
            joinedload(Accident.category)
        )

        if search:
            query = query.filter(
                (Accident.title.ilike(f'%{search}%')) |
                (Accident.description.ilike(f'%{search}%'))
            )

        if year_filter:
            query = query.filter(Accident.year_id == year_filter)

        if category_filter:
            query = query.filter(Accident.category_id == category_filter)

        # Order by
        query = query.order_by(Accident.created_at.desc())

        # Total count
        total = query.count()

        # Pagination
        offset = (page - 1) * per_page
        accidents = query.limit(per_page).offset(offset).all()

        # Get years and categories for filters
        years_list = session.query(AccidentYear).order_by(AccidentYear.name.desc()).all()
        categories_list = session.query(AccidentCategory).order_by(AccidentCategory.name).all()

        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

    except Exception as e:
        print(f"Accidents list error: {e}")
        import traceback
        traceback.print_exc()
        accidents = []
        years_list = []
        categories_list = []
        total = 0
        total_pages = 0
        has_prev = False
        has_next = False
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template(
        'accident/list.html',
        accidents=accidents,
        years=years_list,
        categories=categories_list,
        search=search,
        year_filter=year_filter,
        category_filter=category_filter,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next
    )


@accident_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new accident"""
    session = get_sync_session()

    try:
        if request.method == 'POST':
            year_id = request.form.get('year_id', type=int)
            category_id = request.form.get('category_id', type=int)
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            file_pdf = request.form.get('file_pdf', '').strip()

            # Validate
            if not year_id:
                flash('Yil tanlanishi shart!', 'error')
                return redirect(url_for('accident.create'))

            if not category_id:
                flash('Kategoriya tanlanishi shart!', 'error')
                return redirect(url_for('accident.create'))

            if not title:
                flash('Sarlavha kiritilishi shart!', 'error')
                return redirect(url_for('accident.create'))

            if not file_pdf:
                flash('PDF fayl ID kiritilishi shart!', 'error')
                return redirect(url_for('accident.create'))

            # Create accident
            accident = Accident(
                year_id=year_id,
                category_id=category_id,
                title=title,
                description=description if description else None,
                file_pdf=file_pdf
            )

            session.add(accident)
            session.commit()

            flash('Hodisa muvaffaqiyatli qo\'shildi!', 'success')
            return redirect(url_for('accident.list'))

        # GET request
        years_list = session.query(AccidentYear).order_by(AccidentYear.name.desc()).all()
        categories_list = session.query(AccidentCategory).order_by(AccidentCategory.name).all()

        return render_template(
            'accident/create.html',
            years=years_list,
            categories=categories_list
        )

    except Exception as e:
        session.rollback()
        print(f"Accident create error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('accident.create'))
    finally:
        session.close()


@accident_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit accident"""
    session = get_sync_session()

    try:
        accident = session.query(Accident).options(
            joinedload(Accident.year),
            joinedload(Accident.category)
        ).get(id)

        if not accident:
            flash('Hodisa topilmadi!', 'error')
            return redirect(url_for('accident.list'))

        if request.method == 'POST':
            year_id = request.form.get('year_id', type=int)
            category_id = request.form.get('category_id', type=int)
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            file_pdf = request.form.get('file_pdf', '').strip()

            # Validate
            if not year_id:
                flash('Yil tanlanishi shart!', 'error')
                return redirect(url_for('accident.edit', id=id))

            if not category_id:
                flash('Kategoriya tanlanishi shart!', 'error')
                return redirect(url_for('accident.edit', id=id))

            if not title:
                flash('Sarlavha kiritilishi shart!', 'error')
                return redirect(url_for('accident.edit', id=id))

            if not file_pdf:
                flash('PDF fayl ID kiritilishi shart!', 'error')
                return redirect(url_for('accident.edit', id=id))

            # Update
            accident.year_id = year_id
            accident.category_id = category_id
            accident.title = title
            accident.description = description if description else None
            accident.file_pdf = file_pdf

            session.commit()

            flash('Hodisa yangilandi!', 'success')
            return redirect(url_for('accident.list'))

        # GET request
        years_list = session.query(AccidentYear).order_by(AccidentYear.name.desc()).all()
        categories_list = session.query(AccidentCategory).order_by(AccidentCategory.name).all()

        return render_template(
            'accident/edit.html',
            accident=accident,
            years=years_list,
            categories=categories_list
        )

    except Exception as e:
        session.rollback()
        print(f"Accident edit error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('accident.list'))
    finally:
        session.close()


@accident_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete accident"""
    session = get_sync_session()

    try:
        accident = session.query(Accident).get(id)

        if not accident:
            flash('Hodisa topilmadi!', 'error')
            return redirect(url_for('accident.list'))

        session.delete(accident)
        session.commit()

        flash('Hodisa o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Accident delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('accident.list'))


@accident_bp.route('/<int:id>/view')
@login_required
def view(id):
    """View accident details"""
    session = get_sync_session()

    try:
        accident = session.query(Accident).options(
            joinedload(Accident.year),
            joinedload(Accident.category)
        ).get(id)

        if not accident:
            flash('Hodisa topilmadi!', 'error')
            return redirect(url_for('accident.list'))

        return render_template('accident/view.html', accident=accident)

    except Exception as e:
        print(f"Accident view error: {e}")
        flash('Xatolik yuz berdi!', 'error')
        return redirect(url_for('accident.list'))
    finally:
        session.close()