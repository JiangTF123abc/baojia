"""
测试CORS和OPTIONS预检请求
"""
from app import create_app

app = create_app()

print("="*60)
print("CORS和OPTIONS预检测试")
print("="*60)

with app.test_client() as client:
    # 测试1: OPTIONS预检请求
    print("\n1. 测试OPTIONS预检请求...")
    resp = client.options('/api/projects',
                         headers={'Origin': 'http://localhost:5173'})
    print(f"   状态码: {resp.status_code}")
    print(f"   CORS头:")
    print(f"     - Allow-Origin: {resp.headers.get('Access-Control-Allow-Origin')}")
    print(f"     - Allow-Methods: {resp.headers.get('Access-Control-Allow-Methods')}")
    print(f"     - Allow-Headers: {resp.headers.get('Access-Control-Allow-Headers')}")
    
    if resp.status_code == 200:
        print("   ✓ OPTIONS预检请求正常")
    else:
        print("   ✗ OPTIONS预检请求失败")
    
    # 测试2: 登录获取token
    print("\n2. 测试登录...")
    resp = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'Admin@123456'
    })
    
    if resp.status_code != 200:
        print(f"   ✗ 登录失败: {resp.get_json()}")
        exit(1)
    
    token = resp.get_json()['data']['access_token']
    print("   ✓ 登录成功，获取到token")
    
    # 测试3: 带认证的GET请求
    print("\n3. 测试带认证的项目列表请求...")
    resp = client.get('/api/projects',
                     headers={'Authorization': f'Bearer {token}'})
    print(f"   状态码: {resp.status_code}")
    data = resp.get_json()
    print(f"   响应: {data}")
    
    if resp.status_code == 200:
        print("   ✓ 认证请求正常")
    else:
        print("   ✗ 认证请求失败")

print("\n" + "="*60)
print("✓ CORS配置测试完成")
print("="*60)
print("\n请重启后端服务以应用更改:")
print("  cd backend")
print("  python run.py")
