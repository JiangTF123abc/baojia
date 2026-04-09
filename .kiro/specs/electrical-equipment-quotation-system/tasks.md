# 实施计划：电气设备报价系统

## 概述

按照"数据层 → 服务层 → API 层 → 前端"的顺序逐步实现，每个阶段均包含测试任务，确保增量验证。

## 任务

- [x] 1. 初始化项目结构与数据库模型
  - 创建 `backend/` 目录结构（app/models, app/api, app/services, app/utils）
  - 创建 `frontend/` 目录结构（src/api, src/components, src/views, src/stores, src/composables）
  - 编写 `backend/config.py`（数据库连接字符串、JWT 密钥、环境配置）
  - 编写 `backend/app/__init__.py` Flask 工厂函数，注册蓝图和扩展
  - 编写 `backend/app/extensions.py` 初始化 SQLAlchemy 和 PyJWT
  - 编写所有 SQLAlchemy 模型：`project.py`, `cabinet.py`, `structure_component.py`, `base_component.py`, `material.py`, `price_formula.py`, `template.py`, `user.py`, `audit_log.py`
  - 在模型中实现乐观锁 `version` 字段和级联删除关系
  - 编写数据库初始化脚本（建表、初始管理员账号、示例公式数据）
  - _需求：1.1, 1.2, 14.1, 18.1–18.5_

- [x] 2. 实现认证服务与 API
  - [x] 2.1 实现 `AuthService`（用户登录、密码哈希验证、JWT 签发与刷新）
    - 编写 `app/services/auth_service.py`，使用 PyJWT 签发包含 `user_id` 和 `role` 声明的令牌
    - 编写 `app/utils/decorators.py` 权限装饰器（`@require_auth`, `@require_role`）
    - _需求：15.1, 15.2, 15.3, 15.4, 15.5_

  - [ ]* 2.2 编写 AuthService 单元测试
    - 测试登录成功/失败、令牌过期返回 401、viewer 角色删除操作返回 403
    - _需求：15.3, 15.4, 15.6_

  - [x] 2.3 实现 `app/api/auth.py` 蓝图（`POST /api/auth/login`, `/refresh`, `/logout`）
    - _需求：15.1, 15.2_

- [x] 3. 实现项目与层级管理服务和 API
  - [x] 3.1 实现 `ProjectService`（CRUD、树结构查询、级联删除）
    - 编写 `app/services/project_service.py`
    - 实现乐观锁更新逻辑：`UPDATE ... WHERE id=:id AND version=:v`，影响行数为 0 时抛出 `ConflictError`
    - _需求：1.1–1.8, 14.2, 14.3, 18.1, 18.5, 18.6, 19.2, 19.3, 19.6_

  - [ ]* 3.2 编写属性测试：属性 1（创建操作生成唯一标识符）
    - **属性 1：创建操作生成唯一标识符**
    - **验证需求：1.2, 2.2**

  - [ ]* 3.3 编写属性测试：属性 2（层级关联完整性）
    - **属性 2：层级关联完整性**
    - **验证需求：18.2, 18.3, 18.4**

  - [ ]* 3.4 编写属性测试：属性 18（级联删除完整性）
    - **属性 18：级联删除完整性**
    - **验证需求：18.5**

  - [ ]* 3.5 编写属性测试：属性 14（无效输入被拒绝）
    - **属性 14：无效输入被拒绝**
    - **验证需求：18.6, 18.7, 18.8**

  - [x] 3.6 实现 `app/api/projects.py`, `cabinets.py`, `components.py` 蓝图
    - 实现所有 CRUD 端点及 `GET /api/projects/{id}/tree`
    - _需求：1.1–1.8, 14.1_

