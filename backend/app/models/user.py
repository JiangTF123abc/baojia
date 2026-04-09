from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
import re
from ..extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=True, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(200))
    role = db.Column(db.String(20), nullable=False, default='viewer')  # viewer | editor | admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)
    version = db.Column(db.Integer, default=1, nullable=False)

    # 关联
    projects = db.relationship('Project', back_populates='creator', lazy='dynamic')
    templates = db.relationship('Template', back_populates='creator', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', back_populates='user', lazy='dynamic')

    @validates('email')
    def validate_email(self, key, email):
        """验证邮箱格式"""
        if email is not None:
            # 邮箱格式正则表达式
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValueError('Invalid email format')
        return email

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'version': self.version,
        }

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
