# web/routes/video.py
"""
Video Routes - Categories and Videos CRUD
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from db import get_sync_session
from db.models import VideoCategory, Video
from sqlalchemy import func
from sqlalchemy.orm import joinedload

video_bp = Blueprint('video', __name__, url_prefix='/video')


# ==================== CATEGORIES ====================

@video_bp.route('/categories')
@login_required
def categories():
    """List all video categories"""
    session = get_sync_session()

    try:
        categories_list = session.query(VideoCategory).order_by(
            VideoCategory.section.asc(),
            VideoCategory.name.asc()
        ).all()

        # Count videos for each category
        for category in categories_list:
            category.videos_count = session.query(func.count(Video.id)).filter(
                Video.category_id == category.id
            ).scalar() or 0

    except Exception as e:
        print(f"Categories list error: {e}")
        categories_list = []
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template('video/categories.html', categories=categories_list)


@video_bp.route('/categories/create', methods=['GET', 'POST'])
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
                return redirect(url_for('video.categories_create'))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('video.categories_create'))

            category = VideoCategory(
                name=name,
                section=section
            )

            session.add(category)
            session.commit()

            flash(f'"{name}" kategoriyasi qo\'shildi!', 'success')
            return redirect(url_for('video.categories'))

        except Exception as e:
            session.rollback()
            print(f"Category create error: {e}")
            flash(f'Xatolik: {str(e)}', 'error')
            return redirect(url_for('video.categories_create'))
        finally:
            session.close()

    return render_template('video/categories_create.html')


@video_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def categories_edit(id):
    """Edit category"""
    session = get_sync_session()

    try:
        category = session.query(VideoCategory).get(id)

        if not category:
            flash('Kategoriya topilmadi!', 'error')
            return redirect(url_for('video.categories'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            section = request.form.get('section', '').strip()

            if not name:
                flash('Kategoriya nomi kiritilishi shart!', 'error')
                return redirect(url_for('video.categories_edit', id=id))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('video.categories_edit', id=id))

            category.name = name
            category.section = section
            session.commit()

            flash(f'"{name}" kategoriyasi yangilandi!', 'success')
            return redirect(url_for('video.categories'))

        return render_template('video/categories_edit.html', category=category)

    except Exception as e:
        session.rollback()
        print(f"Category edit error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('video.categories'))
    finally:
        session.close()


@video_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def categories_delete(id):
    """Delete category"""
    session = get_sync_session()

    try:
        category = session.query(VideoCategory).get(id)

        if not category:
            flash('Kategoriya topilmadi!', 'error')
            return redirect(url_for('video.categories'))

        # Check if category has videos
        videos_count = session.query(func.count(Video.id)).filter(
            Video.category_id == id
        ).scalar()

        if videos_count > 0:
            flash(f'Bu kategoriyada {videos_count} ta video bor!', 'warning')
            return redirect(url_for('video.categories'))

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

    return redirect(url_for('video.categories'))


# ==================== VIDEOS ====================

@video_bp.route('/')
@video_bp.route('/list')
@login_required
def list():
    """List all videos with pagination"""
    session = get_sync_session()

    try:
        # Get parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        section_filter = request.args.get('section', '').strip()
        category_filter = request.args.get('category', '', type=int)
        search = request.args.get('search', '').strip()

        # Query with eager loading
        query = session.query(Video).options(
            joinedload(Video.category)
        )

        if search:
            query = query.filter(
                (Video.name.ilike(f'%{search}%')) |
                (Video.description.ilike(f'%{search}%'))
            )

        if section_filter:
            query = query.join(VideoCategory).filter(
                VideoCategory.section == section_filter
            )

        if category_filter:
            query = query.filter(Video.category_id == category_filter)

        # Order by
        query = query.order_by(Video.created_at.desc())

        # Total count
        total = query.count()

        # Pagination
        offset = (page - 1) * per_page
        videos = query.limit(per_page).offset(offset).all()

        # Get categories for filters
        categories_list = session.query(VideoCategory).order_by(
            VideoCategory.section.asc(),
            VideoCategory.name.asc()
        ).all()

        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

    except Exception as e:
        print(f"Videos list error: {e}")
        import traceback
        traceback.print_exc()
        videos = []
        categories_list = []
        total = 0
        total_pages = 0
        has_prev = False
        has_next = False
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template(
        'video/list.html',
        videos=videos,
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


@video_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new video"""
    session = get_sync_session()

    try:
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            file = request.form.get('file', '').strip()
            section = request.form.get('section', '').strip()  # ✅ QO'SHAMIZ
            category_id = request.form.get('category_id')

            # Validation
            if not name or not file or not category_id:
                flash('Barcha majburiy maydonlarni to\'ldiring!', 'error')
                return redirect(url_for('video.create'))

            # ✅ SECTION VALIDATION
            if not section or section not in ['MM', 'SX']:
                flash('Bo\'limni tanlang!', 'error')
                return redirect(url_for('video.create'))

            # ✅ KATEGORIYA SECTION BILAN TO'G'RI KELISHI KERAK
            category = session.query(VideoCategory).filter_by(id=category_id).first()
            if not category:
                flash('Kategoriya topilmadi!', 'error')
                return redirect(url_for('video.create'))

            if category.section != section:
                flash('Kategoriya tanlangan bo\'limga mos kelmaydi!', 'error')
                return redirect(url_for('video.create'))

            # Create video
            video = Video(
                category_id=category_id,
                name=name,
                description=description,
                file=file
            )

            session.add(video)
            session.commit()

            flash('Video muvaffaqiyatli qo\'shildi!', 'success')
            return redirect(url_for('video.list'))

        # GET request
        categories_list = session.query(VideoCategory).order_by(
            VideoCategory.section.asc(),
            VideoCategory.name.asc()
        ).all()

        return render_template(
            'video/create.html',
            categories=categories_list
        )

    except Exception as e:
        session.rollback()
        print(f"Video create error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('video.create'))
    finally:
        session.close()


@video_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit video"""
    session = get_sync_session()

    try:
        video = session.query(Video).options(
            joinedload(Video.category)
        ).get(id)

        if not video:
            flash('Video topilmadi!', 'error')
            return redirect(url_for('video.list'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            file = request.form.get('file', '').strip()
            section = request.form.get('section', '').strip()  # ✅ QO'SHILDI
            category_id = request.form.get('category_id', type=int)

            # Validate
            if not name:
                flash('Nom kiritilishi shart!', 'error')
                return redirect(url_for('video.edit', id=id))

            if not description:
                flash('Tavsif kiritilishi shart!', 'error')
                return redirect(url_for('video.edit', id=id))

            if not file:
                flash('Fayl ID kiritilishi shart!', 'error')
                return redirect(url_for('video.edit', id=id))

            # ✅ YANGI: Section validation
            if not section or section not in ['MM', 'SX']:
                flash('Bo\'limni tanlang!', 'error')
                return redirect(url_for('video.edit', id=id))

            # ✅ YANGI: Category validation
            if not category_id:
                flash('Kategoriyani tanlang!', 'error')
                return redirect(url_for('video.edit', id=id))

            category = session.query(VideoCategory).filter_by(id=category_id).first()
            if not category:
                flash('Kategoriya topilmadi!', 'error')
                return redirect(url_for('video.edit', id=id))

            # ✅ YANGI: Section va category mos kelishi kerak
            if category.section != section:
                flash('Kategoriya tanlangan bo\'limga mos kelmaydi!', 'error')
                return redirect(url_for('video.edit', id=id))

            # Update
            video.category_id = category_id
            video.name = name
            video.description = description
            video.file = file

            session.commit()

            flash('Video yangilandi!', 'success')
            return redirect(url_for('video.list'))

        # GET request
        categories_list = session.query(VideoCategory).order_by(
            VideoCategory.section.asc(),
            VideoCategory.name.asc()
        ).all()

        # ✅ YANGI: Current section
        current_section = video.category.section if video.category else ''

        return render_template(
            'video/edit.html',
            video=video,
            categories=categories_list,
            current_section=current_section  # ✅ QO'SHILDI
        )

    except Exception as e:
        session.rollback()
        print(f"Video edit error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('video.list'))
    finally:
        session.close()


@video_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete video"""
    session = get_sync_session()

    try:
        video = session.query(Video).get(id)

        if not video:
            flash('Video topilmadi!', 'error')
            return redirect(url_for('video.list'))

        session.delete(video)
        session.commit()

        flash('Video o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Video delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('video.list'))


@video_bp.route('/<int:id>/view')
@login_required
def view(id):
    """View video details"""
    session = get_sync_session()

    try:
        video = session.query(Video).options(
            joinedload(Video.category)
        ).get(id)

        if not video:
            flash('Video topilmadi!', 'error')
            return redirect(url_for('video.list'))

        return render_template('video/view.html', video=video)

    except Exception as e:
        print(f"Video view error: {e}")
        flash('Xatolik yuz berdi!', 'error')
        return redirect(url_for('video.list'))
    finally:
        session.close()