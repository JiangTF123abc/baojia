"""
确保用户表存在并创建管理员账号
"""
import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 将 backend 目录加入路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import User


def ensure_users_table():
    """确保用户表存在并创建管理员账号"""
    app = create_app()

    with app.app_context():
        print('=' * 60)
        print('检查用户表...')
        print('=' * 60)
        
        # 创建用户表（如果不存在）
        try:
            db.create_all()
            print('✓ 用户表已确保存在')
        except Exception as e:
            print(f'✗ 创建用户表失败: {e}')
            return False
        
        # 检查管理员账号
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123456')
        admin_display = os.environ.get('ADMIN_DISPLAY_NAME', '系统管理员')
        
        print(f'\n检查管理员账号: {admin_username}')
        
        existing_admin = User.query.filter_by(username=admin_username).first()
        
        if existing_admin:
            print(f'✓ 管理员账号已存在')
            print(f'  - 用户名: {existing_admin.username}')
            print(f'  - 显示名称: {existing_admin.display_name}')
            print(f'  - 角色: {existing_admin.role}')
            print(f'  - 状态: {"激活" if existing_admin.is_active else "禁用"}')
            print(f'  - 创建时间: {existing_admin.created_at}')
            
            # 询问是否重置密码
            print(f'\n如需重置密码，请运行: python update_password.py')
        else:
            print(f'✗ 管理员账号不存在，正在创建...')
            
            try:
                admin = User(
                    username=admin_username,
                    display_name=admin_display,
                    role='admin',
                    is_active=True,
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                
                print(f'✓ 管理员账号创建成功')
                print(f'  - 用户名: {admin_username}')
                print(f'  - 密码: {admin_password}')
                print(f'  - 显示名称: {admin_display}')
                print(f'  - 角色: admin')
                print(f'\n⚠️  请妥善保管管理员密码！')
            except Exception as e:
                print(f'✗ 创建管理员账号失败: {e}')
                db.session.rollback()
                return False
        
        # 显示所有用户
        print('\n' + '=' * 60)
        print('当前系统用户列表:')
        print('=' * 60)
        
        users = User.query.all()
        if users:
            print(f'{"ID":<5} {"用户名":<15} {"显示名称":<15} {"角色":<10} {"状态":<8}')
            print('-' * 60)
            for user in users:
                status = "激活" if user.is_active else "禁用"
                print(f'{user.id:<5} {user.username:<15} {user.display_name or "":<15} {user.role:<10} {status:<8}')
        else:
            print('暂无用户')
        
        print('\n' + '=' * 60)
        print('用户表检查完成')
        print('=' * 60)
        
        return True


if __name__ == '__main__':
    success = ensure_users_table()
    sys.exit(0 if success else 1)
