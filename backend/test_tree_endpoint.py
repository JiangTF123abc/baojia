"""
测试tree接口的详细调试
"""
import sys
import traceback
from app import create_app
from app.extensions import db
from app.models import Project, Cabinet, StructureComponent, BaseComponent

app = create_app()

print("="*60)
print("Tree接口调试")
print("="*60)

with app.app_context():
    # 查询所有项目
    print("\n1. 查询所有项目...")
    projects = Project.query.all()
    print(f"   找到 {len(projects)} 个项目")
    
    for p in projects:
        print(f"\n   项目 {p.id}: {p.name}")
        print(f"   - 创建时间: {p.created_at}")
        print(f"   - 客户: {p.customer}")
        
        # 查询该项目的柜体
        cabinets = p.cabinets.all()
        print(f"   - 柜体数量: {len(cabinets)}")
        
        for c in cabinets:
            print(f"     柜体 {c.id}: {c.name}")
            
            # 查询结构组件
            try:
                scs = c.structure_components.all()
                print(f"       - 结构组件数量: {len(scs)}")
                
                for sc in scs:
                    print(f"         结构组件 {sc.id}: {sc.name}")
                    
                    # 查询基础元器件
                    try:
                        bcs = sc.base_components.all()
                        print(f"           - 基础元器件数量: {len(bcs)}")
                    except Exception as e:
                        print(f"           ✗ 查询基础元器件失败: {e}")
                        traceback.print_exc()
            except Exception as e:
                print(f"       ✗ 查询结构组件失败: {e}")
                traceback.print_exc()
        
        # 测试to_dict方法
        print(f"\n   测试 to_dict(include_cabinets=True)...")
        try:
            tree_data = p.to_dict(include_cabinets=True)
            print(f"   ✓ to_dict 成功")
            print(f"   - 柜体数量: {len(tree_data.get('cabinets', []))}")
        except Exception as e:
            print(f"   ✗ to_dict 失败: {e}")
            traceback.print_exc()

print("\n" + "="*60)
print("调试完成")
print("="*60)