- [x] 4. 实现 Cabinet 复制与跨项目移动
  - [x] 4.1 在 `ProjectService` 中实现 `copy_cabinet` 方法
    - 深度复制所有 StructureComponent 和 BaseComponent，新 Cabinet 名称追加"(副本)"
    - _需求：2.1, 2.2, 2.3, 2.4_

  - [ ]* 4.2 编写属性测试：属性 3（Cabinet 复制完整性）
    - **属性 3：Cabinet 复制完整性**
    - **验证需求：2.1, 2.2, 2.3**

  - [x] 4.3 在 `ProjectService` 中实现 `move_cabinet` 方法（事务内执行，失败时回滚）
    - _需求：3.1, 3.2, 3.3, 3.4_

  - [ ]* 4.4 编写属性测试：属性 4（Cabinet 跨项目移动保留数据）
    - **属性 4：Cabinet 跨项目移动保留数据**
    - **验证需求：3.1, 3.2, 3.3**

  - [ ]* 4.5 编写属性测试：属性 5（移动失败时原结构不变）
    - **属性 5：移动失败时原结构不变**
    - **验证需求：3.4**

  - [x] 4.6 实现 `POST /api/cabinets/{id}/copy` 和 `PUT /api/cabinets/{id}/move` 端点
    - _需求：2.1–2.4, 3.1–3.4_

- [x] 5. 实现价格引擎服务
  - [x] 5.1 实现 `app/services/price_engine.py`
    - 使用 SymPy `sympify` 解析公式字符串，`lambdify` 生成可调用函数
    - 实现 `calculate_base_price(quantity, unit_price, discount_rate)` 函数
    - 实现 `apply_formula(base_cost, **params)` 函数
    - 实现 `format_formula(expr)` 将 SymPy 表达式格式化为字符串
    - 公式语法无效时捕获 `SympifyError`，记录日志并返回默认公式
    - _需求：5.1–5.9, 16.1–16.8_

  - [ ]* 5.2 编写属性测试：属性 6（价格聚合不变量）
    - **属性 6：价格聚合不变量**
    - **验证需求：5.3, 5.4, 5.5, 5.6**

  - [ ]* 5.3 编写属性测试：属性 7（后端价格计算权威性）
    - **属性 7：后端价格计算权威性**
    - **验证需求：5.8, 5.9**

  - [ ]* 5.4 编写属性测试：属性 8（价格公式解析往返）
    - **属性 8：价格公式解析往返**
    - **验证需求：16.8**

  - [ ]* 5.5 编写 PriceEngine 单元测试
    - 测试无效公式语法时使用默认公式（需求 16.5）
    - 测试边界值：数量为最小正数、单价为 0
    - _需求：16.4, 16.5_

  - [x] 5.6 实现 `POST /api/price-engine/calculate` 端点（后端价格验证）
    - _需求：5.8, 5.9_

  - [x] 5.7 实现 `GET /api/price-formulas` 端点
    - _需求：5.1, 16.1_

- [x] 6. 实现材料数据库搜索与附件推荐
  - [x] 6.1 实现 `app/services/material_service.py`
    - 实现 `search_materials(query, limit=20)` 模糊搜索（型号、名称、规格）
    - 实现 `get_accessories(material_id)` 查询关联附件
    - _需求：4.1–4.6, 11.1–11.7_

  - [ ]* 6.2 编写属性测试：属性 13（材料搜索结果数量限制）
    - **属性 13：材料搜索结果数量限制**
    - **验证需求：11.4**

  - [x] 6.3 实现 `GET /api/materials/search` 和 `GET /api/materials/{id}/accessories` 端点
    - _需求：4.1–4.3, 11.1–11.7_

- [x] 7. 实现乐观锁并发控制
  - [x] 7.1 在所有写操作服务方法中统一应用乐观锁逻辑
    - 封装 `optimistic_update(model, id, version, **fields)` 工具函数
    - 冲突时返回 409 并附带最新数据
    - _需求：19.1–19.6_

  - [ ]* 7.2 编写属性测试：属性 15（乐观锁并发冲突检测）
    - **属性 15：乐观锁并发冲突检测**
    - **验证需求：19.2, 19.3, 19.6**

