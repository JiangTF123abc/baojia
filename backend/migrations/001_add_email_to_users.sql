-- 用户表添加邮箱字段迁移脚本
-- 任务：1.1 为 User 表添加 email 字段
-- 执行环境：SQL Server
-- 执行方式：在SQL Server Management Studio中执行此脚本

USE [baojia];  -- 替换为你的数据库名
GO

PRINT '============================================================';
PRINT '开始执行用户表邮箱字段迁移...';
PRINT '============================================================';
PRINT '';

-- 1. 添加 email 字段（允许NULL，稍后更新）
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email')
BEGIN
    ALTER TABLE users ADD email NVARCHAR(255) NULL;
    PRINT '✓ 已添加 email 字段';
END
ELSE
BEGIN
    PRINT '✗ email 字段已存在，跳过添加';
END
GO

-- 2. 为现有用户生成默认邮箱（使用用户名@example.com格式）
UPDATE users 
SET email = username + '@example.com'
WHERE email IS NULL;
PRINT '✓ 已为现有用户设置默认邮箱';
GO

-- 3. 将 email 字段设置为 NOT NULL
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email' AND IS_NULLABLE = 'YES')
BEGIN
    ALTER TABLE users ALTER COLUMN email NVARCHAR(255) NOT NULL;
    PRINT '✓ 已将 email 字段设置为 NOT NULL';
END
ELSE
BEGIN
    PRINT '✗ email 字段已经是 NOT NULL';
END
GO

-- 4. 添加唯一约束
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'UQ_users_email' AND object_id = OBJECT_ID('users'))
BEGIN
    ALTER TABLE users ADD CONSTRAINT UQ_users_email UNIQUE (email);
    PRINT '✓ 已创建 email 唯一约束';
END
ELSE
BEGIN
    PRINT '✗ email 唯一约束已存在';
END
GO

-- 5. 创建邮箱字段索引（提高查询性能）
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_email' AND object_id = OBJECT_ID('users'))
BEGIN
    CREATE INDEX idx_users_email ON users(email);
    PRINT '✓ 已创建 email 索引';
END
ELSE
BEGIN
    PRINT '✗ email 索引已存在';
END
GO

PRINT '';
PRINT '============================================================';
PRINT '迁移完成！';
PRINT '============================================================';
PRINT '';

-- 6. 验证迁移结果
PRINT '验证迁移结果：';
PRINT '';

-- 显示 email 字段信息
SELECT 
    COLUMN_NAME as '列名',
    DATA_TYPE as '数据类型',
    CHARACTER_MAXIMUM_LENGTH as '最大长度',
    IS_NULLABLE as '可为空',
    COLUMN_DEFAULT as '默认值'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email';

-- 显示唯一约束
SELECT 
    CONSTRAINT_NAME as '约束名称',
    CONSTRAINT_TYPE as '约束类型'
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_NAME = 'users' AND CONSTRAINT_TYPE = 'UNIQUE';

-- 显示索引
SELECT 
    name as '索引名称',
    type_desc as '索引类型',
    is_unique as '是否唯一'
FROM sys.indexes
WHERE object_id = OBJECT_ID('users') AND name LIKE '%email%';

-- 显示用户数据（验证邮箱已填充）
PRINT '';
PRINT '用户邮箱数据示例：';
SELECT TOP 5
    id as '用户ID',
    username as '用户名',
    email as '邮箱',
    created_at as '创建时间'
FROM users
ORDER BY id;

GO
