"""
用户表邮箱字段迁移脚本
任务：1.1 为 User 表添加 email 字段
执行方式：python backend/migrations/run_migration_001.py
"""

import pyodbc
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_db_connection():
    """获取数据库连接"""
    server = os.getenv('DB_SERVER', 'localhost')
    database = os.getenv('DB_NAME', 'baojia')
    username = os.getenv('DB_USER', 'sa')
    password = os.getenv('DB_PASSWORD', '')
    
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'TrustServerCertificate=yes;'
    )
    
    return pyodbc.connect(conn_str)

def execute_migration():
    """执行迁移脚本"""
    print('=' * 60)
    print('开始执行用户表邮箱字段迁移...')
    print('=' * 60)
    print()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 添加 email 字段
        print('步骤 1: 添加 email 字段...')
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                          WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email')
            BEGIN
                ALTER TABLE users ADD email NVARCHAR(255) NULL;
                SELECT 'added' as result;
            END
            ELSE
            BEGIN
                SELECT 'exists' as result;
            END
        """)
        result = cursor.fetchone()
        if result and result[0] == 'added':
            print('✓ 已添加 email 字段')
        else:
            print('✗ email 字段已存在，跳过添加')
        conn.commit()
        
        # 2. 为现有用户生成默认邮箱
        print('\n步骤 2: 为现有用户设置默认邮箱...')
        cursor.execute("""
            UPDATE users 
            SET email = username + '@example.com'
            WHERE email IS NULL
        """)
        rows_affected = cursor.rowcount
        conn.commit()
        print(f'✓ 已为 {rows_affected} 个用户设置默认邮箱')
        
        # 3. 将 email 字段设置为 NOT NULL
        print('\n步骤 3: 将 email 字段设置为 NOT NULL...')
        cursor.execute("""
            SELECT IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email'
        """)
        is_nullable = cursor.fetchone()[0]
        
        if is_nullable == 'YES':
            cursor.execute("ALTER TABLE users ALTER COLUMN email NVARCHAR(255) NOT NULL")
            conn.commit()
            print('✓ 已将 email 字段设置为 NOT NULL')
        else:
            print('✗ email 字段已经是 NOT NULL')
        
        # 4. 添加唯一约束
        print('\n步骤 4: 添加 email 唯一约束...')
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes 
                          WHERE name = 'UQ_users_email' AND object_id = OBJECT_ID('users'))
            BEGIN
                ALTER TABLE users ADD CONSTRAINT UQ_users_email UNIQUE (email);
                SELECT 'added' as result;
            END
            ELSE
            BEGIN
                SELECT 'exists' as result;
            END
        """)
        result = cursor.fetchone()
        if result and result[0] == 'added':
            print('✓ 已创建 email 唯一约束')
        else:
            print('✗ email 唯一约束已存在')
        conn.commit()
        
        # 5. 创建索引
        print('\n步骤 5: 创建 email 索引...')
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes 
                          WHERE name = 'idx_users_email' AND object_id = OBJECT_ID('users'))
            BEGIN
                CREATE INDEX idx_users_email ON users(email);
                SELECT 'added' as result;
            END
            ELSE
            BEGIN
                SELECT 'exists' as result;
            END
        """)
        result = cursor.fetchone()
        if result and result[0] == 'added':
            print('✓ 已创建 email 索引')
        else:
            print('✗ email 索引已存在')
        conn.commit()
        
        # 验证迁移结果
        print('\n' + '=' * 60)
        print('迁移完成！验证结果：')
        print('=' * 60)
        
        # 显示字段信息
        print('\nemail 字段信息：')
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email'
        """)
        row = cursor.fetchone()
        if row:
            print(f'  列名: {row[0]}')
            print(f'  数据类型: {row[1]}')
            print(f'  最大长度: {row[2]}')
            print(f'  可为空: {row[3]}')
        
        # 显示用户数据示例
        print('\n用户邮箱数据示例：')
        cursor.execute("""
            SELECT TOP 5 id, username, email, created_at
            FROM users
            ORDER BY id
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f'  ID: {row[0]}, 用户名: {row[1]}, 邮箱: {row[2]}')
        
        cursor.close()
        conn.close()
        
        print('\n✓ 迁移成功完成！')
        return True
        
    except Exception as e:
        print(f'\n✗ 迁移失败: {str(e)}')
        return False

if __name__ == '__main__':
    success = execute_migration()
    exit(0 if success else 1)