- [x] 8. 实现权限控制
  - [ ]* 8.1 编写属性测试：属性 16（权限角色控制）
    - **属性 16：权限角色控制**
    - **验证需求：15.5, 15.6, 15.7, 15.8**

- [x] 9. 实现审计日志服务
  - [x] 9.1 实现 `app/services/audit_service.py`
    - 实现 `log_action(user_id, action, entity_type, entity_id, old_value, new_value, ip)` 方法
    - 在所有 CREATE/UPDATE/DELETE/EXPORT 操作的服务层调用审计记录
    - _需求：20.1–20.8_

  - [ ]* 9.2 编写属性测试：属性 17（审计日志完整性）
    - **属性 17：审计日志完整性**
    - **验证需求：20.1, 20.2, 20.3, 20.4, 20.5**

  - [x] 9.3 实现 `GET /api/audit-logs` 查询端点和 `GET /api/audit-logs/export` 导出端点
    - _需求：20.7, 20.8_

- [x] 10. 检查点 - 确保所有后端测试通过
  - 确保所有测试通过，如有问题请向用户反馈。

- [x] 11. 实现模板服务与 BOM 解析
  - [x] 11.1 实现 `app/services/template_service.py`
    - 实现 `save_as_template(node_id, node_type, name, description, user_id)` 将节点序列化为 JSON
    - 实现 `apply_template(template_id, target_project_id)` 反序列化并使用最新物料价格
    - _需求：8.1–8.7_

  - [ ]* 11.2 编写属性测试：属性 11（模板保存与应用往返）
    - **属性 11：模板保存与应用往返**
    - **验证需求：8.2, 8.5, 8.6**

  - [x] 11.3 实现 `app/services/bom_parser.py`
    - 使用 openpyxl 解析 BOM Excel 文件（型号、名称、数量、规格列）
    - 逐行与 Material_Database 匹配，匹配成功填充单价，失败标记为待确认
    - 格式无效时返回具体错误位置
    - _需求：9.1–9.8_

  - [ ]* 11.4 编写属性测试：属性 12（BOM 解析匹配正确性）
    - **属性 12：BOM 解析匹配正确性**
    - **验证需求：9.3, 9.4, 9.5**

  - [x] 11.5 实现模板和 BOM 相关 API 端点（`/api/templates/*`, `/api/bom/*`）
    - _需求：8.1–8.7, 9.1–9.8_

- [x] 12. 实现报表生成服务
  - [x] 12.1 实现 `app/services/report_service.py` - Excel 核价单生成
    - 使用 openpyxl 生成包含完整层级数据的 Excel 文件
    - 将 Price_Formula 写入 Excel 公式单元格，层级缩进展示树状结构
    - 包含折扣率、损耗率、辅材费、人工费、税金参数
    - _需求：6.1–6.7_

  - [ ]* 12.2 编写属性测试：属性 9（Excel 核价单内容完整性）
    - **属性 9：Excel 核价单内容完整性**
    - **验证需求：6.2, 6.3, 6.4, 6.5**

  - [ ]* 12.3 编写属性测试：属性 10（数据导出导入往返）
    - **属性 10：数据导出导入往返**
    - **验证需求：17.3, 17.4, 17.5**

  - [x] 12.4 实现 PDF 客户报价单生成
    - 使用 ReportLab 生成 PDF，包含项目名称、客户、日期、Cabinet 汇总价格
    - 隐藏成本明细，每页添加公司水印，支持中文字体
    - _需求：7.1–7.7_

  - [x] 12.5 实现报表 API 端点（`POST /api/reports/internal-pricing/{id}`, `POST /api/reports/customer-quotation/{id}`, `GET /api/reports/download/{token}`）
    - _需求：6.7, 7.7_

