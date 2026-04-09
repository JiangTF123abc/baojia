import os


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', '8'))
    JWT_REFRESH_EXPIRATION_DAYS = int(os.environ.get('JWT_REFRESH_EXPIRATION_DAYS', '7'))

    # SQL Server 连接配置（通过环境变量）
    DB_SERVER = os.environ.get('DB_SERVER', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'quotation_db')
    DB_USER = os.environ.get('DB_USER', 'sa')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_DRIVER = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')

    # 构建连接字符串（pyodbc 格式）
    from urllib.parse import quote_plus
    connection_string = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }

    # 文件上传
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    REPORT_FOLDER = os.environ.get('REPORT_FOLDER', 'reports')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    # 测试时使用 SQLite 内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_EXPIRATION_HOURS = 1


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}


def get_config():
    env = os.environ.get('FLASK_ENV', 'default')
    return config_map.get(env, DevelopmentConfig)
