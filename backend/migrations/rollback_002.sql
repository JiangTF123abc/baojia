-- 回滚验证码表迁移脚本
-- 任务：1.2 创建 VerificationCode 表 - 回滚
-- 执行环境：SQL Server
-- 执行方式：在SQL Server Management Studio中执行此脚本

USE [baojia];  -- 替换为你的数据库名
GO

PRINT '============================================================';
PRINT '开始回滚验证码表迁移...';
PRINT '============================================================';
PRINT '';

-- 1. 删除复合索引
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_verification_codes_email_is_used_expires_at' AND object_id = OBJECT_ID('verification_codes'))
BEGIN
    DROP INDEX idx_verification_codes_email_is_used_expires_at ON verification_codes;
    PRINT '✓ 已删除复合索引 (email, is_used, expires_at)';
END
ELSE
BEGIN
    PRINT '✗ 复合索引不存在';
END
GO

-- 2. 删除 is_used 索引
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_verification_codes_is_used' AND object_id = OBJECT_ID('verification_codes'))
BEGIN
    DROP INDEX idx_verification_codes_is_used ON verification_codes;
    PRINT '✓ 已删除 is_used 索引';
END
ELSE
BEGIN
    PRINT '✗ is_used 索引不存在';
END
GO

-- 3. 删除 expires_at 索引
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_verification_codes_expires_at' AND object_id = OBJECT_ID('verification_codes'))
BEGIN
    DROP INDEX idx_verification_codes_expires_at ON verification_codes;
    PRINT '✓ 已删除 expires_at 索引';
END
ELSE
BEGIN
    PRINT '✗ expires_at 索引不存在';
END
GO

-- 4. 删除 email 索引
IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_verification_codes_email' AND object_id = OBJECT_ID('verification_codes'))
BEGIN
    DROP INDEX idx_verification_codes_email ON verification_codes;
    PRINT '✓ 已删除 email 索引';
END
ELSE
BEGIN
    PRINT '✗ email 索引不存在';
END
GO

-- 5. 删除外键约束
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_verification_codes_user_id' AND parent_object_id = OBJECT_ID('verification_codes'))
BEGIN
    ALTER TABLE verification_codes DROP CONSTRAINT FK_verification_codes_user_id;
    PRINT '✓ 已删除外键约束 FK_verification_codes_user_id';
END
ELSE
BEGIN
    PRINT '✗ 外键约束不存在';
END
GO

-- 6. 删除 verification_codes 表
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'verification_codes')
BEGIN
    DROP TABLE verification_codes;
    PRINT '✓ 已删除 verification_codes 表';
END
ELSE
BEGIN
    PRINT '✗ verification_codes 表不存在';
END
GO

PRINT '';
PRINT '============================================================';
PRINT '回滚完成！';
PRINT '============================================================';
PRINT '';

-- 验证回滚结果
PRINT '验证回滚结果：';
PRINT '';

-- 检查表是否已删除
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'verification_codes')
BEGIN
    PRINT '✓ verification_codes 表已成功删除';
END
ELSE
BEGIN
    PRINT '✗ verification_codes 表仍然存在';
END

GO
