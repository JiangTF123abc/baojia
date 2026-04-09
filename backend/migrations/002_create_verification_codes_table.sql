-- 创建验证码表迁移脚本
-- 任务：1.2 创建 VerificationCode 表
-- 执行环境：SQL Server
-- 执行方式：在SQL Server Management Studio中执行此脚本

USE [baojia];  -- 替换为你的数据库名
GO

PRINT '============================================================';
PRINT '开始创建验证码表...';
PRINT '============================================================';
PRINT '';

-- 1. 创建 verification_codes 表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'verification_codes')
BEGIN
    CREATE TABLE verification_codes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        email NVARCHAR(255) NOT NULL,
        code NVARCHAR(10) NOT NULL,
        purpose NVARCHAR(50) NOT NULL,
        expires_at DATETIME NOT NULL,
        is_used BIT NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT GETDATE(),
        
        -- 外键约束：关联 users 表
        CONSTRAINT FK_verification_codes_user_id 
            FOREIGN KEY (user_id) REFERENCES users(id) 
            ON DELETE CASCADE
    );
    PRINT '✓ 已创建 verification_codes 表';
END
ELSE
BEGIN
    PRINT '✗ verification_codes 表已存在，跳过创建';
END
GO

-- 2. 创建 email 索引（提高按邮箱查询性能）
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_verification_codes_email' AND object_id = OBJECT_ID('verification_codes'))
BEGIN
    CREATE INDEX idx_verification_codes_email ON verification_codes(email);
    PRINT '✓ 已创建 email 索引';
END
ELSE
BEGIN
    PRINT '✗ email 索引已存在';
END
GO

-- 3. 创建 expires_at 索引（提高过期验证码清理性能）
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_verification_codes_expires_at' AND object_id = OBJECT_ID('verification_codes'))
BEGIN
    CREATE INDEX idx_verification_codes_expires_at ON verification_codes(expires_at);
    PRINT '✓ 已创建 expires_at 索引';
END
ELSE
BEGIN
    PRINT '✗ expires_at 索引已存在';
END
GO

-- 4. 创建 is_used 索引（提高未使用验证码查询性能）
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_verification_codes_is_used' AND object_id = OBJECT_ID('verification_codes'))
BEGIN
    CREATE INDEX idx_verification_codes_is_used ON verification_codes(is_used);
    PRINT '✓ 已创建 is_used 索引';
END
ELSE
BEGIN
    PRINT '✗ is_used 索引已存在';
END
GO

-- 5. 创建复合索引（优化常见查询：按邮箱查找未使用且未过期的验证码）
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_verification_codes_email_is_used_expires_at' AND object_id = OBJECT_ID('verification_codes'))
BEGIN
    CREATE INDEX idx_verification_codes_email_is_used_expires_at 
    ON verification_codes(email, is_used, expires_at);
    PRINT '✓ 已创建复合索引 (email, is_used, expires_at)';
END
ELSE
BEGIN
    PRINT '✗ 复合索引已存在';
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

-- 显示表结构
PRINT '表结构信息：';
SELECT 
    COLUMN_NAME as '列名',
    DATA_TYPE as '数据类型',
    CHARACTER_MAXIMUM_LENGTH as '最大长度',
    IS_NULLABLE as '可为空',
    COLUMN_DEFAULT as '默认值'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'verification_codes'
ORDER BY ORDINAL_POSITION;

PRINT '';
PRINT '外键约束信息：';
-- 显示外键约束
SELECT 
    fk.name as '约束名称',
    OBJECT_NAME(fk.parent_object_id) as '子表',
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) as '子表列',
    OBJECT_NAME(fk.referenced_object_id) as '父表',
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) as '父表列',
    fk.delete_referential_action_desc as '删除操作'
FROM sys.foreign_keys fk
INNER JOIN sys.foreign_key_columns fkc 
    ON fk.object_id = fkc.constraint_object_id
WHERE fk.parent_object_id = OBJECT_ID('verification_codes');

PRINT '';
PRINT '索引信息：';
-- 显示所有索引
SELECT 
    i.name as '索引名称',
    i.type_desc as '索引类型',
    i.is_unique as '是否唯一',
    i.is_primary_key as '是否主键',
    STRING_AGG(c.name, ', ') as '索引列'
FROM sys.indexes i
INNER JOIN sys.index_columns ic 
    ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN sys.columns c 
    ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.object_id = OBJECT_ID('verification_codes')
GROUP BY i.name, i.type_desc, i.is_unique, i.is_primary_key
ORDER BY i.is_primary_key DESC, i.name;

GO
