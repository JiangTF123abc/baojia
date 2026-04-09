"""
执行验证码表迁移脚本
任务：1.2 创建 VerificationCode 表
"""

import pyodbc
import os
from pathlib import Path

def run_migration():
    """执行 SQL 迁移脚本"""
    
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
    print("开始执行验证码表迁移...")
    print("=" * 60)
    print(f"数据库服务器: {server}")
    print(f"数据库名称: {database}")
    print("")
    
    try:
        # 读取 SQL 脚本
        script_path = Path(__file__).parent / '002_create_verification_codes_table.sql'
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 连接数据库
        print("正在连接数据库...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 执行 SQL 脚本（分批执行，按 GO 分隔）
        print("正在执行迁移脚本...")
        print("")
        
        batches = sql_script.split('GO')
        for i, batch in enumerate(batches, 1):
            batch = batch.strip()
            if batch:
                try:
                    cursor.execute(batch)
                    # 获取所有打印消息
                    while cursor.nextset():
                        pass
                    conn.commit()
                except Exception as e:
                    print(f"批次 {i} 执行出错: {str(e)}")
                    raise
        
        print("")
        print("=" * 60)
        print("迁移执行成功！")
        print("=" * 60)
        
        cursor.close()
        conn.close()
        
        return True
        
    except FileNotFoundError:
        print(f"错误: 找不到迁移脚本文件 {script_path}")
        return False
    except pyodbc.Error as e:
        print(f"数据库错误: {str(e)}")
        return False
    except Exception as e:
        print(f"执行失败: {str(e)}")
        return False

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
