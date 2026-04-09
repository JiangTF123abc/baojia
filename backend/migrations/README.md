# 数据库迁移脚本

本目录包含用户注册与密码管理系统的数据库迁移脚本。

## 迁移列表

### 001 - 添加用户邮箱字段

**文件**: `001_add_email_to_users.sql` / `run_migration_001.py`

**任务**: 1.1 为 User 表添加 email 字段

**变更内容**:
- 添加 `email` 字段 (NVARCHAR(255), NOT NULL, UNIQUE)
- 为现有用户生成默认邮箱 (username@example.com)
- 创建邮箱唯一约束 (UQ_users_email)
- 创建邮箱索引 (idx_users_email)

**执行方式**:

#### 方式 1: 使用 Python 脚本（推荐）

```bash
# 在项目根目录执行
python backend/migrations/run_migration_001.py
```

优点：
- 自动读取 .env 配置
- 提供详细的执行日志
- 自动验证迁移结果
- 错误处理更完善

#### 方式 2: 使用 SQL 脚本

1. 打开 SQL Server Management Studio (SSMS)
2. 连接到数据库服务器
3. 打开 `001_add_email_to_users.sql` 文件
4. 修改第一行的数据库名称（如果需要）
5. 执行脚本 (F5)

## 注意事项

### 执行前检查

1. **备份数据库**: 在执行任何迁移前，请先备份数据库
   ```sql
   BACKUP DATABASE [baojia] TO DISK = 'C:\Backup\baojia_backup.bak'
   ```

2. **检查环境变量**: 确保 `backend/.env` 文件包含正确的数据库连接信息
   ```
   DB_SERVER=localhost
   DB_NAME=baojia
   DB_USER=sa
   DB_PASSWORD=your_password
   ```

3. **检查依赖**: 确保已安装 pyodbc 和 python-dotenv
   ```bash
   pip install pyodbc python-dotenv
   ```

### 迁移特性

- **幂等性**: 所有迁移脚本都是幂等的，可以安全地重复执行
- **验证**: 每个迁移都会在执行后验证结果
- **回滚**: 如果需要回滚，请参考下方的回滚脚本

### 现有用户处理

迁移会为所有现有用户自动生成默认邮箱地址，格式为 `username@example.com`。

**重要**: 在生产环境中，您需要：
1. 通知用户更新他们的真实邮箱地址
2. 或者通过管理界面批量导入真实邮箱
3. 或者在用户下次登录时强制更新邮箱

## 回滚脚本

如果需要回滚迁移 001，可以执行以下 SQL：

```sql
USE [baojia];
GO

-- 删除索引
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_email')
    DROP INDEX idx_users_email ON users;

-- 删除唯一约束
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'UQ_users_email')
    ALTER TABLE users DROP CONSTRAINT UQ_users_email;

-- 删除字段
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
           WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email')
    ALTER TABLE users DROP COLUMN email;

PRINT '迁移 001 已回滚';
GO
```

## 验证迁移

执行迁移后，可以运行以下查询验证结果：

```sql
-- 检查字段是否存在
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email';

-- 检查唯一约束
SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_NAME = 'users' AND CONSTRAINT_TYPE = 'UNIQUE';

-- 检查索引
SELECT name, type_desc, is_unique
FROM sys.indexes
WHERE object_id = OBJECT_ID('users') AND name LIKE '%email%';

-- 检查数据
SELECT id, username, email FROM users;
```

## 下一步

完成此迁移后，您需要：

1. 更新 `backend/app/models/user.py` 模型，添加 email 字段
2. 实现用户注册 API，包含邮箱验证
3. 实现忘记密码功能
4. 配置邮件服务

详见 `.kiro/specs/user-registration-password-management/tasks.md`
