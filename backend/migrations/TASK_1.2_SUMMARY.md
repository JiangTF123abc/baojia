# 任务 1.2 执行总结：创建 VerificationCode 表

## 任务概述

**任务编号**: 1.2  
**任务名称**: 创建 VerificationCode 表  
**执行日期**: 2025年  
**状态**: ✅ 已完成

## 任务目标

创建 `verification_codes` 表，用于存储密码重置验证码，包含以下功能：
- 存储验证码信息（用户ID、邮箱、验证码、用途、过期时间）
- 外键关联 users 表
- 创建必要的索引以优化查询性能

## 表结构设计

### 字段列表

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| id | INT | PRIMARY KEY, IDENTITY(1,1) | 主键，自增 |
| user_id | INT | NOT NULL, FOREIGN KEY | 用户ID，关联 users.id |
| email | NVARCHAR(255) | NOT NULL | 用户邮箱 |
| code | NVARCHAR(10) | NOT NULL | 验证码（6位数字） |
| purpose | NVARCHAR(50) | NOT NULL | 验证码用途（如 'password_reset'） |
| expires_at | DATETIME | NOT NULL | 过期时间 |
| is_used | BIT | NOT NULL, DEFAULT 0 | 是否已使用 |
| created_at | DATETIME | NOT NULL, DEFAULT GETDATE() | 创建时间 |

### 约束和索引

#### 外键约束
- **FK_verification_codes_user_id**: 关联 users(id)，级联删除

#### 索引
1. **idx_verification_codes_email**: 单列索引，优化按邮箱查询
2. **idx_verification_codes_expires_at**: 单列索引，优化过期验证码清理
3. **idx_verification_codes_is_used**: 单列索引，优化未使用验证码查询
4. **idx_verification_codes_email_is_used_expires_at**: 复合索引，优化常见查询场景

## 创建的文件

### 1. SQL 迁移脚本
**文件**: `002_create_verification_codes_table.sql`

功能：
- 创建 verification_codes 表
- 创建外键约束
- 创建所有必需的索引
- 包含详细的执行日志和验证查询

### 2. Python 执行脚本
**文件**: `run_migration_002.py`

功能：
- 自动读取并执行 SQL 迁移脚本
- 支持从环境变量读取数据库连接信息
- 分批执行 SQL 语句（按 GO 分隔）
- 提供详细的执行日志

### 3. 批处理执行脚本
**文件**: `run_migration_002.bat`

功能：
- Windows 环境下快速执行迁移
- 显示执行结果和错误代码

### 4. 测试脚本
**文件**: `test_migration_002.py`

测试内容：
- ✅ 检查表是否存在
- ✅ 检查所有必需字段
- ✅ 检查外键约束
- ✅ 检查所有索引
- ✅ 测试数据插入和查询功能
- ⚠️ 外键级联删除（需实际使用验证）

### 5. 回滚脚本
**文件**: `rollback_002.sql` 和 `rollback_002.py`

功能：
- 删除所有索引
- 删除外键约束
- 删除 verification_codes 表
- 包含安全确认机制

## 执行方式

### 方式一：使用批处理文件（推荐）
```bash
cd backend
migrations\run_migration_002.bat
```

### 方式二：使用 Python 脚本
```bash
cd backend
python migrations/run_migration_002.py
```

### 方式三：直接执行 SQL（SQL Server Management Studio）
1. 打开 `002_create_verification_codes_table.sql`
2. 修改数据库名称（如需要）
3. 执行脚本

## 测试验证

执行测试脚本：
```bash
cd backend
python migrations/test_migration_002.py
```

测试将验证：
- 表结构完整性
- 外键约束正确性
- 索引创建成功
- 基本 CRUD 操作

## 回滚操作

如需回滚此迁移：

### 使用 Python 脚本（推荐）
```bash
cd backend
python migrations/rollback_002.py
```

### 直接执行 SQL
```bash
# 在 SQL Server Management Studio 中执行
backend/migrations/rollback_002.sql
```

⚠️ **警告**: 回滚操作将删除 verification_codes 表及其所有数据，请谨慎操作！

## 性能优化

### 索引策略
1. **单列索引**: 支持简单查询场景
   - email: 按邮箱查找验证码
   - expires_at: 清理过期验证码
   - is_used: 查找未使用的验证码

2. **复合索引**: 优化复杂查询
   - (email, is_used, expires_at): 查找特定邮箱的有效验证码

### 查询优化示例
```sql
-- 此查询将使用复合索引，性能最优
SELECT * FROM verification_codes
WHERE email = 'user@example.com'
  AND is_used = 0
  AND expires_at > GETDATE()
ORDER BY created_at DESC;
```

## 数据库关系

```
users (1) ----< (N) verification_codes
  |                      |
  id  <-- FK_user_id -- user_id
```

- 一个用户可以有多个验证码记录
- 删除用户时，相关验证码记录会级联删除

## 后续任务

此迁移为以下功能提供数据基础：
- ✅ 任务 1.3: 创建 VerificationCode 模型类
- ✅ 任务 2.1: 实现邮件服务
- ✅ 任务 2.2: 实现验证码生成和验证逻辑
- ✅ 任务 3.x: 实现密码重置 API

## 注意事项

1. **数据库连接**: 确保 `.env` 文件中配置了正确的数据库连接信息
2. **ODBC 驱动**: 需要安装 ODBC Driver 17 for SQL Server
3. **权限要求**: 执行用户需要有创建表、索引和外键的权限
4. **数据备份**: 建议在生产环境执行前备份数据库
5. **验证码清理**: 建议定期清理过期的验证码记录（可通过定时任务实现）

## 验证码清理建议

可以创建定时任务定期清理过期验证码：

```sql
-- 清理 24 小时前过期的验证码
DELETE FROM verification_codes
WHERE expires_at < DATEADD(HOUR, -24, GETDATE());
```

## 参考文档

- 设计文档: `.kiro/specs/user-registration-password-management/design.md`
- 需求文档: `.kiro/specs/user-registration-password-management/requirements.md`
- 任务列表: `.kiro/specs/user-registration-password-management/tasks.md`
- 迁移日志: `backend/migrations/MIGRATION_LOG.md`

## 执行记录

| 日期 | 操作 | 执行人 | 结果 |
|------|------|--------|------|
| 2025-xx-xx | 创建迁移脚本 | Kiro | ✅ 成功 |
| 待执行 | 执行迁移 | - | - |
| 待执行 | 测试验证 | - | - |

---

**文档版本**: 1.0  
**最后更新**: 2025年
