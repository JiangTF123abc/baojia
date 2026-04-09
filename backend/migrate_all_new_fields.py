"""
添加所有新字段到数据库表
"""
from app import create_app
from app.extensions import db

app = create_app()

print("="*60)
print("数据库迁移：添加所有新字段")
print("="*60)

with app.app_context():
    try:
        # 1. cabinets表新字段
        print("\n1. 添加cabinets表新字段...")
        cabinet_fields = [
            "ALTER TABLE cabinets ADD control_category NVARCHAR(50) NULL",
            "ALTER TABLE cabinets ADD cabinet_type NVARCHAR(100) NULL",
            "ALTER TABLE cabinets ADD control_structure NVARCHAR(100) NULL",
            "ALTER TABLE cabinets ADD quotation_mode NVARCHAR(50) NULL"
        ]
        
        for sql in cabinet_fields:
            try:
                db.session.execute(db.text(sql))
                field_name = sql.split('ADD ')[1].split(' ')[0]
                print(f"  ✓ 添加字段: {field_name}")
            except Exception as e:
                if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                    field_name = sql.split('ADD ')[1].split(' ')[0]
                    print(f"  - 字段已存在: {field_name}")
                else:
                    raise
        
        # 2. structure_components表新字段
        print("\n2. 添加structure_components表新字段...")
        sc_fields = [
            "ALTER TABLE structure_components ADD circuit_type NVARCHAR(100) NULL"
        ]
        
        for sql in sc_fields:
            try:
                db.session.execute(db.text(sql))
                field_name = sql.split('ADD ')[1].split(' ')[0]
                print(f"  ✓ 添加字段: {field_name}")
            except Exception as e:
                if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                    field_name = sql.split('ADD ')[1].split(' ')[0]
                    print(f"  - 字段已存在: {field_name}")
                else:
                    raise
        
        # 3. base_components表新字段
        print("\n3. 添加base_components表新字段...")
        bc_fields = [
            "ALTER TABLE base_components ADD component_category NVARCHAR(100) NULL",
            "ALTER TABLE base_components ADD is_auto_matched BIT NOT NULL DEFAULT 0",
            "ALTER TABLE base_components ADD is_hidden BIT NOT NULL DEFAULT 0"
        ]
        
        for sql in bc_fields:
            try:
                db.session.execute(db.text(sql))
                field_name = sql.split('ADD ')[1].split(' ')[0]
                print(f"  ✓ 添加字段: {field_name}")
            except Exception as e:
                if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                    field_name = sql.split('ADD ')[1].split(' ')[0]
                    print(f"  - 字段已存在: {field_name}")
                else:
                    raise
        
        db.session.commit()
        print("\n✓ 所有字段添加成功！")
        
        # 验证所有字段
        print("\n验证新字段...")
        
        tables_to_check = {
            'cabinets': ['control_category', 'cabinet_type', 'control_structure', 'quotation_mode'],
            'structure_components': ['circuit_type'],
            'base_components': ['component_category', 'is_auto_matched', 'is_hidden']
        }
        
        all_ok = True
        for table_name, expected_columns in tables_to_check.items():
            result = db.session.execute(db.text(f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}'
                AND COLUMN_NAME IN ({','.join(f"'{c}'" for c in expected_columns)})
            """))
            columns = [row[0] for row in result]
            print(f"  {table_name}: {len(columns)}/{len(expected_columns)} 字段")
            
            if len(columns) != len(expected_columns):
                missing = set(expected_columns) - set(columns)
                print(f"    ⚠ 缺少: {missing}")
                all_ok = False
        
        if all_ok:
            print("\n✓ 数据库迁移完成！所有字段已添加")
        else:
            print("\n⚠ 警告：部分字段未成功添加")
            
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

print("\n" + "="*60)
print("迁移完成，请重启后端服务")
print("="*60)
