# web/routes/test.py
"""
Test Routes - Categories, Tests (Questions) and Answers CRUD
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from db import get_sync_session
from db.models import TestCategory, Test, TestAnswer, test_category_association
from sqlalchemy import func
from sqlalchemy.orm import joinedload

test_bp = Blueprint('test', __name__, url_prefix='/test')


# ==================== CATEGORIES ====================

@test_bp.route('/categories')
@login_required
def categories():
    """List all test categories"""
    session = get_sync_session()

    try:
        categories_list = session.query(TestCategory).order_by(
            TestCategory.section.asc(),
            TestCategory.name.asc()
        ).all()

        # Count tests for each category
        for category in categories_list:
            category.tests_count = session.query(func.count(test_category_association.c.test_id)).filter(
                test_category_association.c.category_id == category.id
            ).scalar() or 0

    except Exception as e:
        print(f"Categories list error: {e}")
        categories_list = []
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template('test/categories.html', categories=categories_list)


@test_bp.route('/categories/create', methods=['GET', 'POST'])
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
                return redirect(url_for('test.categories_create'))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('test.categories_create'))

            category = TestCategory(
                name=name,
                section=section
            )

            session.add(category)
            session.commit()

            flash(f'"{name}" kategoriyasi qo\'shildi!', 'success')
            return redirect(url_for('test.categories'))

        except Exception as e:
            session.rollback()
            print(f"Category create error: {e}")
            flash(f'Xatolik: {str(e)}', 'error')
            return redirect(url_for('test.categories_create'))
        finally:
            session.close()

    return render_template('test/categories_create.html')


@test_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def categories_edit(id):
    """Edit category"""
    session = get_sync_session()

    try:
        category = session.query(TestCategory).get(id)

        if not category:
            flash('Kategoriya topilmadi!', 'error')
            return redirect(url_for('test.categories'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            section = request.form.get('section', '').strip()

            if not name:
                flash('Kategoriya nomi kiritilishi shart!', 'error')
                return redirect(url_for('test.categories_edit', id=id))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('test.categories_edit', id=id))

            category.name = name
            category.section = section
            session.commit()

            flash(f'"{name}" kategoriyasi yangilandi!', 'success')
            return redirect(url_for('test.categories'))

        return render_template('test/categories_edit.html', category=category)

    except Exception as e:
        session.rollback()
        print(f"Category edit error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('test.categories'))
    finally:
        session.close()


@test_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def categories_delete(id):
    """Delete category"""
    session = get_sync_session()

    try:
        category = session.query(TestCategory).get(id)

        if not category:
            flash('Kategoriya topilmadi!', 'error')
            return redirect(url_for('test.categories'))

        # Check if category has tests
        tests_count = session.query(func.count(test_category_association.c.test_id)).filter(
            test_category_association.c.category_id == id
        ).scalar()

        if tests_count > 0:
            flash(f'Bu kategoriyada {tests_count} ta test bor!', 'warning')
            return redirect(url_for('test.categories'))

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

    return redirect(url_for('test.categories'))


# ==================== TESTS ====================

@test_bp.route('/')
@test_bp.route('/list')
@login_required
def list():
    """List all tests with pagination"""
    session = get_sync_session()

    try:
        # Get parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        section_filter = request.args.get('section', '').strip()
        category_filter = request.args.get('category', '', type=int)
        search = request.args.get('search', '').strip()

        # Query with eager loading
        query = session.query(Test).options(
            joinedload(Test.categories),
            joinedload(Test.answers)
        )

        if search:
            query = query.filter(Test.text.ilike(f'%{search}%'))

        if section_filter or category_filter:
            query = query.join(Test.categories)

            if section_filter:
                query = query.filter(TestCategory.section == section_filter)

            if category_filter:
                query = query.filter(TestCategory.id == category_filter)

        # Order by
        query = query.order_by(Test.created_at.desc())

        # Total count
        total = query.count()

        # Pagination
        offset = (page - 1) * per_page
        tests = query.limit(per_page).offset(offset).all()

        # Get categories for filters
        categories_list = session.query(TestCategory).order_by(
            TestCategory.section.asc(),
            TestCategory.name.asc()
        ).all()

        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

    except Exception as e:
        print(f"Tests list error: {e}")
        import traceback
        traceback.print_exc()
        tests = []
        categories_list = []
        total = 0
        total_pages = 0
        has_prev = False
        has_next = False
        flash('Xatolik yuz berdi!', 'error')
    finally:
        session.close()

    return render_template(
        'test/list.html',
        tests=tests,
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


@test_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new test with answers"""
    session = get_sync_session()

    try:
        if request.method == 'POST':
            text = request.form.get('text', '').strip()
            image = request.form.get('image', '').strip()
            section = request.form.get('section', '').strip()
            category_ids = request.form.getlist('categories')

            # Answers (4 ta majburiy)
            answer_1 = request.form.get('answer_1', '').strip()
            answer_2 = request.form.get('answer_2', '').strip()
            answer_3 = request.form.get('answer_3', '').strip()
            answer_4 = request.form.get('answer_4', '').strip()

            # Correct answers (checkboxlar)
            correct_answers = request.form.getlist('correct')

            # Validate
            if not text:
                flash('Savol matni kiritilishi shart!', 'error')
                return redirect(url_for('test.create'))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('test.create'))

            if not category_ids:
                flash('Kamida bitta kategoriya tanlanishi shart!', 'error')
                return redirect(url_for('test.create'))

            if not all([answer_1, answer_2, answer_3, answer_4]):
                flash('Barcha javoblar (1, 2, 3, 4) kiritilishi shart!', 'error')
                return redirect(url_for('test.create'))

            if not correct_answers:
                flash('Kamida bitta to\'g\'ri javob belgilanishi shart!', 'error')
                return redirect(url_for('test.create'))

            # Create test
            test = Test(
                text=text,
                image=image if image else None
            )

            session.add(test)
            session.flush()  # Get test ID

            # Add categories
            categories = session.query(TestCategory).filter(
                TestCategory.id.in_(category_ids)
            ).all()
            test.categories = categories

            # Add answers
            answers_data = [
                {'text': answer_1, 'is_correct': '1' in correct_answers},
                {'text': answer_2, 'is_correct': '2' in correct_answers},
                {'text': answer_3, 'is_correct': '3' in correct_answers},
                {'text': answer_4, 'is_correct': '4' in correct_answers},
            ]

            for answer_data in answers_data:
                answer = TestAnswer(
                    text=answer_data['text'],
                    is_correct=answer_data['is_correct'],
                    test_id=test.id
                )
                session.add(answer)

            session.commit()

            flash('Test muvaffaqiyatli qo\'shildi!', 'success')
            return redirect(url_for('test.list'))

        # GET request
        categories_list = session.query(TestCategory).order_by(
            TestCategory.section.asc(),
            TestCategory.name.asc()
        ).all()

        return render_template(
            'test/create.html',
            categories=categories_list
        )

    except Exception as e:
        session.rollback()
        print(f"Test create error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('test.create'))
    finally:
        session.close()


# EDIT funksiyasi ham xuddi shunday yangilanadi (370-qator atrofida)
@test_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit test with answers"""
    session = get_sync_session()

    try:
        test = session.query(Test).options(
            joinedload(Test.categories),
            joinedload(Test.answers)
        ).get(id)

        if not test:
            flash('Test topilmadi!', 'error')
            return redirect(url_for('test.list'))

        if request.method == 'POST':
            text = request.form.get('text', '').strip()
            image = request.form.get('image', '').strip()
            section = request.form.get('section', '').strip()
            category_ids = request.form.getlist('categories')

            # Answers
            answer_1 = request.form.get('answer_1', '').strip()
            answer_2 = request.form.get('answer_2', '').strip()
            answer_3 = request.form.get('answer_3', '').strip()
            answer_4 = request.form.get('answer_4', '').strip()

            # Correct answers
            correct_answers = request.form.getlist('correct')

            # Validate
            if not text:
                flash('Savol matni kiritilishi shart!', 'error')
                return redirect(url_for('test.edit', id=id))

            if not section or section not in ['MM', 'SX']:
                flash('Bo\'lim tanlanishi shart!', 'error')
                return redirect(url_for('test.edit', id=id))

            if not category_ids:
                flash('Kamida bitta kategoriya tanlanishi shart!', 'error')
                return redirect(url_for('test.edit', id=id))

            if not all([answer_1, answer_2, answer_3, answer_4]):
                flash('Barcha javoblar kiritilishi shart!', 'error')
                return redirect(url_for('test.edit', id=id))

            if not correct_answers:
                flash('Kamida bitta to\'g\'ri javob belgilanishi shart!', 'error')
                return redirect(url_for('test.edit', id=id))

            # Update test
            test.text = text
            test.image = image if image else None

            # Update categories
            categories = session.query(TestCategory).filter(
                TestCategory.id.in_(category_ids)
            ).all()
            test.categories = categories

            # Update answers
            answers_data = [
                {'text': answer_1, 'is_correct': '1' in correct_answers},
                {'text': answer_2, 'is_correct': '2' in correct_answers},
                {'text': answer_3, 'is_correct': '3' in correct_answers},
                {'text': answer_4, 'is_correct': '4' in correct_answers},
            ]

            # Sort answers
            test.answers.sort(key=lambda x: x.id)

            for i, answer_data in enumerate(answers_data):
                if i < len(test.answers):
                    test.answers[i].text = answer_data['text']
                    test.answers[i].is_correct = answer_data['is_correct']

            session.commit()

            flash('Test yangilandi!', 'success')
            return redirect(url_for('test.list'))

        # GET request
        categories_list = session.query(TestCategory).order_by(
            TestCategory.section.asc(),
            TestCategory.name.asc()
        ).all()

        # Get current answers (sorted)
        answers = sorted(test.answers, key=lambda x: x.id)

        # Find current section
        current_section = test.categories[0].section if test.categories else ''

        # Find correct answers
        correct_indices = []
        for i, answer in enumerate(answers):
            if answer.is_correct:
                correct_indices.append(str(i + 1))

        return render_template(
            'test/edit.html',
            test=test,
            categories=categories_list,
            answers=answers,
            current_section=current_section,
            correct_indices=correct_indices
        )

    except Exception as e:
        session.rollback()
        print(f"Test edit error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Xatolik: {str(e)}', 'error')
        return redirect(url_for('test.list'))
    finally:
        session.close()


@test_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete test"""
    session = get_sync_session()

    try:
        test = session.query(Test).get(id)

        if not test:
            flash('Test topilmadi!', 'error')
            return redirect(url_for('test.list'))

        session.delete(test)
        session.commit()

        flash('Test o\'chirildi!', 'success')

    except Exception as e:
        session.rollback()
        print(f"Test delete error: {e}")
        flash(f'Xatolik: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('test.list'))


@test_bp.route('/<int:id>/view')
@login_required
def view(id):
    """View test details"""
    session = get_sync_session()

    try:
        test = session.query(Test).options(
            joinedload(Test.categories),
            joinedload(Test.answers)
        ).get(id)

        if not test:
            flash('Test topilmadi!', 'error')
            return redirect(url_for('test.list'))

        # Sort answers
        answers = sorted(test.answers, key=lambda x: x.id)

        return render_template('test/view.html', test=test, answers=answers)

    except Exception as e:
        print(f"Test view error: {e}")
        flash('Xatolik yuz berdi!', 'error')
        return redirect(url_for('test.list'))
    finally:
        session.close()