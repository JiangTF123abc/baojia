"""
快速诊断脚本 - 检查后端问题
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("="*60)
print("电气设备报价系统 - 后端诊断")
print("="*60)

# 1. 检查环境变量
print("\n1. 检查环境变量...")
db_server = os.environ.get('DB_SERVER')
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
print(f"   DB_SERVER: {db_server}")
print(f"   DB_NAME: {db_name}")
print(f"   DB_USER: {db_user}")

# 2. 尝试创建Flask应用
print("\n2. 尝试创建Flask应用...")
try:
    from app import create_app
    app = create_app()
    print("   ✓ Flask应用创建成功")
except Exception as e:
    print(f"   ✗ Flask应用创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 尝试连接数据库
print("\n3. 尝试连接数据库...")
try:
    with app.app_context():
        from app.extensions import db
        # 尝试执行简单查询
        result = db.session.execute(db.text("SELECT 1")).scalar()
        print(f"   ✓ 数据库连接成功 (结果: {result})")
except Exception as e:
    print(f"   ✗ 数据库连接失败: {e}")
    print("\n   可能的原因:")
    print("   - SQL Server服务未启动")
    print("   - 网络连接问题（无法访问 192.168.1.220:6811）")
    print("   - 数据库凭据错误")
    print("   - 防火墙阻止连接")
    print("\n   建议:")
    print("   1. 检查SQL Server是否运行")
    print("   2. 使用测试配置（SQLite）: set FLASK_ENV=testing")
    print("   3. 或者更新 .env 文件中的数据库配置")
    sys.exit(1)

# 4. 检查数据库表
print("\n4. 检查数据库表...")
try:
    with app.app_context():
        from app.extensions import db
        from sqlalchemy import inspect
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("   ✗ 数据库中没有表")
            print("\n   请运行: python init_db.py")
        else:
            print(f"   ✓ 找到 {len(tables)} 个表:")
            for table in sorted(tables):
                print(f"     - {table}")
except Exception as e:
    print(f"   ✗ 检查表失败: {e}")
    sys.exit(1)

# 5. 检查用户表
print("\n5. 检查用户数据...")
try:
    with app.app_context():
        from app.models.user import User
        user_count = User.query.count()
        print(f"   ✓ 用户表有 {user_count} 条记录")
        
        if user_count == 0:
            print("   ⚠ 没有用户，请运行: python init_db.py")
        else:
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"   ✓ 找到管理员账号: {admin.username}")
            else:
                print("   ⚠ 没有管理员账号")
except Exception as e:
    print(f"   ✗ 检查用户失败: {e}")

print("\n" + "="*60)
print("诊断完成")
print("="*60)
