# web/config.py
"""
Flask Configuration
"""
import os
from utils.env_data import Config as BotConfig


class FlaskConfig:
    """Flask app configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'rjutb-admin-secret-key-2024-change-in-production')

    # ✅ Admin credentials - .ENV DAN OLINADI
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '$2b$12$kuqxaSZdkaymXCdW/Oi5Iu/SWHU4NH30RX1KPbl9nB9ZhSsDm0cwG')

    # Database
    SQLALCHEMY_DATABASE_URI = BotConfig.db.DB_URL.replace(
        'postgresql+asyncpg',
        'postgresql+psycopg2'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'

    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour