-- 创建用户表（如果不存在）
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
BEGIN
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(100) NOT NULL UNIQUE,
        password_hash NVARCHAR(256) NOT NULL,
        display_name NVARCHAR(200),
        role NVARCHAR(20) NOT NULL DEFAULT 'viewer',
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT GETDATE(),
        last_login_at DATETIME,
        version INT NOT NULL DEFAULT 1
    );
    
    PRINT '用户表创建成功';
END
ELSE
BEGIN
    PRINT '用户表已存在';
END
GO

-- 创建索引
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_username' AND object_id = OBJECT_ID('users'))
BEGIN
    CREATE INDEX idx_users_username ON users(username);
    PRINT '用户名索引创建成功';
END
GO

-- 检查是否存在管理员账号
IF NOT EXISTS (SELECT * FROM users WHERE username = 'admin')
BEGIN
    -- 注意：这里的密码哈希是 'Admin@123456' 的 werkzeug 哈希值
    -- 实际使用时应该通过 Python 脚本生成正确的哈希值
    PRINT '警告：请运行 Python 脚本 init_db.py 来创建管理员账号';
    PRINT '或者运行 update_password.py 来设置管理员密码';
END
ELSE
BEGIN
    PRINT '管理员账号已存在';
END
GO

-- 显示用户表结构
SELECT 
    COLUMN_NAME as '列名',
    DATA_TYPE as '数据类型',
    CHARACTER_MAXIMUM_LENGTH as '最大长度',
    IS_NULLABLE as '可为空',
    COLUMN_DEFAULT as '默认值'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;
GO

-- 显示现有用户（不显示密码）
SELECT 
    id as '用户ID',
    username as '用户名',
    display_name as '显示名称',
    role as '角色',
    is_active as '是否激活',
    created_at as '创建时间',
    last_login_at as '最后登录时间'
FROM users;
GO
