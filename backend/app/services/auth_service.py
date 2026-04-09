from datetime import datetime, timedelta, timezone
from typing import Optional
from flask import current_app

from ..extensions import db, encode_token, decode_token
from ..models.user import User


class AuthService:

    def login(self, username: str, password: str) -> dict:
        """验证用户凭据，返回 access_token 和 refresh_token"""
        user = User.query.filter_by(username=username, is_active=True).first()
        if not user or not user.check_password(password):
            raise ValueError("用户名或密码错误")

        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.session.commit()

        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }

    def refresh_token(self, refresh_token_str: str) -> dict:
        """验证 refresh token，签发新 access_token"""
        secret = current_app.config["JWT_SECRET_KEY"]
        try:
            payload = decode_token(refresh_token_str, secret)
        except Exception:
            raise ValueError("无效或已过期的 refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("令牌类型错误")

        user = User.query.filter_by(id=payload["user_id"], is_active=True).first()
        if not user:
            raise ValueError("用户不存在或已被禁用")

        access_token = self._create_access_token(user)
        return {"access_token": access_token}

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 查询用户"""
        return User.query.get(user_id)

    def register(self, username: str, password: str, display_name: str = "") -> dict:
        """注册新用户"""
        existing = User.query.filter_by(username=username).first()
        if existing:
            raise ValueError("用户名已存在")

        user = User(username=username, display_name=display_name or username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _create_access_token(self, user: User) -> str:
        secret = current_app.config["JWT_SECRET_KEY"]
        hours = current_app.config.get("JWT_EXPIRATION_HOURS", 8)
        exp = datetime.now(tz=timezone.utc) + timedelta(hours=hours)
        payload = {
            "user_id": user.id,
            "role": user.role,
            "type": "access",
            "exp": exp,
        }
        return encode_token(payload, secret)

    def _create_refresh_token(self, user: User) -> str:
        secret = current_app.config["JWT_SECRET_KEY"]
        days = current_app.config.get("JWT_REFRESH_EXPIRATION_DAYS", 7)
        exp = datetime.now(tz=timezone.utc) + timedelta(days=days)
        payload = {
            "user_id": user.id,
            "role": user.role,
            "type": "refresh",
            "exp": exp,
        }
        return encode_token(payload, secret)


auth_service = AuthService()
