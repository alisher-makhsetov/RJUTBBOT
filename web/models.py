# web/models.py

"""
User Models for Flask-Login
"""
from flask_login import UserMixin


class User(UserMixin):
    """Admin user model"""
    def __init__(self, username):
        self.id = username
        self.username = username

    def __repr__(self):
        return f'<User {self.username}>'