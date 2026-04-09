# 实施计划：用户注册与密码管理系统

## 概述

本实施计划基于设计文档，将用户注册与密码管理功能分解为可执行的开发任务。系统采用 Flask + SQLAlchemy + SQL Server 后端和 Vue 3 + TypeScript 前端架构，实现邮箱验证、密码强度检查、忘记密码流程和密码重置功能。

## 任务列表

- [x] 1. 数据库迁移与模型扩展
  - [x] 1.1 为 User 表添加 email 字段
    - 创建数据库迁移脚本，添加 email 列（VARCHAR(255), UNIQUE, NOT NULL）
    - 为现有用户数据添加默认邮箱或处理空值
    - 创建邮箱字段的唯一索引
    - _设计参考: User Model 扩展_
  
  - [x] 1.2 创建 VerificationCode 表
    - 创建 verification_codes 表结构
    - 包含字段：id, user_id, email, code, purpose, expires_at, is_used, created_at
    - 创建外键约束关联 users 表
    - 创建索引：email, expires_at, is_used
    - _设计参考: VerificationCode Model_
  
  - [x] 1.3 更新 User 模型类
    - 在 backend/app/models/user.py 中添加 email 字段定义
    - 添加邮箱格式验证
    - 更新 to_dict() 方法包含 email 字段
    - _设计参考: User Model 接口_

- [ ] 2. 实现验证码模型与服务
  - [x] 2.1 创建 VerificationCode 模型类
    - 在 backend/app/models/ 创建 verification_code.py
    - 实现 generate_code() 静态方法（生成6位数字验证码）
    - 实现 is_valid() 方法（检查是否过期和已使用）
    - 实现 mark_as_used() 方法
    - _设计参考: VerificationCode Model 接口_
  
  - [ ] 2.2 创建邮件服务
    - 在 backend/app/services/ 创建 email_service.py
    - 实现 SMTP 邮件发送功能
    - 实现验证码邮件模板
    - 配置邮件服务器参数（从环境变量读取）
    - 添加邮件发送错误处理和重试机制
    - _设计参考: EmailService 组件_
  
  - [ ] 2.3 创建密码管理服务
    - 在 backend/app/services/ 创建 password_service.py
    - 实现 request_password_reset() 方法（生成验证码并发送邮件）
    - 实现 verify_code() 方法（验证验证码有效性）
    - 实现 reset_password() 方法（重置密码）
    - 实现验证码清理逻辑（删除过期验证码）
    - _设计参考: 忘记密码流程_

- [ ] 3. 扩展认证 API 端点
  - [ ] 3.1 更新注册端点支持邮箱
    - 修改 backend/app/api/auth.py 中的 /api/auth/register 端点
    - 添加 email 参数验证（必填、格式验证、唯一性检查）
    - 添加密码强度验证（至少8个字符，包含大小写字母和数字）
    - 更新错误消息提示
    - _设计参考: 用户注册流程_
  
  - [ ] 3.2 更新认证服务支持邮箱注册
    - 修改 backend/app/services/auth_service.py 中的 register() 方法
    - 添加邮箱唯一性检查
    - 添加邮箱格式验证
    - 保存用户邮箱到数据库
    - _设计参考: User Model 扩展_

- [ ] 4. 实现密码管理 API 端点
  - [ ] 4.1 创建密码管理 API 蓝图
    - 在 backend/app/api/ 创建 password.py
    - 创建 password_bp 蓝图，前缀 /api/password
    - 注册蓝图到主应用
    - _设计参考: PasswordAPI 组件_
  
  - [ ] 4.2 实现忘记密码端点
    - 实现 POST /api/password/forgot 端点
    - 验证邮箱格式和存在性
    - 调用密码服务生成验证码
    - 发送验证码邮件
    - 返回成功响应
    - _设计参考: 忘记密码流程_
  
  - [ ] 4.3 实现验证码验证端点
    - 实现 POST /api/password/verify-code 端点
    - 验证验证码有效性（未过期、未使用、匹配）
    - 生成重置令牌（JWT token，短期有效）
    - 返回重置令牌
    - _设计参考: 验证码验证流程_
  
  - [ ] 4.4 实现密码重置端点
    - 实现 POST /api/password/reset 端点
    - 验证重置令牌有效性
    - 验证新密码强度
    - 更新用户密码
    - 标记验证码为已使用
    - 返回成功响应
    - _设计参考: 密码重置流程_

- [ ] 5. Checkpoint - 后端功能验证
  - 确保所有后端测试通过，验证数据库迁移成功，测试 API 端点功能。如有问题请询问用户。

