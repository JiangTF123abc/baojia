"""
直接使用pyodbc执行数据库迁移
"""
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量获取数据库连接信息
db_uri = os.getenv('DATABASE_URI', '')
print("数据库URI:", db_uri[:50] + "...")

# 解析连接字符串
# 格式: mssql+pyodbc://user:pass@host:port/dbname?driver=...
if 'mssql+pyodbc://' in db_uri:
    parts = db_uri.replace('mssql+pyodbc://', '').split('@')
    user_pass = parts[0].split(':')
    username = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ''
    
    host_db = parts[1].split('/')
    host_port = host_db[0].split(':')
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else '1433'
    
    db_driver = host_db[1].split('?')
    database = db_driver[0]
    driver = 'ODBC Driver 17 for SQL Server'
    
    conn_str = f'DRIVER={{{driver}}};SERVER={host},{port};DATABASE={database};UID={username};PWD={password}'
    
    print("\n连接到数据库...")
    print(f"服务器: {host}:{port}")
    print(f"数据库: {database}")
    
    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()
        print("✓ 连接成功\n")
        
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
        
        for table, column, sql in migrations:
            try:
                # 检查字段是否存在
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{table}' AND COLUMN_NAME = '{column}'
                """)
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    print(f"  - {table}.{column} 已存在")
                else:
                    cursor.execute(sql)
                    conn.commit()
                    print(f"  ✓ {table}.{column} 添加成功")
            except Exception as e:
                print(f"  ✗ {table}.{column} 失败: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        print("\n✓ 迁移完成！请重启后端服务")
        
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ 无法解析数据库URI")
