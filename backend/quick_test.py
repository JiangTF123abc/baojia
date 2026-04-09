"""
快速测试 - 检查后端API是否正常
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("快速API测试")
print("="*60)

# 测试1: 导入检查
print("\n1. 检查导入...")
try:
    from app import create_app
    from app.extensions import db
    from app.models import User, Project
    print("   ✓ 所有模块导入成功")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试2: 创建应用
print("\n2. 创建Flask应用...")
try:
    app = create_app()
    print("   ✓ Flask应用创建成功")
    print(f"   - 数据库URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
except Exception as e:
    print(f"   ✗ 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试3: 数据库查询
print("\n3. 测试数据库查询...")
try:
    with app.app_context():
        user_count = User.query.count()
        project_count = Project.query.count()
        print(f"   ✓ 数据库查询成功")
        print(f"   - 用户数: {user_count}")
        print(f"   - 项目数: {project_count}")
except Exception as e:
    print(f"   ✗ 查询失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试4: 测试登录API
print("\n4. 测试登录API...")
try:
    with app.test_client() as client:
        resp = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'Admin@123456'
        })
        print(f"   状态码: {resp.status_code}")
        data = resp.get_json()
        print(f"   响应: {data}")
        
        if resp.status_code == 200:
            print("   ✓ 登录API正常")
            token = data['data']['access_token']
            
            # 测试5: 测试创建项目API
            print("\n5. 测试创建项目API...")
            headers = {'Authorization': f'Bearer {token}'}
            resp2 = client.post('/api/projects',
                               json={'name': '测试项目ABC', 'customer': '测试客户'},
                               headers=headers)
            print(f"   状态码: {resp2.status_code}")
            data2 = resp2.get_json()
            print(f"   响应: {data2}")
            
            if resp2.status_code == 201:
                print("   ✓ 创建项目API正常")
            else:
                print("   ✗ 创建项目API失败")
                if 'message' in data2:
                    print(f"   错误信息: {data2['message']}")
        else:
            print("   ✗ 登录API失败")
except Exception as e:
    print(f"   ✗ API测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✓ 所有测试通过！后端API正常工作")
print("="*60)
print("\n如果前端仍然无法访问，请检查:")
print("1. 后端服务是否在运行 (python run.py)")
print("2. 浏览器控制台是否有CORS错误")
print("3. 前端是否正确配置了API地址")
