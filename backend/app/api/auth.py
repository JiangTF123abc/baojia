from flask import Blueprint, request, jsonify

from ..services.auth_service import auth_service

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def ok(data):
    return jsonify({"code": 0, "data": data, "message": "ok"})


def err(code, message):
    return jsonify({"code": code, "data": None, "message": message}), code


@auth_bp.post('/login')
def login():
    body = request.get_json(silent=True) or {}
    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return err(400, "用户名和密码不能为空")

    try:
        result = auth_service.login(username, password)
    except ValueError as e:
        return err(401, str(e))

    return ok(result)


@auth_bp.post('/refresh')
def refresh():
    body = request.get_json(silent=True) or {}
    token = body.get("refresh_token", "")

    if not token:
        return err(400, "refresh_token 不能为空")

    try:
        result = auth_service.refresh_token(token)
    except ValueError as e:
        return err(401, str(e))

    return ok(result)


@auth_bp.post('/logout')
def logout():
    return ok({"message": "ok"})


@auth_bp.post('/register')
def register():
    body = request.get_json(silent=True) or {}
    username = body.get("username", "").strip()
    password = body.get("password", "")
    display_name = body.get("display_name", "").strip()

    if not username or not password:
        return err(400, "用户名和密码不能为空")
    if len(username) < 3:
        return err(400, "用户名至少需要3个字符")
    if len(password) < 6:
        return err(400, "密码至少需要6个字符")

    try:
        result = auth_service.register(username, password, display_name)
    except ValueError as e:
        return err(400, str(e))

    return ok(result)
