"""更新管理员密码"""
import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 将 backend 目录加入路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    # 查询管理员账号
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("❌ 管理员账号不存在")
    else:
        # 设置新密码
        new_password = '123456'
        admin.set_password(new_password)
        db.session.commit()
        
        print(f"✅ 密码已更新为：{new_password}")
        print(f"   密码哈希：{admin.password_hash[:50]}...")
        
        # 验证密码
        if admin.check_password(new_password):
            print(f"✅ 密码验证成功！")
        else:
            print(f"❌ 密码验证失败！")
