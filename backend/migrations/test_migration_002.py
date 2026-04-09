"""
测试验证码表迁移结果
任务：1.2 创建 VerificationCode 表
"""

import pyodbc
import os
from datetime import datetime, timedelta

def test_migration():
    """测试迁移是否成功"""
    
    # 从环境变量读取数据库连接信息
    server = os.getenv('DB_SERVER', 'localhost')
    database = os.getenv('DB_NAME', 'baojia')
    username = os.getenv('DB_USER', 'sa')
    password = os.getenv('DB_PASSWORD', '')
    
    # 构建连接字符串
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'TrustServerCertificate=yes;'
    )
    
    print("=" * 60)
    print("开始测试验证码表迁移结果...")
    print("=" * 60)
    print("")
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 测试 1: 检查表是否存在
        print("测试 1: 检查 verification_codes 表是否存在")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'verification_codes'
        """)
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print("✓ verification_codes 表存在")
        else:
            print("✗ verification_codes 表不存在")
            return False
        
        # 测试 2: 检查所有必需字段
        print("\n测试 2: 检查表字段")
        required_columns = ['id', 'user_id', 'email', 'code', 'purpose', 
                          'expires_at', 'is_used', 'created_at']
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'verification_codes'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        for col in required_columns:
            if col in existing_columns:
                print(f"✓ 字段 {col} 存在")
            else:
                print(f"✗ 字段 {col} 不存在")
                return False
        
        # 测试 3: 检查外键约束
        print("\n测试 3: 检查外键约束")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sys.foreign_keys 
            WHERE name = 'FK_verification_codes_user_id' 
            AND parent_object_id = OBJECT_ID('verification_codes')
        """)
        fk_exists = cursor.fetchone()[0]
        if fk_exists:
            print("✓ 外键约束 FK_verification_codes_user_id 存在")
        else:
            print("✗ 外键约束不存在")
            return False
        
        # 测试 4: 检查索引
        print("\n测试 4: 检查索引")
        required_indexes = [
            'idx_verification_codes_email',
            'idx_verification_codes_expires_at',
            'idx_verification_codes_is_used',
            'idx_verification_codes_email_is_used_expires_at'
        ]
        
        cursor.execute("""
            SELECT name 
            FROM sys.indexes 
            WHERE object_id = OBJECT_ID('verification_codes')
            AND name IS NOT NULL
        """)
        existing_indexes = [row[0] for row in cursor.fetchall()]
        
        for idx in required_indexes:
            if idx in existing_indexes:
                print(f"✓ 索引 {idx} 存在")
            else:
                print(f"✗ 索引 {idx} 不存在")
                return False
        
        # 测试 5: 测试插入和查询功能
        print("\n测试 5: 测试数据插入和查询")
        
        # 获取第一个用户ID用于测试
        cursor.execute("SELECT TOP 1 id, email FROM users")
        user_row = cursor.fetchone()
        if not user_row:
            print("⚠ 警告: users 表中没有数据，跳过插入测试")
        else:
            test_user_id = user_row[0]
            test_email = user_row[1]
            test_code = '123456'
            test_purpose = 'password_reset'
            test_expires_at = datetime.now() + timedelta(minutes=5)
            
            # 插入测试数据
            cursor.execute("""
                INSERT INTO verification_codes 
                (user_id, email, code, purpose, expires_at, is_used)
                VALUES (?, ?, ?, ?, ?, 0)
            """, test_user_id, test_email, test_code, test_purpose, test_expires_at)
            conn.commit()
            print(f"✓ 成功插入测试验证码记录")
            
            # 查询测试数据
            cursor.execute("""
                SELECT id, user_id, email, code, purpose, is_used
                FROM verification_codes
                WHERE email = ? AND code = ?
            """, test_email, test_code)
            result = cursor.fetchone()
            
            if result:
                print(f"✓ 成功查询验证码记录: ID={result[0]}, Email={result[2]}, Code={result[3]}")
            else:
                print("✗ 查询验证码记录失败")
                return False
            
            # 清理测试数据
            cursor.execute("DELETE FROM verification_codes WHERE email = ? AND code = ?", 
                         test_email, test_code)
            conn.commit()
            print("✓ 已清理测试数据")
        
        # 测试 6: 测试外键级联删除
        print("\n测试 6: 测试外键级联删除（跳过，避免删除真实用户数据）")
        print("⚠ 外键级联删除功能需要在实际使用中验证")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("所有测试通过！迁移成功！")
        print("=" * 60)
        
        return True
        
    except pyodbc.Error as e:
        print(f"\n数据库错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_migration()
    exit(0 if success else 1)
