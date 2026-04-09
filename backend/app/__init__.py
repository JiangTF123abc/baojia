import os
from flask import Flask, request
from .extensions import db
from .api.auth import auth_bp
from .api.projects import projects_bp
from .api.cabinets import cabinets_bp
from .api.components import components_bp
from .api.materials import materials_bp
from .api.reports import reports_bp
from .api.templates import templates_bp
from .api.cabinet_configs import bp as cabinet_configs_bp


def create_app(config=None) -> Flask:
    """Flask 应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    if config is None:
        from config import get_config
        app.config.from_object(get_config())
    elif isinstance(config, dict):
        app.config.update(config)
    else:
        app.config.from_object(config)

    # 添加CORS支持（不使用flask-cors）
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # 处理所有OPTIONS预检请求
    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response

    # 确保上传和报表目录存在
    for folder_key in ('UPLOAD_FOLDER', 'REPORT_FOLDER'):
        folder = app.config.get(folder_key)
        if folder:
            os.makedirs(folder, exist_ok=True)

    # 初始化扩展
    _init_extensions(app)

    # 注册蓝图
    _register_blueprints(app)

    return app


def _init_extensions(app: Flask):
    """初始化 Flask 扩展"""
    db.init_app(app)


def _register_blueprints(app: Flask):
    """注册所有 API 蓝图"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(cabinets_bp)
    app.register_blueprint(components_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(templates_bp)
    app.register_blueprint(cabinet_configs_bp)
