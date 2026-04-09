"""
测试API端点
"""
import sys
from app import create_app
from app.extensions import db

app = create_app()

print("测试 POST /api/projects...")
with app.test_client() as client:
    # 先登录获取token
    print("\n1. 登录...")
    login_resp = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'Admin@123456'
    })
    print(f"   状态码: {login_resp.status_code}")
    print(f"   响应: {login_resp.get_json()}")
    
    if login_resp.status_code != 200:
        print("   ✗ 登录失败")
        sys.exit(1)
    
    token = login_resp.get_json()['data']['access_token']
    print(f"   ✓ 登录成功，token: {token[:20]}...")
    
    # 测试创建项目
    print("\n2. 创建项目...")
    headers = {'Authorization': f'Bearer {token}'}
    create_resp = client.post('/api/projects', 
                              json={'name': '测试项目', 'customer': '测试客户'},
                              headers=headers)
    print(f"   状态码: {create_resp.status_code}")
    print(f"   响应: {create_resp.get_json()}")
    
    if create_resp.status_code == 201:
        print("   ✓ 创建成功")
    else:
        print("   ✗ 创建失败")
        sys.exit(1)
    
    # 测试获取项目列表
    print("\n3. 获取项目列表...")
    list_resp = client.get('/api/projects', headers=headers)
    print(f"   状态码: {list_resp.status_code}")
    data = list_resp.get_json()
    if list_resp.status_code == 200:
        projects = data.get('data', [])
        print(f"   ✓ 获取成功，共 {len(projects)} 个项目")
        for p in projects:
            print(f"     - {p['name']} (ID: {p['id']})")
    else:
        print(f"   ✗ 获取失败: {data}")

print("\n✓ 所有测试通过")
