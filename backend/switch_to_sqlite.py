"""
切换到SQLite数据库并初始化
"""
import os
from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

# 设置为测试环境（使用SQLite）
os.environ['FLASK_ENV'] = 'testing'

app = create_app()

print("="*60)
print("切换到SQLite数据库")
print("="*60)

with app.app_context():
    print("\n1. 删除旧数据库...")
    db.drop_all()
    print("  ✓ 完成")
    
    print("\n2. 创建新表结构...")
    db.create_all()
    print("  ✓ 完成")
    
    print("\n3. 创建管理员账号...")
    admin = User(
        username='admin',
        password_hash=generate_password_hash('Admin@123456'),
        role='admin',
        display_name='管理员'
    )
    db.session.add(admin)
    db.session.commit()
    print("  ✓ 管理员账号创建成功")
    print(f"     用户名: admin")
    print(f"     密码: Admin@123456")

print("\n" + "="*60)
print("✓ SQLite数据库初始化完成！")
print("="*60)
print("\n现在可以启动后端服务:")
print("  set FLASK_ENV=testing")
print("  python run.py")
