"""
直接测试tree API端点
"""
import traceback
from app import create_app

app = create_app()

print("="*60)
print("Tree API测试")
print("="*60)

with app.test_client() as client:
    # 1. 登录
    print("\n1. 登录...")
    resp = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'Admin@123456'
    })
    
    if resp.status_code != 200:
        print(f"   ✗ 登录失败: {resp.get_json()}")
        exit(1)
    
    token = resp.get_json()['data']['access_token']
    print("   ✓ 登录成功")
    
    # 2. 获取项目列表
    print("\n2. 获取项目列表...")
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/api/projects', headers=headers)
    
    print(f"   状态码: {resp.status_code}")
    if resp.status_code != 200:
        print(f"   ✗ 失败: {resp.get_json()}")
        exit(1)
    
    projects = resp.get_json()['data']
    print(f"   ✓ 成功，找到 {len(projects)} 个项目")
    
    if not projects:
        print("\n   没有项目，先创建一个...")
        resp = client.post('/api/projects', 
                          json={'name': '测试项目', 'customer': '测试客户'},
                          headers=headers)
        print(f"   创建状态码: {resp.status_code}")
        if resp.status_code == 201:
            print("   ✓ 项目创建成功")
            projects = [resp.get_json()['data']]
        else:
            print(f"   ✗ 创建失败: {resp.get_json()}")
            exit(1)
    
    # 3. 测试每个项目的tree接口
    for p in projects:
        project_id = p['id']
        print(f"\n3. 测试项目 {project_id} 的tree接口...")
        
        try:
            resp = client.get(f'/api/projects/{project_id}/tree', headers=headers)
            print(f"   状态码: {resp.status_code}")
            
            if resp.status_code == 200:
                tree = resp.get_json()['data']
                print(f"   ✓ 成功")
                print(f"   - 项目名: {tree.get('name')}")
                print(f"   - 柜体数量: {len(tree.get('cabinets', []))}")
            else:
                print(f"   ✗ 失败")
                print(f"   响应: {resp.get_json()}")
                print(f"   响应文本: {resp.get_data(as_text=True)}")
        except Exception as e:
            print(f"   ✗ 异常: {e}")
            traceback.print_exc()

print("\n" + "="*60)
print("测试完成")
print("="*60)
