from datetime import datetime, timedelta
import random
from ..extensions import db


class VerificationCode(db.Model):
    """验证码模型类
    
    用于管理密码重置验证码的生成、存储和验证。
    验证码为6位数字，默认有效期5分钟。
    """
    __tablename__ = 'verification_codes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # 'password_reset'
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    is_used = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关联
    user = db.relationship('User', backref=db.backref('verification_codes', lazy='dynamic'))

    @staticmethod
    def generate_code() -> str:
        """生成6位数字验证码
        
        Returns:
            str: 6位数字字符串，范围 000000-999999
        """
        return str(random.randint(0, 999999)).zfill(6)

    def is_valid(self) -> bool:
        """检查验证码是否有效
        
        验证码有效的条件：
        1. 未被使用 (is_used == False)
        2. 未过期 (expires_at > 当前时间)
        
        Returns:
            bool: 验证码有效返回 True，否则返回 False
        """
        if self.is_used:
            return False
        
        if datetime.utcnow() > self.expires_at:
            return False
        
        return True

    def mark_as_used(self) -> None:
        """标记验证码为已使用
        
        将 is_used 字段设置为 True，防止验证码被重复使用。
        注意：此方法不会自动提交数据库事务，需要调用方手动提交。
        """
        self.is_used = True

    def __repr__(self):
        return f'<VerificationCode {self.code} for {self.email} ({self.purpose})>'
