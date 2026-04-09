# 数据库迁移执行日志

本文件记录所有已执行的数据库迁移。

## 迁移记录格式

```
### [迁移编号] 迁移名称
- **执行日期**: YYYY-MM-DD HH:MM:SS
- **执行人**: 执行者名称
- **状态**: 成功/失败/回滚
- **备注**: 相关说明
```

---

## 待执行迁移

### 001 - 添加用户邮箱字段
- **状态**: 待执行
- **文件**: `001_add_email_to_users.sql` / `run_migration_001.py`
- **任务**: 1.1 为 User 表添加 email 字段
- **说明**: 
  - 添加 email 字段 (NVARCHAR(255), NOT NULL, UNIQUE)
  - 为现有用户生成默认邮箱
  - 创建唯一约束和索引

### 002 - 创建验证码表
- **状态**: 待执行
- **文件**: `002_create_verification_codes_table.sql` / `run_migration_002.py`
- **任务**: 1.2 创建 VerificationCode 表
- **说明**: 
  - 创建 verification_codes 表
  - 包含字段：id, user_id, email, code, purpose, expires_at, is_used, created_at
  - 创建外键约束关联 users 表（级联删除）
  - 创建索引：email, expires_at, is_used 及复合索引

---

## 已执行迁移

_暂无已执行的迁移_

---

## 使用说明

执行迁移后，请在"已执行迁移"部分添加记录，格式如下：

```markdown
### 001 - 添加用户邮箱字段
- **执行日期**: 2025-01-15 14:30:00
- **执行人**: 张三
- **状态**: 成功
- **备注**: 为 5 个现有用户生成了默认邮箱
```
