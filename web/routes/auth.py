# web/routes/auth.py
"""
Authentication Routes - Login/Logout
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, current_user
from web.config import FlaskConfig
from web.models import User  # ← YANGI IMPORT!
import bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == FlaskConfig.ADMIN_USERNAME:
            try:
                stored_hash = FlaskConfig.ADMIN_PASSWORD
                password_bytes = password.encode('utf-8')
                stored_hash_bytes = stored_hash.encode('utf-8')

                if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                    user = User(username)
                    login_user(user, remember=True)
                    session.pop('_flashes', None)
                    session['just_logged_in'] = True

                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('dashboard.index'))

            except Exception as e:
                print(f"❌ Login error: {e}")
                error = "Tizimda xatolik yuz berdi!"
                return render_template('auth/login.html', error=error)

        error = "Noto'g'ri username yoki parol!"

    return render_template('auth/login.html', error=error)


@auth_bp.route('/logout')
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('auth.login'))