"""
添加Cabinet表的新字段
"""
from app import create_app
from app.extensions import db

app = create_app()

print("="*60)
print("数据库迁移：添加Cabinet新字段")
print("="*60)

with app.app_context():
    try:
        # 添加新字段到cabinets表
        print("\n正在添加新字段到cabinets表...")
        
        sql_commands = [
            "ALTER TABLE cabinets ADD control_category NVARCHAR(50) NULL",
            "ALTER TABLE cabinets ADD cabinet_type NVARCHAR(100) NULL",
            "ALTER TABLE cabinets ADD control_structure NVARCHAR(100) NULL",
            "ALTER TABLE cabinets ADD quotation_mode NVARCHAR(50) NULL"
        ]
        
        for sql in sql_commands:
            try:
                db.session.execute(db.text(sql))
                print(f"  ✓ {sql}")
            except Exception as e:
                if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                    print(f"  - 字段已存在，跳过")
                else:
                    print(f"  ✗ 失败: {e}")
                    raise
        
        db.session.commit()
        print("\n✓ 所有字段添加成功！")
        
        # 验证字段是否存在
        print("\n验证新字段...")
        result = db.session.execute(db.text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'cabinets' 
            AND COLUMN_NAME IN ('control_category', 'cabinet_type', 'control_structure', 'quotation_mode')
        """))
        columns = [row[0] for row in result]
        print(f"  找到的字段: {columns}")
        
        if len(columns) == 4:
            print("\n✓ 数据库迁移完成！所有字段已添加")
        else:
            print(f"\n⚠ 警告：只找到 {len(columns)}/4 个字段")
            
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

print("\n" + "="*60)
print("请重启后端服务以应用更改")
print("="*60)