- [x] 13. 检查点 - 确保所有后端测试通过
  - 确保所有测试通过，如有问题请向用户反馈。

- [x] 14. 实现前端基础架构
  - 初始化 Vue 3 + TypeScript + Vite 项目，安装 Element Plus、Pinia、Axios
  - 配置 Axios 拦截器（自动注入 JWT、处理 401 自动跳转登录页）
  - 实现 `src/stores/auth.ts`（登录、登出、令牌刷新）
  - 实现登录页面 `LoginView.vue` 和路由守卫
  - _需求：15.1–15.4_

- [x] 15. 实现项目树与主布局
  - [x] 15.1 实现 `src/components/ProjectTree/` 组件
    - 使用 Element Plus `el-tree` 渲染四层树状结构
    - 支持节点展开/折叠、选中高亮（含所有子节点）
    - 实现右键菜单（复制 Cabinet、删除节点）
    - _需求：1.6, 1.7, 1.8_

  - [x] 15.2 实现 `src/stores/project.ts` Pinia store
    - 管理当前项目树状态、选中节点、价格聚合数据
    - _需求：1.6, 5.3–5.6_

  - [x] 15.3 实现 `ProjectList.vue` 和 `ProjectDetail.vue` 视图
    - _需求：1.1–1.8_

- [x] 16. 实现类 Excel 报价表格
  - [x] 16.1 实现 `src/components/QuotationTable/` 组件
    - 使用 Element Plus `el-table` 渲染 BaseComponent 列表（型号、名称、规格、数量、单价、折扣率、总价）
    - 实现单元格内联编辑，数量/单价变化时实时重新计算总价
    - 实现多选复选框，选中后显示批量操作工具栏（批量修改折扣率、批量删除）
    - _需求：5.3, 5.7, 10.6, 10.7, 12.1–12.7_

  - [x] 16.2 实现 `src/composables/useKeyboardNav.ts`
    - Enter 键移动到下一行同列，Tab 键移动到同行下一列，Shift+Tab 移动到上一列
    - Ctrl+C 复制选中单元格，Ctrl+V 粘贴
    - _需求：10.1–10.5_

  - [x] 16.3 实现 `src/composables/useOptimisticLock.ts`
    - 封装带 `version` 字段的更新请求，处理 409 冲突响应（显示冲突提示和最新值）
    - _需求：19.3, 19.4, 19.5_

- [x] 17. 实现材料搜索与附件推荐
  - [x] 17.1 实现 `src/components/MaterialSearch/` 下拉搜索组件
    - 使用 `src/composables/useDebounceSearch.ts` 实现 300ms 防抖
    - 搜索结果最多显示 20 条，展示型号、名称、规格、单价
    - 选中后自动填充 BaseComponent 所有字段
    - 无结果时显示"未找到匹配项"
    - _需求：11.1–11.7_

  - [x] 17.2 实现 `src/components/AccessoryPanel/` 附件推荐面板
    - 添加 BaseComponent 后自动查询关联附件并展示推荐列表
    - 支持一键添加附件到当前 StructureComponent，支持忽略推荐
    - 删除 BaseComponent 时提示是否同时删除关联附件
    - _需求：4.1–4.6_

- [x] 18. 实现 BOM 导入与模板库前端
  - [x] 18.1 实现 `src/components/BomImport/` 拖拽上传组件
    - 支持拖拽上传 Excel 文件，显示解析预览（匹配成功/待确认状态）
    - 用户确认后提交导入，格式无效时显示错误信息
    - _需求：9.1–9.8_

  - [x] 18.2 实现 `TemplateLibrary.vue` 模板库视图
    - 展示模板列表，支持搜索、应用、编辑、删除
    - _需求：8.3, 8.4, 8.7_

- [x] 19. 实现离线缓存与网络恢复
  - 实现 `src/composables/useOfflineCache.ts`
  - 使用 localStorage 缓存未保存修改，监听 `online` 事件触发同步提示
  - _需求：14.5, 14.6_

