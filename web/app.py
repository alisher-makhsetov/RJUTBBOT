# web/app.py
"""
RJUTB Admin Panel - Custom Flask Application
Professional admin panel with beautiful UI
"""
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from web.config import FlaskConfig
from db import get_sync_session
from db.models import (
    Folder, File,
    Accident, AccidentYear, AccidentCategory,
    Conspect, ConspectCategory,
    Video, VideoCategory,
    Test, TestCategory,
    User as BotUser
)
from sqlalchemy import func

# ========== FLASK APP ==========
app = Flask(__name__)
app.config.from_object(FlaskConfig)

# ========== FLASK-LOGIN ==========
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


# ========== USER CLASS ==========
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    if user_id == FlaskConfig.ADMIN_USERNAME:
        return User(user_id)
    return None


# ========== ROUTES ==========

# --- HOME ---
@app.route('/')
def index():
    """Redirect to dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


# ========== IMPORT BLUEPRINTS ==========
from web.routes.auth import auth_bp
from web.routes.dashboard import dashboard_bp
from web.routes.folder import folder_bp
from web.routes.file import file_bp
from web.routes.accident import accident_bp
from web.routes.conspect import conspect_bp
from web.routes.video import video_bp
from web.routes.test import test_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(folder_bp)
app.register_blueprint(file_bp)
app.register_blueprint(accident_bp)
app.register_blueprint(conspect_bp)
app.register_blueprint(video_bp)
app.register_blueprint(test_bp)

# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


# ========== CONTEXT PROCESSORS ==========
@app.context_processor
def inject_now():
    """Inject current datetime to all templates"""
    return {'now': datetime.now()}


# ========== RUN ==========
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎯 RJUTB Admin Panel - Custom Flask")
    print("=" * 60)
    print(f"✅ Server: http://0.0.0.0:5000")
    print(f"✅ Admin Panel: http://0.0.0.0:5000/")
    print(f"📝 Username: {FlaskConfig.ADMIN_USERNAME}")
    print(f"🔒 Password: (hash in .env file)")
    print("=" * 60)
    print()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )