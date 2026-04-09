from functools import wraps

from flask import request, g, current_app, jsonify

from ..extensions import decode_token


def require_auth(f):
    """从 Authorization: Bearer <token> 提取并验证 JWT，将 user_id 和 role 注入 g.current_user"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"code": 401, "data": None, "message": "缺少认证令牌"}), 401

        token = auth_header[len("Bearer "):]
        secret = current_app.config["JWT_SECRET_KEY"]
        try:
            payload = decode_token(token, secret)
        except Exception:
            return jsonify({"code": 401, "data": None, "message": "无效或已过期的令牌"}), 401

        if payload.get("type") != "access":
            return jsonify({"code": 401, "data": None, "message": "令牌类型错误"}), 401

        g.current_user = {
            "user_id": payload["user_id"],
            "role": payload["role"],
        }
        return f(*args, **kwargs)

    return decorated


def require_role(*roles):
    """检查 g.current_user['role'] 是否在允许的角色列表中"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = getattr(g, "current_user", None)
            if not current_user:
                return jsonify({"code": 401, "data": None, "message": "未认证"}), 401
            if current_user.get("role") not in roles:
                return jsonify({"code": 403, "data": None, "message": "权限不足"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