- [x] 20. 实现报表下载与管理员面板
  - 实现报表生成按钮（核价单 Excel、客户报价单 PDF）及下载链接
  - 实现 `AdminPanel.vue`（审计日志查询/导出、用户管理、价格公式配置）
  - _需求：6.1–6.7, 7.1–7.7, 20.8_

- [x] 21. 最终检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请向用户反馈。

- [x] 22. 扩展数据模型以支持新报价逻辑
  - [x] 22.1 更新 Cabinet 模型
    - 在 `backend/app/models/cabinet.py` 中添加字段：`control_category`, `cabinet_type`, `control_structure`, `quotation_mode`
    - 更新数据库迁移脚本
    - _新增业务逻辑：柜体分类体系、报价模式_

  - [x] 22.2 更新 StructureComponent 模型
    - 在 `backend/app/models/structure_component.py` 中添加字段：`circuit_type`
    - 更新数据库迁移脚本
    - _新增业务逻辑：非标柜按回路报价_

  - [x] 22.3 更新 BaseComponent 模型
    - 在 `backend/app/models/base_component.py` 中添加字段：`component_category`, `is_auto_matched`, `is_hidden`
    - 更新数据库迁移脚本
    - _新增业务逻辑：自动匹配、自动隐藏_

  - [x] 22.4 更新 Material 模型
    - 在 `backend/app/models/material.py` 中添加字段：`component_type`
    - 更新数据库迁移脚本
    - _新增业务逻辑：元器件分类_

  - [x] 22.5 创建 CabinetTypeConfig 模型
    - 创建 `backend/app/models/cabinet_type_config.py`
    - 定义字段：`control_category`, `cabinet_type`, `control_structure`, `description`, `is_active`
    - 添加唯一约束：(control_category, cabinet_type, control_structure)
    - _新增业务逻辑：柜体类型配置_

  - [x] 22.6 创建 AutoMatchRule 模型
    - 创建 `backend/app/models/auto_match_rule.py`
    - 定义字段：`cabinet_type_config_id`, `material_id`, `component_category`, `default_quantity`, `is_required`, `match_priority`
    - 建立与 CabinetTypeConfig 和 Material 的外键关系
    - _新增业务逻辑：自动匹配规则_

  - [x] 22.7 创建 LaborCostRule 模型
    - 创建 `backend/app/models/labor_cost_rule.py`
    - 定义字段：`cabinet_type_config_id`, `assembly_fee_rate`, `management_fee_rate`, `profit_rate`, `has_plc`, `programming_fee`, `debugging_fee`, `is_active`
    - 建立与 CabinetTypeConfig 的外键关系
    - _新增业务逻辑：人工费用规则_

  - [x] 22.8 更新数据库初始化脚本
    - 在 `backend/init_db.py` 中添加示例柜体类型配置数据
    - 添加示例自动匹配规则数据
    - 添加示例人工费用规则数据
    - 添加示例材料数据（包含 component_type）

- [x] 23. 实现自动匹配服务
  - [x] 23.1 创建 AutoMatchService
    - 创建 `backend/app/services/auto_match_service.py`
    - 实现 `apply_auto_match(cabinet)` 方法：根据柜体配置查询匹配规则并自动插入元器件
    - 实现 `get_cabinet_type_config(control_category, cabinet_type, control_structure)` 方法
    - 实现错误处理：配置不存在、规则缺失时的降级策略
    - _新增业务逻辑：自动匹配规则_

  - [x] 23.2 实现自动隐藏规则
    - 在 AutoMatchService 中实现 `apply_auto_hide_rules(cabinet)` 方法
    - 当 control_structure='非标控制' 时，隐藏 PLC 相关元器件
    - _新增业务逻辑：自动隐藏机制_

  - [ ]* 23.3 编写属性测试：属性 20（快速报价模式自动匹配完整性）
    - **属性 20：快速报价模式自动匹配完整性**
    - **验证需求：新增业务逻辑 - 自动匹配规则**

  - [ ]* 23.4 编写属性测试：属性 21（自动隐藏规则正确性）
    - **属性 21：自动隐藏规则正确性**
    - **验证需求：新增业务逻辑 - 自动隐藏机制**

  - [ ]* 23.5 编写属性测试：属性 24（报价模式一致性）
    - **属性 24：报价模式一致性**
    - **验证需求：新增业务逻辑 - 报价模式**

