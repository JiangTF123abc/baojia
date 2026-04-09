# 设计文档：用户注册与密码管理系统

## 概述

本系统实现完整的用户注册与密码管理功能，包括邮箱验证、密码强度检查、忘记密码流程和密码重置功能。系统采用前后端分离架构，后端使用 Flask + SQLAlchemy + SQL Server，前端使用 Vue 3 + TypeScript + Element Plus。核心安全特性包括邮箱唯一性验证、验证码时效控制、密码加密存储和防暴力破解机制。

## 架构设计

### 系统架构图

```mermaid
graph TB
    subgraph Frontend["前端层 (Vue 3 + TypeScript)"]
        RegPage[注册页面]
        ForgotPage[忘记密码页面]
        VerifyPage[验证码验证页面]
        ResetPage[密码重置页面]
    end
    
    subgraph Backend["后端层 (Flask)"]
        AuthAPI[认证API]
        PasswordAPI[密码管理API]
        EmailService[邮件服务]
        ValidationService[验证服务]
    end
    
    subgraph Data["数据层"]
        UserDB[(用户表)]
        VerifyDB[(验证码表)]
    end
    
    subgraph External["外部服务"]
        SMTP[SMTP邮件服务器]
    end
    
    RegPage --> AuthAPI
    ForgotPage --> PasswordAPI
    VerifyPage --> PasswordAPI
    ResetPage --> PasswordAPI
    
    AuthAPI --> ValidationService
    AuthAPI --> UserDB
    
    PasswordAPI --> ValidationService
    PasswordAPI --> EmailService
    PasswordAPI --> VerifyDB
    PasswordAPI --> UserDB
    
    EmailService --> SMTP
```

### 主要业务流程

#### 用户注册流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant A as 认证API
    participant V as 验证服务
    participant D as 数据库
    
    U->>F: 填写注册信息
    F->>F: 前端验证（格式、密码强度）
    F->>A: POST /api/auth/register
    A->>V: 验证邮箱格式
    A->>D: 检查邮箱唯一性
    alt 邮箱已存在
        D-->>A: 邮箱已注册
        A-->>F: 400 邮箱已被使用
        F-->>U: 显示错误提示
    else 邮箱可用
        A->>V: 验证密码强度
        A->>D: 创建用户记录
        D-->>A: 用户创建成功
        A-->>F: 200 注册成功 + JWT Token
        F-->>U: 跳转到主页
    end
```


#### 忘记密码流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant P as 密码API
    participant E as 邮件服务
    participant D as 数据库
    participant S as SMTP服务器
    
    U->>F: 输入注册邮箱
    F->>P: POST /api/password/forgot
    P->>D: 查询邮箱是否存在
    alt 邮箱不存在
        D-->>P: 未找到用户
        P-->>F: 400 邮箱未注册
        F-->>U: 显示错误提示
    else 邮箱存在
        P->>P: 生成6位数字验证码
        P->>D: 保存验证码（5分钟有效期）
        P->>E: 发送验证码邮件
        E->>S: SMTP发送
        S-->>E: 发送成功
        E-->>P: 邮件已发送
        P-->>F: 200 验证码已发送
        F-->>U: 跳转到验证码页面
    end
```

#### 验证码验证与密码重置流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant P as 密码API
    participant D as 数据库
    
    U->>F: 输入验证码
    F->>P: POST /api/password/verify-code
    P->>D: 查询验证码
    alt 验证码无效或过期
        D-->>P: 验证码不存在或已过期
        P-->>F: 400 验证码错误
        F-->>U: 显示错误提示
    else 验证码有效
        D-->>P: 验证码正确
        P->>P: 生成重置令牌
        P-->>F: 200 验证成功 + 重置令牌
        F-->>U: 跳转到密码重置页面
        
        U->>F: 输入新密码
        F->>P: POST /api/password/reset
        P->>D: 验证重置令牌
        P->>D: 更新用户密码
        D-->>P: 密码更新成功
        P->>D: 删除已使用的验证码
        P-->>F: 200 密码重置成功
        F-->>U: 跳转到登录页面
    end
```

## 组件与接口设计

### 后端组件

#### 1. 用户模型 (User Model)

**目的**: 扩展现有用户模型，添加邮箱字段和相关验证

**接口**:
```python
class User(db.Model):
    __tablename__ = 'users'
    
    id: int
    username: str
    email: str  # 新增字段
    password_hash: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime
    version: int
    
    def set_password(self, password: str) -> None
    def check_password(self, password: str) -> bool
    def to_dict(self) -> dict
```

**职责**:
- 存储用户基本信息和邮箱地址
- 提供密码加密和验证方法
- 序列化用户数据

#### 2. 验证码模型 (VerificationCode Model)

**目的**: 管理密码重置验证码的生成、存储和验证

**接口**:
```python
class VerificationCode(db.Model):
    __tablename__ = 'verification_codes'
    
    id: int
    user_id: int
    email: str
    code: str
    purpose: str  # 'password_reset'
    expires_at: datetime
    is_used: bool
    created_at: datetime
    
    @staticmethod
    def generate_code() -> str
    def is_valid() -> bool
    def mark_as_used() -> None
```

**职责**:
- 生成随机6位数字验证码
- 管理验证码有效期（5-10分钟）
- 跟踪验证码使用状态