- [ ] 6. 前端注册页面增强
  - [ ] 6.1 更新注册表单添加邮箱字段
    - 修改 frontend/src/views/RegisterView.vue
    - 添加邮箱输入框（带格式验证）
    - 添加密码强度指示器
    - 添加密码确认输入框
    - 实现前端邮箱格式验证
    - _设计参考: 注册页面组件_
  
  - [ ] 6.2 更新注册 API 调用
    - 修改 frontend/src/stores/auth.ts 中的注册方法
    - 添加 email 参数到注册请求
    - 处理邮箱相关错误消息
    - _设计参考: 用户注册流程_

- [ ] 7. 实现忘记密码页面
  - [ ] 7.1 创建忘记密码页面组件
    - 创建 frontend/src/views/ForgotPasswordView.vue
    - 实现邮箱输入表单
    - 添加表单验证
    - 实现发送验证码按钮
    - 添加加载状态和错误提示
    - _设计参考: 忘记密码页面组件_
  
  - [ ] 7.2 实现验证码验证页面
    - 创建 frontend/src/views/VerifyCodeView.vue
    - 实现6位数字验证码输入框
    - 添加验证码倒计时显示
    - 实现重新发送验证码功能
    - 添加验证按钮和错误提示
    - _设计参考: 验证码验证页面组件_
  
  - [ ] 7.3 实现密码重置页面
    - 创建 frontend/src/views/ResetPasswordView.vue
    - 实现新密码输入表单
    - 添加密码强度指示器
    - 实现密码确认验证
    - 添加提交按钮和成功提示
    - _设计参考: 密码重置页面组件_

- [ ] 8. 实现前端密码管理服务
  - [ ] 8.1 创建密码管理 API 方法
    - 在 frontend/src/api/index.ts 添加密码管理相关方法
    - 实现 forgotPassword(email) 方法
    - 实现 verifyCode(email, code) 方法
    - 实现 resetPassword(token, newPassword) 方法
    - _设计参考: 密码管理 API 端点_
  
  - [ ] 8.2 更新路由配置
    - 修改 frontend/src/router/index.ts
    - 添加 /forgot-password 路由
    - 添加 /verify-code 路由
    - 添加 /reset-password 路由
    - 配置路由守卫（重置密码页面需要令牌）
    - _设计参考: 前端路由配置_

- [ ] 9. 更新登录页面添加忘记密码链接
  - [ ] 9.1 修改登录页面
    - 修改 frontend/src/views/LoginView.vue
    - 将"忘记密码？"链接指向 /forgot-password 路由
    - 确保链接样式与设计一致
    - _设计参考: 登录页面组件_

- [ ] 10. 实现密码强度验证工具
  - [ ] 10.1 创建密码验证工具函数
    - 在 backend/app/utils/validators.py 添加 validate_password_strength() 函数
    - 检查密码长度（至少8个字符）
    - 检查是否包含大写字母、小写字母和数字
    - 返回验证结果和错误消息
    - _设计参考: ValidationService 组件_
  
  - [ ] 10.2 创建前端密码强度组件
    - 创建 frontend/src/components/PasswordStrength/index.vue
    - 实现密码强度实时检测
    - 显示强度指示器（弱/中/强）
    - 显示密码要求提示
    - _设计参考: 密码强度检查_

- [ ] 11. 配置环境变量
  - [ ] 11.1 添加邮件服务配置
    - 在 backend/.env 添加 SMTP 配置
    - 添加 SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
    - 添加 MAIL_FROM_ADDRESS, MAIL_FROM_NAME
    - 添加验证码有效期配置 VERIFICATION_CODE_EXPIRY_MINUTES
    - _设计参考: 邮件服务配置_

- [ ] 12. Checkpoint - 端到端功能测试
  - 测试完整的用户注册流程（包含邮箱）
  - 测试忘记密码流程（发送验证码、验证、重置）
  - 测试密码强度验证
  - 测试错误处理和边界情况
  - 如有问题请询问用户。

- [ ] 13. 安全增强与优化
  - [ ] 13.1 实现验证码防暴力破解
    - 添加验证码尝试次数限制（最多5次）
    - 添加验证码请求频率限制（同一邮箱1分钟内只能请求1次）
    - 记录失败尝试到日志
    - _设计参考: 防暴力破解机制_
  
  - [ ] 13.2 添加邮箱验证安全措施
    - 对不存在的邮箱也返回成功消息（防止邮箱枚举）
    - 添加验证码加密存储
    - 实现验证码自动清理任务（删除过期验证码）
    - _设计参考: 安全特性_

- [ ] 14. 最终验收测试
  - 验证所有功能正常工作
  - 检查错误处理和用户体验
  - 确认安全措施已实施
  - 如有问题请询问用户。

## 注意事项

- 所有涉及密码的操作必须使用加密存储
- 验证码必须设置合理的过期时间（5-10分钟）
- 邮件发送失败需要有适当的错误处理
- 前端表单验证与后端验证保持一致
- 所有 API 端点需要适当的错误处理和日志记录
- 密码重置令牌应该是短期有效的（15-30分钟）