- [x] 24. 实现人工费用计算服务
  - [x] 24.1 创建 LaborCostService
    - 创建 `backend/app/services/labor_cost_service.py`
    - 实现 `calculate_labor_cost(cabinet, base_cost)` 方法
    - 实现 `check_cabinet_has_plc(cabinet)` 方法：检查控制结构或元器件中是否包含 PLC
    - 实现 `get_labor_cost_rule(cabinet)` 方法：查询人工费用规则
    - 实现错误处理和降级策略（使用默认费率）
    - _新增业务逻辑：人工费用联动计算_

  - [ ]* 24.2 编写属性测试：属性 22（人工费用计算正确性）
    - **属性 22：人工费用计算正确性**
    - **验证需求：新增业务逻辑 - 人工费用联动计算**

  - [ ]* 24.3 编写属性测试：属性 25（回路类型非标柜应用）
    - **属性 25：回路类型非标柜应用**
    - **验证需求：新增业务逻辑 - 非标柜报价原则**

- [x] 25. 扩展 API 接口
  - [x] 25.1 创建柜体配置 API
    - 创建 `backend/app/api/cabinet_configs.py` 蓝图
    - 实现 `GET /api/cabinet-type-configs`：获取柜体类型配置列表
    - 实现 `GET /api/cabinet-type-configs/{id}/auto-match-rules`：获取自动匹配规则
    - 实现 `POST /api/cabinet-type-configs`：创建柜体配置（管理员）
    - 实现 `PUT /api/cabinet-type-configs/{id}`：更新柜体配置（管理员）
    - _新增业务逻辑：柜体分类体系_

  - [x] 25.2 扩展 Cabinet API
    - 在 `backend/app/api/cabinets.py` 中添加端点：
    - `POST /api/cabinets/{id}/auto-match`：触发自动匹配
    - `POST /api/cabinets/{id}/apply-hide-rules`：应用自动隐藏规则
    - 更新 `POST /api/cabinets` 端点：支持新字段（control_category, cabinet_type, control_structure, quotation_mode）
    - _新增业务逻辑：自动匹配、自动隐藏_

  - [x] 25.3 扩展价格引擎 API
    - 在 `backend/app/api/materials.py` 或创建新端点
    - 实现 `POST /api/price-engine/calculate-labor`：计算人工费用
    - 支持按柜体配置和基础成本计算
    - _新增业务逻辑：人工费用联动计算_

  - [x] 25.4 扩展材料搜索 API
    - 更新 `GET /api/materials/search` 端点：支持 `category` 参数过滤
    - _新增业务逻辑：按分类搜索_

- [x] 26. 实现前端柜体类型选择器
  - [x] 26.1 创建 CabinetTypeSelector 组件
    - 创建 `frontend/src/components/CabinetTypeSelector/index.vue`
    - 实现三级联动选择：控制大类 → 柜体类型 → 控制结构
    - 使用 Element Plus 级联选择器或分步选择
    - 实时显示选择结果
    - _新增业务逻辑：柜体分类体系_

  - [x] 26.2 创建 QuotationModeSelector 组件
    - 创建 `frontend/src/components/QuotationModeSelector/index.vue`
    - 提供两种模式选择：详细逐项报价 / 快速报价
    - 显示每种模式的说明和适用场景
    - _新增业务逻辑：报价模式_

  - [x] 26.3 创建 CircuitTypeSelector 组件
    - 创建 `frontend/src/components/CircuitTypeSelector/index.vue`
    - 提供回路类型选择：电机回路、变频回路、三角降压回路等
    - 用于非标柜的结构组件
    - _新增业务逻辑：非标柜按回路报价_

