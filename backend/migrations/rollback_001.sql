-- 回滚迁移 001：删除用户邮箱字段
-- 警告：此操作将删除所有邮箱数据，请谨慎执行！
-- 执行环境：SQL Server
-- 执行方式：在SQL Server Management Studio中执行此脚本

USE [baojia];  -- 替换为你的数据库名
GO

PRINT '============================================================';
PRINT '警告：即将回滚用户表邮箱字段迁移';
PRINT '此操作将删除所有邮箱数据！';
PRINT '============================================================';
PRINT '';

-- 备份提醒
PRINT '请确认：';
PRINT '1. 已备份数据库';
PRINT '2. 确实需要回滚此迁移';
PRINT '';
PRINT '如需继续，请执行以下步骤...';
PRINT '';

-- 1. 删除索引
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_email' AND object_id = OBJECT_ID('users'))
BEGIN
    DROP INDEX idx_users_email ON users;
    PRINT '✓ 已删除 email 索引';
END
ELSE
BEGIN
    PRINT '✗ email 索引不存在';
END
GO

-- 2. 删除唯一约束
IF EXISTS (SELECT * FROM sys.objects WHERE name = 'UQ_users_email' AND type = 'UQ')
BEGIN
    ALTER TABLE users DROP CONSTRAINT UQ_users_email;
    PRINT '✓ 已删除 email 唯一约束';
END
ELSE
BEGIN
    PRINT '✗ email 唯一约束不存在';
END
GO

-- 3. 删除 email 字段
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email')
BEGIN
    ALTER TABLE users DROP COLUMN email;
    PRINT '✓ 已删除 email 字段';
END
ELSE
BEGIN
    PRINT '✗ email 字段不存在';
END
GO

PRINT '';
PRINT '============================================================';
PRINT '回滚完成！';
PRINT '============================================================';
PRINT '';

-- 验证回滚结果
PRINT '验证回滚结果：';

-- 检查字段是否已删除
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'email')
BEGIN
    PRINT '✓ email 字段已成功删除';
END
ELSE
BEGIN
    PRINT '✗ email 字段仍然存在';
END

-- 显示当前用户表结构
PRINT '';
PRINT '当前用户表结构：';
SELECT 
    COLUMN_NAME as '列名',
    DATA_TYPE as '数据类型',
    CHARACTER_MAXIMUM_LENGTH as '最大长度',
    IS_NULLABLE as '可为空'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;

GO
