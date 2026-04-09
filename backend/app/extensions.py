from flask_sqlalchemy import SQLAlchemy
import jwt as pyjwt

# SQLAlchemy 实例（在工厂函数中绑定 app）
db = SQLAlchemy()

# PyJWT 直接使用模块级函数，无需实例化
# 提供统一的 JWT 工具函数


def encode_token(payload: dict, secret_key: str, algorithm: str = 'HS256') -> str:
    """签发 JWT 令牌"""
    return pyjwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(token: str, secret_key: str, algorithm: str = 'HS256') -> dict:
    """解码并验证 JWT 令牌"""
    return pyjwt.decode(token, secret_key, algorithms=[algorithm])