- [x] 27. 实现前端状态管理
  - [x] 27.1 创建 cabinetConfig store
    - 创建 `frontend/src/stores/cabinetConfig.ts`
    - 管理柜体类型配置列表
    - 管理自动匹配规则
    - 提供查询和缓存功能
    - _新增业务逻辑：柜体配置状态管理_

  - [x] 27.2 创建 useAutoMatch composable
    - 创建 `frontend/src/composables/useAutoMatch.ts`
    - 封装自动匹配逻辑
    - 处理匹配结果和错误
    - _新增业务逻辑：自动匹配逻辑_

- [x] 28. 更新前端创建配电柜流程
  - [x] 28.1 更新 ProjectDetail.vue
    - 在创建配电柜对话框中集成 CabinetTypeSelector
    - 在创建配电柜对话框中集成 QuotationModeSelector
    - 根据选择的报价模式决定是否触发自动匹配
    - _新增业务逻辑：柜体分类、报价模式_

  - [x] 28.2 更新 QuotationTable 组件
    - 支持显示 component_category 列
    - 支持过滤 is_hidden=true 的元器件
    - 显示 is_auto_matched 标记（可选）
    - _新增业务逻辑：自动匹配、自动隐藏_

  - [x] 28.3 更新结构组件创建流程
    - 当 control_structure='非标控制' 时，显示 CircuitTypeSelector
    - 要求用户选择回路类型
    - _新增业务逻辑：非标柜按回路报价_

- [x] 29. 实现人工费用显示
  - [x] 29.1 在 ProjectDetail 中显示人工费用
    - 在项目总价旁边显示人工费用明细
    - 显示：组装费、管理费、利润、编程费、调试费
    - 实时更新（当元器件总价变化时）
    - _新增业务逻辑：人工费用联动计算_

  - [x] 29.2 在报表中包含人工费用
    - 更新 Excel 核价单生成逻辑，包含人工费用明细
    - 更新 PDF 客户报价单，包含人工费用（可选显示明细）
    - _新增业务逻辑：人工费用联动计算_

- [-] 30. 测试与验证
  - [ ]* 30.1 编写属性测试：属性 23（柜体类型配置唯一性）
    - **属性 23：柜体类型配置唯一性**
    - **验证需求：新增业务逻辑 - 柜体分类体系**

  - [x] 30.2 集成测试：完整报价流程
    - 测试快速报价模式：创建柜体 → 自动匹配 → 微调 → 生成报价
    - 测试详细报价模式：创建柜体 → 手动添加元器件 → 生成报价
    - 测试非标柜报价：创建非标柜 → 按回路添加元器件 → 验证自动隐藏 → 生成报价
    - 测试人工费用计算：验证包含/不包含 PLC 时的费用差异

  - [-] 30.3 用户验收测试
    - 准备测试数据：多种柜体类型配置、自动匹配规则、人工费用规则
    - 邀请用户测试完整报价流程
    - 收集反馈并优化

- [-] 31. 最终检查点 - 新功能验证
  - 确保所有新功能正常工作
  - 确保向后兼容性（现有项目不受影响）
  - 确保性能满足要求

## 备注

- 标有 `*` 的子任务为可选项，可跳过以加快 MVP 交付
- 每个任务均引用具体需求条款以确保可追溯性
- 属性测试使用 Python Hypothesis（后端）和 fast-check（前端），每个属性最少运行 100 次迭代
- 每个属性测试注释格式：`# Feature: electrical-equipment-quotation-system, Property {N}: {property_text}`
- 检查点确保增量验证，避免问题积累
