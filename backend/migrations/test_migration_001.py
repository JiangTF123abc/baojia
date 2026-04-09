"""
测试迁移脚本 001 的语法和逻辑
不会实际修改数据库，仅验证脚本正确性
"""

import os
import sys

def test_sql_file_exists():
    """测试 SQL 文件是否存在"""
    sql_file = os.path.join(os.path.dirname(__file__), '001_add_email_to_users.sql')
    assert os.path.exists(sql_file), "SQL 文件不存在"
    print("✓ SQL 文件存在")
    return sql_file

def test_sql_syntax(sql_file):
    """测试 SQL 语法（基本检查）"""
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键语句
    assert 'ALTER TABLE users ADD email' in content, "缺少添加字段语句"
    assert 'NVARCHAR(255)' in content, "邮箱字段类型不正确"
    assert 'NOT NULL' in content, "缺少 NOT NULL 约束"
    assert 'UNIQUE' in content, "缺少唯一约束"
    assert 'CREATE INDEX' in content, "缺少索引创建语句"
    assert 'UPDATE users' in content, "缺少默认值更新语句"
    
    print("✓ SQL 语法检查通过")

def test_python_script_exists():
    """测试 Python 脚本是否存在"""
    py_file = os.path.join(os.path.dirname(__file__), 'run_migration_001.py')
    assert os.path.exists(py_file), "Python 脚本不存在"
    print("✓ Python 脚本存在")
    return py_file

def test_python_imports(py_file):
    """测试 Python 脚本导入"""
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'import pyodbc' in content, "缺少 pyodbc 导入"
    assert 'from dotenv import load_dotenv' in content, "缺少 dotenv 导入"
    assert 'def get_db_connection' in content, "缺少数据库连接函数"
    assert 'def execute_migration' in content, "缺少迁移执行函数"
    
    print("✓ Python 脚本结构检查通过")

def test_readme_exists():
    """测试 README 是否存在"""
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    assert os.path.exists(readme_file), "README 文件不存在"
    print("✓ README 文件存在")

def test_bat_file_exists():
    """测试批处理文件是否存在"""
    bat_file = os.path.join(os.path.dirname(__file__), 'run_migration_001.bat')
    assert os.path.exists(bat_file), "批处理文件不存在"
    print("✓ 批处理文件存在")

def main():
    print("=" * 60)
    print("测试迁移脚本 001")
    print("=" * 60)
    print()
    
    try:
        # 测试文件存在性
        sql_file = test_sql_file_exists()
        py_file = test_python_script_exists()
        test_readme_exists()
        test_bat_file_exists()
        
        print()
        
        # 测试内容
        test_sql_syntax(sql_file)
        test_python_imports(py_file)
        
        print()
        print("=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print()
        print("迁移脚本已准备就绪，可以执行：")
        print("  python backend/migrations/run_migration_001.py")
        print("  或")
        print("  backend/migrations/run_migration_001.bat")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {str(e)}")
        return False
    except Exception as e:
        print(f"\n✗ 发生错误: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
