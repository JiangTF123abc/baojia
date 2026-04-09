"""测试登录功能"""
import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 将 backend 目录加入路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    # 查询管理员账号
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("❌ 管理员账号不存在")
    else:
        print(f"✅ 找到管理员账号：{admin.username}")
        print(f"   显示名称：{admin.display_name}")
        print(f"   角色：{admin.role}")
        print(f"   是否激活：{admin.is_active}")
        print(f"   密码哈希：{admin.password_hash[:50]}...")
        
        # 测试密码
        test_passwords = ['Admin@123456', 'admin', 'Admin123456', 's123456']
        print("\n测试密码：")
        for pwd in test_passwords:
            result = admin.check_password(pwd)
            print(f"   {pwd}: {'✅ 正确' if result else '❌ 错误'}")
