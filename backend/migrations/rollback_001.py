"""
回滚迁移 001：删除用户邮箱字段
警告：此操作将删除所有邮箱数据，请谨慎执行！
执行方式：python backend/migrations/rollback_001.py
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

def confirm_rollback():
    """确认回滚操作"""
    print('=' * 60)
    print('警告：即将回滚用户表邮箱字段迁移')
    print('此操作将删除所有邮箱数据！')
    print('=' * 60)
    print()
    print('请确认：')
    print('1. 已备份数据库')
    print('2. 确实需要回滚此迁移')
    print()
    
    response = input('是否继续？(yes/no): ').strip().lower()
    return response == 'yes'

def execute_rollback():
    """执行回滚操作"""
    if not confirm_rollback():
        print('\n回滚操作已取消')
        return False
    
    print('\n开始执行回滚...\n')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 删除索引
        print('步骤 1: 删除 email 索引...')
        cursor.execute("""
            IF EXISTS (SELECT * FROM sys.indexes 
                      WHERE name = 'idx_users_email' AND object_id = OBJECT_ID('users'))
            BEGIN
                DROP INDEX idx_users_email ON users;
                SELECT 'deleted' as result;
            END
            ELSE
            BEGIN
                SELECT 'not_exists' as result;
            END
        """)
        result = cursor.fetchone()
        if result and result[0] == 'deleted':
            print('✓ 已删除 email 索引')
        else:
            print('✗ email 索引不存在')
        conn.commit()
        
        # 2. 删除唯一约束
        print('\n步骤 2: 删除 email 唯一约束...')
        cursor.execute("""
            IF EXISTS (SELECT * FROM sys.objects 
                      WHERE name = 'UQ_users_email' AND type = 'UQ')
            BEGIN
                ALTER TABLE users DROP CONSTRAINT UQ_users_email;
                SELECT 'deleted' as result;
            END
            ELSE
            BEGIN
                SELECT 'not_exists' as result;
            END
        """)
        result = cursor.fetchone()
        if result and result[0] == 'deleted':
            print('✓ 已删除 email 唯一约束')
        else:
            print('✗ email 唯一约束不存在')
        conn.commit()
        
        # 3. 删除 email 字段
        print('\n步骤 3: 删除 email 字段...')
        cursor.execute("""
            IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email')
            BEGIN
                ALTER TABLE users DROP COLUMN email;
                SELECT 'deleted' as result;
            END
            ELSE
            BEGIN
                SELECT 'not_exists' as result;
            END
        """)
        result = cursor.fetchone()
        if result and result[0] == 'deleted':
            print('✓ 已删除 email 字段')
        else:
            print('✗ email 字段不存在')
        conn.commit()
        
        # 验证回滚结果
        print('\n' + '=' * 60)
        print('回滚完成！验证结果：')
        print('=' * 60)
        
        # 检查字段是否已删除
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email'
        """)
        count = cursor.fetchone()[0]
        
        if count == 0:
            print('\n✓ email 字段已成功删除')
        else:
            print('\n✗ email 字段仍然存在')
        
        # 显示当前表结构
        print('\n当前用户表结构：')
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'users'
            ORDER BY ORDINAL_POSITION
        """)
        rows = cursor.fetchall()
        for row in rows:
            nullable = '是' if row[3] == 'YES' else '否'
            max_len = row[2] if row[2] else 'N/A'
            print(f'  {row[0]}: {row[1]}({max_len}), 可为空: {nullable}')
        
        cursor.close()
        conn.close()
        
        print('\n✓ 回滚成功完成！')
        return True
        
    except Exception as e:
        print(f'\n✗ 回滚失败: {str(e)}')
        return False

if __name__ == '__main__':
    success = execute_rollback()
    exit(0 if success else 1)
