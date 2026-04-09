"""
数据库迁移脚本 - 添加缺失的字段
"""
from app import create_app
from app.extensions import db

app = create_app()

print("="*60)
print("数据库迁移：添加新字段")
print("="*60)

migrations = [
    ("cabinets", "control_category", "ALTER TABLE cabinets ADD control_category NVARCHAR(50) NULL"),
    ("cabinets", "cabinet_type", "ALTER TABLE cabinets ADD cabinet_type NVARCHAR(100) NULL"),
    ("cabinets", "control_structure", "ALTER TABLE cabinets ADD control_structure NVARCHAR(100) NULL"),
    ("cabinets", "quotation_mode", "ALTER TABLE cabinets ADD quotation_mode NVARCHAR(50) NULL"),
    ("structure_components", "circuit_type", "ALTER TABLE structure_components ADD circuit_type NVARCHAR(100) NULL"),
    ("base_components", "component_category", "ALTER TABLE base_components ADD component_category NVARCHAR(100) NULL"),
    ("base_components", "is_auto_matched", "ALTER TABLE base_components ADD is_auto_matched BIT NOT NULL DEFAULT 0"),
    ("base_components", "is_hidden", "ALTER TABLE base_components ADD is_hidden BIT NOT NULL DEFAULT 0"),
]

with app.app_context():
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for table, column, sql in migrations:
        try:
            # 检查字段是否已存在
            check_sql = f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table}' AND COLUMN_NAME = '{column}'
            """
            result = db.session.execute(db.text(check_sql))
            exists = result.scalar() > 0
            
            if exists:
                print(f"  - {table}.{column} 已存在，跳过")
                skip_count += 1
            else:
                db.session.execute(db.text(sql))
                db.session.commit()
                print(f"  ✓ {table}.{column} 添加成功")
                success_count += 1
                
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ {table}.{column} 失败: {e}")
            fail_count += 1

print("\n" + "="*60)
print(f"迁移完成: {success_count} 个新增, {skip_count} 个跳过, {fail_count} 个失败")
print("="*60)

if fail_count == 0:
    print("\n✓ 所有字段已就绪，请重启后端服务")
else:
    print("\n⚠ 部分字段添加失败，请检查错误信息")
