# 技术设计文档 - 电气设备报价系统

## 概述

电气设备报价系统是一个面向电气设备制造行业的 B/S 架构报价管理平台。系统采用前后端分离架构，前端基于 Vue 3 + Element Plus 提供类 Excel 的交互体验，后端基于 Python Flask 提供 RESTful API，数据持久化使用 SQL Server，通过 Nginx + Waitress 部署。

核心设计目标：
- 支持"项目→配电柜→结构组件→基础元器件"四层树状数据模型
- 柜体分类体系：控制大类（低压/配电/控制/自控）→ 柜体类型 → 控制结构
- 双模式报价：详细逐项报价（手动）+ 快速报价（自动匹配）
- 智能自动匹配：根据柜体类型自动插入标准元器件
- 自动隐藏机制：根据控制类型隐藏不相关元器件
- 智能材料匹配与附件自动推荐
- 人工费用联动计算：根据柜体配置自动计算组装费、管理费、利润、编程调试费
- 基于 SymPy 的动态报价公式解析与计算
- 多格式报表生成（Excel 核价单 + PDF 客户报价单）
- 乐观锁并发控制与完整审计日志

---

## 架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端浏览器                           │
│              Vue 3 + Element Plus + Pinia                    │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│   │ 项目树   │ │ 报价表格 │ │ 报表生成 │ │ 模板/BOM导入 │  │
│   └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS / REST API
┌─────────────────────────▼───────────────────────────────────┐
│                    Nginx 反向代理                             │
│              静态资源服务 + SSL 终止                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Waitress WSGI 服务器                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Flask 应用                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │   │
│  │  │ 项目API  │ │ 材料API  │ │ 报表API  │ │ 认证API│  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │              服务层                           │    │   │
│  │  │  ProjectService │ PriceEngine │ ReportService │    │   │
│  │  │  MaterialService│ TemplateService│ AuditService│   │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ pyodbc / SQLAlchemy
┌─────────────────────────▼───────────────────────────────────┐
│                    SQL Server 数据库                          │
│   Projects │ Cabinets │ StructureComponents │ BaseComponents │
│   Materials │ PriceFormulas │ Templates │ Users │ AuditLogs  │
└─────────────────────────────────────────────────────────────┘
```

### 技术选型

| 层次 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 (Composition API) | 响应式状态管理，组合式逻辑复用 |
| UI 组件库 | Element Plus | 表格、树形、表单组件 |
| 状态管理 | Pinia | 轻量级，TypeScript 友好 |
| HTTP 客户端 | Axios | 请求拦截、JWT 注入 |
| 后端框架 | Flask 3.x | 轻量 RESTful，蓝图模块化 |
| 公式解析 | SymPy | 符号数学，安全解析字符串公式 |
| Excel 生成 | openpyxl | 支持公式写入 |
| PDF 生成 | ReportLab | 水印、中文字体支持 |
| ORM | SQLAlchemy 2.x | 声明式模型，事务管理 |
| 数据库 | SQL Server 2019+ | 企业级事务，行版本并发控制 |
| 认证 | PyJWT | JWT 令牌，角色声明 |
| 部署 | Nginx + Waitress | Windows 友好的 WSGI 服务器 |

---

## 业务流程

### 快速报价流程

```
用户创建配电柜
    ↓
选择报价模式：快速报价
    ↓
选择控制大类（低压类/配电类/控制类/自控类）
    ↓
选择柜体类型（配电箱柜/控制箱柜/低压进线柜等）
    ↓
选择控制结构（非标控制/自控型/纯PLC型/MCC柜/抽屉柜）
    ↓
系统查询 CabinetTypeConfigs 获取配置ID
    ↓
系统查询 AutoMatchRules 获取匹配规则
    ↓
系统自动插入标准元器件
    ├── 一次元器件（断路器、接触器等）
    ├── 二次元器件（按钮、指示灯、端子等）
    ├── PLC及模块（根据控制结构）
    ├── 触摸屏（根据控制结构）
    └── 电源（根据控制结构）
    ↓
应用自动隐藏规则（如果是非标控制）
    ↓
用户微调数量或补充特殊元件
    ↓
系统计算人工费用
    ├── 组装费 = 基础成本 × 组装费率
    ├── 管理费 = 基础成本 × 管理费率
    ├── 利润 = 基础成本 × 利润率
    └── 编程调试费（如果包含PLC）
    ↓
生成报价
```

### 详细报价流程

```
用户创建配电柜
    ↓
选择报价模式：详细逐项报价
    ↓
选择控制大类、柜体类型、控制结构
    ↓
用户手动搜索并添加元器件
    ↓
系统推荐配套附件（可选）
    ↓
用户配置数量和规格
    ↓
系统计算人工费用
    ↓
生成报价
```

### 非标柜报价流程

```
用户创建配电柜
    ↓
选择控制结构：非标控制
    ↓
创建结构组件（按回路）
    ├── 电机回路1
    ├── 变频回路1
    ├── 照明回路
    └── ...
    ↓
为每个回路添加元器件
    ↓
系统应用自动隐藏规则
    （隐藏PLC、触摸屏等不相关元器件）
    ↓
系统计算人工费用
    （不包含编程调试费）
    ↓
生成报价
```

### 人工费用联动触发时机

```
触发条件：
1. 创建配电柜时
2. 修改控制结构时
3. 添加/删除PLC元器件时
4. 元器件总价变化时

处理流程：
    ↓
检查柜体是否包含PLC
    ├── 方法1：控制结构为'自控型'或'纯PLC型'
    └── 方法2：存在component_category='PLC及模块'的元器件
    ↓
查询人工费用规则
    ↓
计算基础人工费用（按比例）
    ├── 组装费
    ├── 管理费
    └── 利润
    ↓
计算编程调试费用（固定金额，仅当包含PLC）
    ├── 编程费
    └── 调试费
    ↓
更新柜体总价
```

---

## 组件与接口

### 后端模块结构

```
backend/
├── app/
│   ├── __init__.py          # Flask 工厂函数
│   ├── extensions.py        # SQLAlchemy, JWT 扩展初始化
│   ├── models/              # SQLAlchemy 数据模型
│   │   ├── project.py
│   │   ├── cabinet.py
│   │   ├── structure_component.py
│   │   ├── base_component.py
│   │   ├── material.py
│   │   ├── price_formula.py
│   │   ├── cabinet_type_config.py      # 新增：柜体类型配置
│   │   ├── auto_match_rule.py          # 新增：自动匹配规则
│   │   ├── labor_cost_rule.py          # 新增：人工费用规则
│   │   ├── template.py
│   │   ├── user.py
│   │   └── audit_log.py
│   ├── api/                 # Flask 蓝图路由
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── cabinets.py
│   │   ├── components.py
│   │   ├── materials.py
│   │   ├── reports.py
│   │   ├── templates.py
│   │   └── cabinet_configs.py          # 新增：柜体配置API
│   ├── services/            # 业务逻辑层
│   │   ├── price_engine.py  # SymPy 公式解析与计算
│   │   ├── auto_match_service.py       # 新增：自动匹配服务
│   │   ├── labor_cost_service.py       # 新增：人工费用计算服务
│   │   ├── report_service.py
│   │   ├── material_service.py
│   │   ├── template_service.py
│   │   └── audit_service.py
│   └── utils/
│       ├── decorators.py    # 权限装饰器
│       └── validators.py
├── config.py
└── run.py
```

### 前端模块结构

```
frontend/
├── src/
│   ├── api/                 # Axios 接口封装
│   ├── components/
│   │   ├── ProjectTree/     # 项目树组件
│   │   ├── QuotationTable/  # 类 Excel 报价表格
│   │   ├── MaterialSearch/  # 物料搜索下拉
│   │   ├── AccessoryPanel/  # 附件推荐面板
│   │   ├── BomImport/       # BOM 拖拽上传
│   │   ├── CabinetTypeSelector/  # 新增：柜体类型选择器
│   │   └── QuotationModeSelector/ # 新增：报价模式选择器
│   ├── views/
│   │   ├── ProjectList.vue
│   │   ├── ProjectDetail.vue
│   │   ├── TemplateLibrary.vue
│   │   └── AdminPanel.vue
│   ├── stores/              # Pinia stores
│   │   ├── project.ts
│   │   ├── auth.ts
│   │   ├── material.ts
│   │   └── cabinetConfig.ts      # 新增：柜体配置状态
│   └── composables/
│       ├── useKeyboardNav.ts  # Excel 快捷键逻辑
│       ├── useDebounceSearch.ts
│       ├── useOptimisticLock.ts
│       └── useAutoMatch.ts        # 新增：自动匹配逻辑
```

### 关键 API 接口

#### 认证

```
POST   /api/auth/login          # 登录，返回 JWT
POST   /api/auth/refresh        # 刷新令牌
POST   /api/auth/logout         # 登出
```

#### 项目管理

```
GET    /api/projects                    # 项目列表
POST   /api/projects                    # 创建项目
GET    /api/projects/{id}/tree          # 获取完整树结构
PUT    /api/projects/{id}               # 更新项目
DELETE /api/projects/{id}               # 删除项目（级联）

GET    /api/cabinet-type-configs        # 获取柜体类型配置列表
GET    /api/cabinet-type-configs/{id}/auto-match-rules  # 获取自动匹配规则

POST   /api/cabinets                    # 创建配电柜
POST   /api/cabinets/{id}/copy          # 复制配电柜
POST   /api/cabinets/{id}/auto-match    # 触发自动匹配（快速报价模式）
POST   /api/cabinets/{id}/apply-hide-rules  # 应用自动隐藏规则
PUT    /api/cabinets/{id}/move          # 跨项目移动
DELETE /api/cabinets/{id}

POST   /api/structure-components
PUT    /api/structure-components/{id}
DELETE /api/structure-components/{id}

POST   /api/base-components
PUT    /api/base-components/{id}
DELETE /api/base-components/{id}
POST   /api/base-components/batch       # 批量操作
```

#### 材料与公式

```
GET    /api/materials/search?q=&limit=20&category=  # 模糊搜索（支持按分类过滤）
GET    /api/materials/{id}/accessories     # 获取关联附件
GET    /api/price-formulas                 # 获取公式配置
POST   /api/price-engine/calculate         # 后端价格验证
POST   /api/price-engine/calculate-labor   # 计算人工费用（根据柜体配置）
```

#### 报表

```
POST   /api/reports/internal-pricing/{project_id}   # 生成 Excel 核价单
POST   /api/reports/customer-quotation/{project_id} # 生成 PDF 报价单
GET    /api/reports/download/{token}                # 下载文件
```

#### 模板与 BOM

```
GET    /api/templates                  # 模板库列表
POST   /api/templates                  # 保存为模板
POST   /api/templates/{id}/apply       # 应用模板
DELETE /api/templates/{id}

POST   /api/bom/upload                 # 上传 BOM 文件
POST   /api/bom/import                 # 确认导入
```

#### 审计日志

```
GET    /api/audit-logs?start=&end=&user=   # 查询日志
GET    /api/audit-logs/export              # 导出日志
```

---

## 数据模型

### ER 图（文本形式）

```
Projects
├── id              INT PK IDENTITY
├── name            NVARCHAR(200) NOT NULL
├── customer        NVARCHAR(200)
├── project_date    DATE
├── notes           NVARCHAR(MAX)
├── created_by      INT FK → Users.id
├── version         INT DEFAULT 1          -- 乐观锁
├── created_at      DATETIME2
└── updated_at      DATETIME2

Cabinets
├── id              INT PK IDENTITY
├── project_id      INT FK → Projects.id (CASCADE DELETE)
├── name            NVARCHAR(200) NOT NULL
├── control_category NVARCHAR(50)          -- 控制大类：低压类/配电类/控制类/自控类
├── cabinet_type    NVARCHAR(100)          -- 柜体类型：配电箱柜/控制箱柜/低压进线柜等
├── control_structure NVARCHAR(100)        -- 控制结构：非标控制/自控型/纯PLC型/MCC柜/抽屉柜
├── quotation_mode  NVARCHAR(50)           -- 报价模式：detailed/quick
├── sort_order      INT DEFAULT 0
├── version         INT DEFAULT 1
├── created_at      DATETIME2
└── updated_at      DATETIME2

StructureComponents
├── id              INT PK IDENTITY
├── cabinet_id      INT FK → Cabinets.id (CASCADE DELETE)
├── name            NVARCHAR(200) NOT NULL
├── circuit_type    NVARCHAR(100)          -- 回路类型：电机回路/变频回路/三角降压等（非标柜使用）
├── sort_order      INT DEFAULT 0
├── version         INT DEFAULT 1
├── created_at      DATETIME2
└── updated_at      DATETIME2

BaseComponents
├── id              INT PK IDENTITY
├── structure_component_id  INT FK → StructureComponents.id (CASCADE DELETE)
├── material_id     INT FK → Materials.id (NULLABLE)
├── component_category NVARCHAR(100)       -- 元器件分类：一次元器件/二次元器件/PLC及模块/触摸屏/电源/端子等
├── model_number    NVARCHAR(200)
├── name            NVARCHAR(200)
├── specification   NVARCHAR(500)
├── quantity        DECIMAL(18,4) NOT NULL CHECK (quantity > 0)
├── unit_price      DECIMAL(18,4) NOT NULL CHECK (unit_price >= 0)
├── discount_rate   DECIMAL(5,4) DEFAULT 1.0
├── total_price     AS (quantity * unit_price * discount_rate) PERSISTED
├── is_auto_matched BIT DEFAULT 0          -- 是否为自动匹配的元器件
├── is_hidden       BIT DEFAULT 0          -- 是否被自动隐藏（根据控制类型）
├── sort_order      INT DEFAULT 0
├── version         INT DEFAULT 1
├── created_at      DATETIME2
└── updated_at      DATETIME2

Materials
├── id              INT PK IDENTITY
├── model_number    NVARCHAR(200) NOT NULL
├── name            NVARCHAR(200) NOT NULL
├── specification   NVARCHAR(500)
├── unit_price      DECIMAL(18,4)
├── category        NVARCHAR(100)          -- 元器件分类
├── component_type  NVARCHAR(100)          -- 元器件类型：一次/二次/PLC/触摸屏/电源/端子等
├── is_active       BIT DEFAULT 1
├── created_at      DATETIME2
└── updated_at      DATETIME2

MaterialAccessories
├── id              INT PK IDENTITY
├── material_id     INT FK → Materials.id
├── accessory_id    INT FK → Materials.id
├── is_required     BIT DEFAULT 0
└── default_quantity DECIMAL(18,4) DEFAULT 1

CabinetTypeConfigs
├── id              INT PK IDENTITY
├── control_category NVARCHAR(50) NOT NULL  -- 控制大类
├── cabinet_type    NVARCHAR(100) NOT NULL  -- 柜体类型
├── control_structure NVARCHAR(100) NOT NULL -- 控制结构
├── description     NVARCHAR(MAX)
├── is_active       BIT DEFAULT 1
├── created_at      DATETIME2
└── updated_at      DATETIME2

AutoMatchRules
├── id              INT PK IDENTITY
├── cabinet_type_config_id INT FK → CabinetTypeConfigs.id
├── material_id     INT FK → Materials.id
├── component_category NVARCHAR(100) NOT NULL -- 元器件分类
├── default_quantity DECIMAL(18,4) DEFAULT 1
├── is_required     BIT DEFAULT 1            -- 是否必选
├── match_priority  INT DEFAULT 0            -- 匹配优先级
├── created_at      DATETIME2
└── updated_at      DATETIME2

LaborCostRules
├── id              INT PK IDENTITY
├── cabinet_type_config_id INT FK → CabinetTypeConfigs.id
├── assembly_fee_rate DECIMAL(5,4)          -- 组装费率
├── management_fee_rate DECIMAL(5,4)        -- 管理费率
├── profit_rate     DECIMAL(5,4)            -- 利润率
├── has_plc         BIT DEFAULT 0           -- 是否包含PLC
├── programming_fee DECIMAL(18,4)           -- 编程费用
├── debugging_fee   DECIMAL(18,4)           -- 调试费用
├── is_active       BIT DEFAULT 1
├── created_at      DATETIME2
└── updated_at      DATETIME2

PriceFormulas
├── id              INT PK IDENTITY
├── name            NVARCHAR(100) NOT NULL
├── formula_str     NVARCHAR(MAX) NOT NULL   -- SymPy 表达式字符串
├── variables       NVARCHAR(MAX)            -- JSON: 变量说明
├── is_default      BIT DEFAULT 0
├── is_active       BIT DEFAULT 1
├── created_at      DATETIME2
└── updated_at      DATETIME2

Templates
├── id              INT PK IDENTITY
├── name            NVARCHAR(200) NOT NULL
├── description     NVARCHAR(MAX)
├── source_type     NVARCHAR(50)             -- 'cabinet' | 'structure_component'
├── template_data   NVARCHAR(MAX) NOT NULL   -- JSON 序列化的完整配置
├── created_by      INT FK → Users.id
├── created_at      DATETIME2
└── updated_at      DATETIME2

Users
├── id              INT PK IDENTITY
├── username        NVARCHAR(100) NOT NULL UNIQUE
├── password_hash   NVARCHAR(256) NOT NULL
├── display_name    NVARCHAR(200)
├── role            NVARCHAR(20) NOT NULL    -- 'viewer' | 'editor' | 'admin'
├── is_active       BIT DEFAULT 1
├── created_at      DATETIME2
└── last_login_at   DATETIME2

AuditLogs
├── id              BIGINT PK IDENTITY
├── user_id         INT FK → Users.id
├── action          NVARCHAR(50) NOT NULL    -- 'CREATE'|'UPDATE'|'DELETE'|'EXPORT'
├── entity_type     NVARCHAR(100) NOT NULL
├── entity_id       INT
├── old_value       NVARCHAR(MAX)            -- JSON
├── new_value       NVARCHAR(MAX)            -- JSON
├── ip_address      NVARCHAR(50)
└── created_at      DATETIME2
```

### 关键关系

```
Projects (1) ──── (N) Cabinets
Cabinets (1) ──── (N) StructureComponents
StructureComponents (1) ──── (N) BaseComponents
Materials (1) ──── (N) BaseComponents
Materials (N) ──── (N) Materials  [通过 MaterialAccessories]
CabinetTypeConfigs (1) ──── (N) AutoMatchRules
CabinetTypeConfigs (1) ──── (N) LaborCostRules
Users (1) ──── (N) Projects
Users (1) ──── (N) Templates
Users (1) ──── (N) AuditLogs
```

### 柜体分类体系

系统支持三级分类体系来精确定义配电柜类型：

1. **控制大类（control_category）**：
   - 低压类
   - 配电类
   - 控制类
   - 自控类

2. **柜体类型（cabinet_type）**：
   - 配电箱/柜
   - 控制箱/柜
   - 低压进线柜/出线柜
   - 低压补偿柜
   - 低压控制柜

3. **控制结构（control_structure）**：
   - 非标控制（不带PLC）
   - 自控型（带PLC+控制回路）
   - 纯PLC型（带PLC，不含控制回路）
   - MCC柜（GGD）
   - 抽屉柜（MNS/GCK）

这三个维度的组合决定了柜体的自动匹配规则和人工费用计算方式。

### 价格计算模型

```
BaseComponent.total_price = quantity × unit_price × discount_rate

StructureComponent.total_price = Σ BaseComponent.total_price

Cabinet.total_price = Σ StructureComponent.total_price

Project.total_price = Σ Cabinet.total_price

最终报价 = PriceFormula(
    base_cost = Project.total_price,
    loss_rate,       -- 损耗率
    aux_material_fee,-- 辅材费
    labor_fee,       -- 人工费（组装费+管理费+利润）
    tax_rate         -- 税率
)

人工费计算（根据柜体配置）：
labor_fee = base_cost × (assembly_fee_rate + management_fee_rate + profit_rate)
           + (has_plc ? programming_fee + debugging_fee : 0)
```

### 报价模式

系统支持两种报价模式，在创建配电柜时选择：

#### 模式一：详细逐项报价（detailed）

- 适用场景：复杂或非标项目
- 工作流程：
  1. 选择控制大类、柜体类型、控制结构
  2. 手动选择所有元器件（不自动匹配）
  3. 逐项配置数量和规格
  4. 系统提供附件推荐但不自动添加
- 特点：完全手动控制，灵活度高

#### 模式二：快速报价（quick）

- 适用场景：标准或常规项目
- 工作流程：
  1. 选择控制大类、柜体类型、控制结构
  2. 系统根据 AutoMatchRules 自动匹配标准元器件
  3. 自动插入典型二次元件（按钮、指示灯、端子等）
  4. 人工微调数量或补充特殊元件
- 特点：快速高效，减少遗漏

### 自动匹配规则

当用户选择快速报价模式时，系统根据以下规则自动匹配元器件：

1. **查询匹配规则**：
   ```sql
   SELECT m.*, amr.default_quantity, amr.component_category
   FROM AutoMatchRules amr
   JOIN Materials m ON amr.material_id = m.id
   WHERE amr.cabinet_type_config_id = (
       SELECT id FROM CabinetTypeConfigs
       WHERE control_category = :control_category
         AND cabinet_type = :cabinet_type
         AND control_structure = :control_structure
   )
   ORDER BY amr.match_priority DESC
   ```

2. **元器件分类自动插入**：
   - 一次元器件：根据柜体类型匹配（断路器、接触器等）
   - 二次元器件：自动插入典型元件（按钮、指示灯、转换开关、蜂鸣器、端子排、继电器、小型开关）
   - PLC及模块：根据控制结构决定是否插入
   - 触摸屏：根据控制结构决定是否插入
   - 电源：根据控制结构决定是否插入
   - 端子：自动插入标准端子排

3. **数量计算**：
   - 使用 AutoMatchRules.default_quantity 作为初始数量
   - 用户可手动调整

### 自动隐藏机制

系统根据控制类型自动隐藏不相关的元器件类别，避免界面混乱：

**隐藏规则**：

当 `control_structure = '非标控制'` 时，自动隐藏：
- PLC及模块
- 开关电源（用于PLC供电）
- 信号隔离器
- 触摸屏
- 编程调试费用

实现方式：
```python
def apply_auto_hide_rules(cabinet):
    if cabinet.control_structure == '非标控制':
        hidden_categories = ['PLC及模块', '开关电源', '信号隔离器', '触摸屏']
        BaseComponent.query.filter(
            BaseComponent.cabinet_id == cabinet.id,
            BaseComponent.component_category.in_(hidden_categories)
        ).update({'is_hidden': True})
```

前端渲染时过滤 `is_hidden = True` 的元器件。

### 人工费用联动计算

系统根据柜体配置自动计算人工费用，包括组装费、管理费、利润和编程调试费。

**计算逻辑**：

```python
def calculate_labor_cost(cabinet, base_cost):
    """
    计算人工费用
    
    Args:
        cabinet: Cabinet 对象
        base_cost: 基础成本（元器件总价）
    
    Returns:
        dict: {
            'assembly_fee': 组装费,
            'management_fee': 管理费,
            'profit': 利润,
            'programming_fee': 编程费,
            'debugging_fee': 调试费,
            'total_labor_cost': 总人工费用
        }
    """
    # 查询人工费用规则
    rule = LaborCostRules.query.join(CabinetTypeConfigs).filter(
        CabinetTypeConfigs.control_category == cabinet.control_category,
        CabinetTypeConfigs.cabinet_type == cabinet.cabinet_type,
        CabinetTypeConfigs.control_structure == cabinet.control_structure,
        LaborCostRules.is_active == True
    ).first()
    
    if not rule:
        # 使用默认费率
        rule = get_default_labor_cost_rule()
    
    # 基础人工费用（按比例）
    assembly_fee = base_cost * rule.assembly_fee_rate
    management_fee = base_cost * rule.management_fee_rate
    profit = base_cost * rule.profit_rate
    
    # 编程调试费用（固定金额，仅当包含PLC时）
    has_plc = check_cabinet_has_plc(cabinet)
    programming_fee = rule.programming_fee if has_plc else 0
    debugging_fee = rule.debugging_fee if has_plc else 0
    
    total_labor_cost = (assembly_fee + management_fee + profit + 
                       programming_fee + debugging_fee)
    
    return {
        'assembly_fee': assembly_fee,
        'management_fee': management_fee,
        'profit': profit,
        'programming_fee': programming_fee,
        'debugging_fee': debugging_fee,
        'total_labor_cost': total_labor_cost
    }

def check_cabinet_has_plc(cabinet):
    """检查柜体是否包含PLC"""
    # 方法1：根据控制结构判断
    if cabinet.control_structure in ['自控型', '纯PLC型']:
        return True
    
    # 方法2：检查是否有PLC类元器件
    plc_count = BaseComponent.query.filter(
        BaseComponent.cabinet_id == cabinet.id,
        BaseComponent.component_category == 'PLC及模块',
        BaseComponent.is_hidden == False
    ).count()
    
    return plc_count > 0
```

**联动触发时机**：

1. 创建配电柜时，根据控制结构初始化人工费用规则
2. 修改控制结构时，重新计算人工费用
3. 添加/删除PLC元器件时，更新编程调试费用
4. 元器件总价变化时，重新计算基于比例的人工费用

### 非标柜报价原则

对于非标准配电柜，系统采用按回路拆分的方式进行报价，而不是直接按柜型报价。

**实现方式**：

1. **回路类型定义**：
   - 电机回路
   - 变频回路
   - 三角降压回路
   - 星三角启动回路
   - 软启动回路
   - 照明回路
   - 插座回路
   - 其他自定义回路

2. **回路级报价**：
   - 在 StructureComponent 中增加 `circuit_type` 字段
   - 每个回路作为一个 StructureComponent
   - 回路内包含该回路所需的所有元器件

3. **优势**：
   - 更灵活，符合实际设计
   - 避免漏项
   - 便于复用标准回路配置
   - 支持保存回路模板

**示例结构**：

```
非标控制柜
├── 电机回路1
│   ├── 断路器
│   ├── 接触器
│   ├── 热继电器
│   └── 按钮、指示灯
├── 变频回路1
│   ├── 断路器
│   ├── 变频器
│   ├── 电抗器
│   └── 操作面板
└── 照明回路
    ├── 断路器
    └── 照明开关
```

### 乐观锁机制

每条记录维护 `version` 字段。更新时：

```sql
UPDATE Projects
SET name = :name, version = version + 1, updated_at = GETDATE()
WHERE id = :id AND version = :expected_version
```

若影响行数为 0，则表示并发冲突，返回 409 Conflict。

---

## 正确性属性

*属性（Property）是在系统所有有效执行中都应成立的特征或行为——本质上是对系统应做什么的形式化陈述。属性是人类可读规范与机器可验证正确性保证之间的桥梁。*


### 属性 1：创建操作生成唯一标识符

*对任意* 数量的 Project/Cabinet/StructureComponent/BaseComponent 创建操作，每次创建返回的 `id` 在同类实体中均不重复。

**验证需求：1.2, 2.2**

### 属性 2：层级关联完整性

*对任意* Cabinet，其 `project_id` 必须指向一个存在的 Project；对任意 StructureComponent，其 `cabinet_id` 必须指向一个存在的 Cabinet；对任意 BaseComponent，其 `structure_component_id` 必须指向一个存在的 StructureComponent。

**验证需求：18.2, 18.3, 18.4**

### 属性 3：Cabinet 复制完整性

*对任意* Cabinet（包含任意数量的 StructureComponent 和 BaseComponent），执行复制操作后，新 Cabinet 的子节点数量和配置数据应与原 Cabinet 完全一致，且新 Cabinet 的 `id` 与原 Cabinet 不同。

**验证需求：2.1, 2.2, 2.3**

### 属性 4：Cabinet 跨项目移动保留数据

*对任意* Cabinet 从源 Project 移动到目标 Project，移动完成后：Cabinet 的所有 StructureComponent 和 BaseComponent 数据不变，Cabinet 的 `project_id` 等于目标 Project 的 `id`，源 Project 不再包含该 Cabinet。

**验证需求：3.1, 3.2, 3.3**

### 属性 5：移动失败时原结构不变

*对任意* 失败的 Cabinet 移动操作（如目标 Project 不存在），源 Project 的结构应保持与操作前完全一致。

**验证需求：3.4**

### 属性 6：价格聚合不变量

*对任意* 层级结构，以下等式在任何数据修改后均成立：
- `BaseComponent.total_price = quantity × unit_price × discount_rate`
- `StructureComponent.total_price = Σ BaseComponent.total_price`
- `Cabinet.total_price = Σ StructureComponent.total_price`
- `Project.total_price = Σ Cabinet.total_price`

**验证需求：5.3, 5.4, 5.5, 5.6**

### 属性 7：后端价格计算权威性

*对任意* BaseComponent 的数量和单价组合，后端 PriceEngine 计算的结果应与前端提交的预计算值进行比对；若不一致，系统应使用后端结果并记录差异日志。

**验证需求：5.8, 5.9**

### 属性 8：价格公式解析往返

*对任意* 语法有效的 Price_Formula 字符串，经过 SymPy 解析后再格式化为字符串，再次解析后应产生与原始公式等价的计算结果（对相同输入变量产生相同数值输出）。

**验证需求：16.8**

### 属性 9：Excel 核价单内容完整性

*对任意* Project，生成的 Internal_Pricing_Sheet 应包含该 Project 下所有 BaseComponent 的型号、名称、数量、单价、总价，以及折扣率、损耗率、辅材费、人工费、税金参数，且数值与数据库中的值一致。

**验证需求：6.2, 6.3, 6.4, 6.5**

### 属性 10：数据导出导入往返

*对任意* Project 数据，将其导出为 Excel 格式再重新导入，应产生与原始数据等价的 Project 结构，包含所有 BaseComponent 的型号、数量、单价和 Price_Formula。

**验证需求：17.3, 17.4, 17.5**

### 属性 11：模板保存与应用往返

*对任意* Cabinet 或 StructureComponent，保存为 Template 后再应用到新 Project，应创建与原节点结构相同（子节点数量和类型一致）的新节点，且 BaseComponent 的单价使用 Material_Database 中的最新值。

**验证需求：8.2, 8.5, 8.6**

### 属性 12：BOM 解析匹配正确性

*对任意* 有效的 BOM Excel 文件，解析后每行数据中：若 `model_number` 在 Material_Database 中存在匹配，则对应 BaseComponent 的 `unit_price` 应等于 Material_Database 中该物料的 `unit_price`；若不存在匹配，则该行应被标记为待确认状态。

**验证需求：9.3, 9.4, 9.5**

### 属性 13：材料搜索结果数量限制

*对任意* 搜索查询，返回的匹配结果数量不超过 20 条。

**验证需求：11.4**

### 属性 14：无效输入被拒绝

*对任意* 以下无效输入，系统应拒绝创建并返回错误：
- 名称为空的 Project 或 Cabinet
- 数量 ≤ 0 的 BaseComponent
- 单价 < 0 的 BaseComponent

**验证需求：18.6, 18.7, 18.8**

### 属性 15：乐观锁并发冲突检测

*对任意* 记录，若两个并发请求同时基于相同的 `version` 值尝试更新，则只有第一个请求成功，第二个请求应收到 409 Conflict 响应，且数据库中的数据与第一个请求的结果一致。

**验证需求：19.2, 19.3, 19.6**

### 属性 16：权限角色控制

*对任意* 角色为 `viewer` 的用户，所有修改、创建、删除操作应返回 403 Forbidden；对任意角色为 `editor` 的用户，只能修改自己创建的 Project；对任意角色为 `admin` 的用户，可以访问所有 Project 和系统配置。

**验证需求：15.5, 15.6, 15.7, 15.8**

### 属性 17：审计日志完整性

*对任意* 创建、修改、删除 Project 或 Cabinet 的操作，以及生成报表的操作，AuditLogs 表中应存在对应记录，且该记录包含操作时间、操作用户 ID、操作类型、受影响实体 ID、修改前值和修改后值。

**验证需求：20.1, 20.2, 20.3, 20.4, 20.5**

### 属性 18：级联删除完整性

*对任意* 被删除的 Project，其所有关联的 Cabinet、StructureComponent 和 BaseComponent 应同时从数据库中删除，不留孤立记录。

**验证需求：18.5**

### 属性 19：批量操作价格一致性

*对任意* 批量折扣率修改操作，操作完成后所有被选中的 BaseComponent 的 `discount_rate` 应等于新设定值，且其所有上级节点（StructureComponent、Cabinet、Project）的总价应已更新为正确的聚合值。

**验证需求：12.3, 12.6**

### 属性 20：快速报价模式自动匹配完整性

*对任意* 选择快速报价模式的 Cabinet（指定了 control_category、cabinet_type、control_structure），执行自动匹配后，系统应根据 AutoMatchRules 插入所有 `is_required = True` 的元器件，且每个插入的 BaseComponent 的 `quantity` 应等于对应规则的 `default_quantity`。

**验证需求：新增业务逻辑 - 自动匹配规则**

### 属性 21：自动隐藏规则正确性

*对任意* 控制结构为"非标控制"的 Cabinet，应用自动隐藏规则后，所有 `component_category` 为 'PLC及模块'、'开关电源'、'信号隔离器'、'触摸屏' 的 BaseComponent 的 `is_hidden` 字段应为 True。

**验证需求：新增业务逻辑 - 自动隐藏机制**

### 属性 22：人工费用计算正确性

*对任意* Cabinet 和基础成本 base_cost，计算的人工费用应满足：
- `assembly_fee = base_cost × assembly_fee_rate`
- `management_fee = base_cost × management_fee_rate`
- `profit = base_cost × profit_rate`
- 若 Cabinet 包含 PLC（控制结构为'自控型'或'纯PLC型'，或存在 component_category='PLC及模块' 的元器件），则 `programming_fee` 和 `debugging_fee` 应为规则中配置的固定值；否则应为 0
- `total_labor_cost = assembly_fee + management_fee + profit + programming_fee + debugging_fee`

**验证需求：新增业务逻辑 - 人工费用联动计算**

### 属性 23：柜体类型配置唯一性

*对任意* 两个不同的 CabinetTypeConfig 记录，其 (control_category, cabinet_type, control_structure) 三元组应不相同。

**验证需求：新增业务逻辑 - 柜体分类体系**

### 属性 24：报价模式一致性

*对任意* Cabinet，若 `quotation_mode = 'detailed'`，则不应存在 `is_auto_matched = True` 的 BaseComponent；若 `quotation_mode = 'quick'`，则应存在至少一个 `is_auto_matched = True` 的 BaseComponent（假设自动匹配规则非空）。

**验证需求：新增业务逻辑 - 报价模式**

### 属性 25：回路类型非标柜应用

*对任意* 控制结构为"非标控制"的 Cabinet，其所有 StructureComponent 应具有有效的 `circuit_type` 值（非空且属于预定义的回路类型列表）。

**验证需求：新增业务逻辑 - 非标柜报价原则**

---

## 错误处理

### 错误分类与响应

| 错误类型 | HTTP 状态码 | 处理策略 |
|----------|-------------|----------|
| 认证失败 | 401 | 返回错误信息，前端跳转登录页 |
| 权限不足 | 403 | 返回角色要求说明 |
| 资源不存在 | 404 | 返回资源类型和 ID |
| 并发冲突 | 409 | 返回当前最新版本数据 |
| 输入验证失败 | 422 | 返回字段级错误详情 |
| 公式语法错误 | 422 | 记录日志，使用默认公式，返回警告 |
| 柜体配置无效 | 422 | 返回无效的配置组合说明 |
| 自动匹配规则缺失 | 422 | 返回警告，允许手动配置 |
| 数据库事务失败 | 500 | 回滚事务，返回通用错误，记录详细日志 |
| BOM 格式无效 | 400 | 返回具体格式错误位置 |

### 事务处理策略

所有写操作（创建、更新、删除）均在数据库事务中执行：

```python
@contextmanager
def transaction():
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        audit_service.log_error(e)
        raise
```

### 公式解析错误处理

```python
def parse_formula(formula_str: str) -> Callable:
    try:
        expr = sympify(formula_str, locals=ALLOWED_SYMBOLS)
        return lambdify(list(expr.free_symbols), expr)
    except (SympifyError, TypeError) as e:
        logger.error(f"Formula parse error: {formula_str}, {e}")
        return DEFAULT_FORMULA  # 使用默认公式
```

### 自动匹配错误处理

```python
def apply_auto_match(cabinet):
    """应用自动匹配规则"""
    try:
        # 查询匹配规则
        config = CabinetTypeConfigs.query.filter_by(
            control_category=cabinet.control_category,
            cabinet_type=cabinet.cabinet_type,
            control_structure=cabinet.control_structure,
            is_active=True
        ).first()
        
        if not config:
            logger.warning(f"No config found for cabinet {cabinet.id}")
            return {
                'status': 'warning',
                'message': '未找到匹配的柜体配置，请手动添加元器件',
                'matched_count': 0
            }
        
        rules = AutoMatchRules.query.filter_by(
            cabinet_type_config_id=config.id
        ).order_by(AutoMatchRules.match_priority.desc()).all()
        
        if not rules:
            logger.warning(f"No auto-match rules for config {config.id}")
            return {
                'status': 'warning',
                'message': '该柜体类型暂无自动匹配规则',
                'matched_count': 0
            }
        
        # 执行匹配
        matched_count = 0
        for rule in rules:
            material = Materials.query.get(rule.material_id)
            if material and material.is_active:
                create_base_component(
                    cabinet=cabinet,
                    material=material,
                    quantity=rule.default_quantity,
                    is_auto_matched=True,
                    component_category=rule.component_category
                )
                matched_count += 1
        
        return {
            'status': 'success',
            'message': f'成功匹配 {matched_count} 个元器件',
            'matched_count': matched_count
        }
        
    except Exception as e:
        logger.error(f"Auto-match error for cabinet {cabinet.id}: {e}")
        db.session.rollback()
        raise AutoMatchError(f"自动匹配失败: {str(e)}")
```

### 人工费用计算错误处理

```python
def calculate_labor_cost(cabinet, base_cost):
    """计算人工费用，带容错处理"""
    try:
        # 查询费用规则
        rule = get_labor_cost_rule(cabinet)
        
        if not rule:
            logger.warning(f"No labor cost rule for cabinet {cabinet.id}, using defaults")
            rule = get_default_labor_cost_rule()
        
        # 验证费率范围
        if not (0 <= rule.assembly_fee_rate <= 1):
            raise ValueError(f"Invalid assembly_fee_rate: {rule.assembly_fee_rate}")
        if not (0 <= rule.management_fee_rate <= 1):
            raise ValueError(f"Invalid management_fee_rate: {rule.management_fee_rate}")
        if not (0 <= rule.profit_rate <= 1):
            raise ValueError(f"Invalid profit_rate: {rule.profit_rate}")
        
        # 执行计算
        result = perform_labor_cost_calculation(cabinet, base_cost, rule)
        
        return result
        
    except ValueError as e:
        logger.error(f"Labor cost calculation validation error: {e}")
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"Labor cost calculation error: {e}")
        # 返回零费用作为降级方案
        return {
            'assembly_fee': 0,
            'management_fee': 0,
            'profit': 0,
            'programming_fee': 0,
            'debugging_fee': 0,
            'total_labor_cost': 0,
            'error': str(e)
        }
```

### 并发冲突处理流程

```
客户端提交更新（携带 version=N）
    ↓
服务端执行 UPDATE ... WHERE id=X AND version=N
    ↓
影响行数 = 0？
    ├── 是 → 查询当前最新数据 → 返回 409 + 最新数据
    └── 否 → 提交事务 → 返回 200 + 新 version=N+1
```

### 网络中断处理

前端使用 localStorage 缓存未保存的修改，网络恢复后提示用户同步：

```typescript
// composables/useOfflineCache.ts
const pendingChanges = useLocalStorage('pending_changes', [])
// 网络恢复时触发同步提示
window.addEventListener('online', () => showSyncPrompt())
```

---

## 测试策略

### 双轨测试方法

系统采用单元测试和属性测试相结合的方式，两者互补：

- **单元测试**：验证具体示例、边界条件和错误处理
- **属性测试**：验证对所有有效输入均成立的通用属性

### 属性测试配置

- 属性测试库：Python 使用 **Hypothesis**，前端使用 **fast-check**
- 每个属性测试最少运行 **100 次迭代**
- 每个属性测试必须通过注释引用设计文档中的属性编号
- 标签格式：`# Feature: electrical-equipment-quotation-system, Property {N}: {property_text}`

### 属性测试实现示例

```python
# tests/test_price_engine.py
from hypothesis import given, settings
from hypothesis import strategies as st

# Feature: electrical-equipment-quotation-system, Property 6: 价格聚合不变量
@given(
    quantity=st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('9999')),
    unit_price=st.decimals(min_value=Decimal('0'), max_value=Decimal('999999')),
    discount_rate=st.decimals(min_value=Decimal('0'), max_value=Decimal('1'))
)
@settings(max_examples=100)
def test_base_component_price_invariant(quantity, unit_price, discount_rate):
    total = calculate_base_price(quantity, unit_price, discount_rate)
    assert total == quantity * unit_price * discount_rate

# Feature: electrical-equipment-quotation-system, Property 8: 价格公式解析往返
@given(
    base_cost=st.floats(min_value=0, max_value=1e6),
    loss_rate=st.floats(min_value=0, max_value=0.5),
    tax_rate=st.floats(min_value=0, max_value=0.3)
)
@settings(max_examples=100)
def test_formula_round_trip(base_cost, loss_rate, tax_rate):
    formula_str = "base_cost * (1 + loss_rate) * (1 + tax_rate)"
    parsed = parse_formula(formula_str)
    result1 = parsed(base_cost=base_cost, loss_rate=loss_rate, tax_rate=tax_rate)
    formatted = format_formula(parsed)
    reparsed = parse_formula(formatted)
    result2 = reparsed(base_cost=base_cost, loss_rate=loss_rate, tax_rate=tax_rate)
    assert abs(result1 - result2) < 1e-9

# Feature: electrical-equipment-quotation-system, Property 15: 乐观锁并发冲突检测
@given(initial_version=st.integers(min_value=1, max_value=1000))
@settings(max_examples=100)
def test_optimistic_lock_conflict(initial_version):
    project = create_project_with_version(initial_version)
    # 第一次更新成功
    result1 = update_project(project.id, "name_1", version=initial_version)
    assert result1.version == initial_version + 1
    # 第二次使用旧版本号更新应失败
    with pytest.raises(ConflictError):
        update_project(project.id, "name_2", version=initial_version)

# Feature: electrical-equipment-quotation-system, Property 20: 快速报价模式自动匹配完整性
@given(
    control_category=st.sampled_from(['低压类', '配电类', '控制类', '自控类']),
    cabinet_type=st.sampled_from(['配电箱/柜', '控制箱/柜', '低压进线柜/出线柜']),
    control_structure=st.sampled_from(['非标控制', '自控型', '纯PLC型', 'MCC柜', '抽屉柜'])
)
@settings(max_examples=100)
def test_auto_match_completeness(control_category, cabinet_type, control_structure):
    # 创建柜体配置和匹配规则
    config = create_cabinet_type_config(control_category, cabinet_type, control_structure)
    required_rules = create_required_auto_match_rules(config)
    
    # 创建快速报价模式的柜体
    cabinet = create_cabinet(
        quotation_mode='quick',
        control_category=control_category,
        cabinet_type=cabinet_type,
        control_structure=control_structure
    )
    
    # 执行自动匹配
    auto_match_service.apply_auto_match(cabinet)
    
    # 验证所有必选元器件都已插入
    matched_components = BaseComponent.query.filter(
        BaseComponent.cabinet_id == cabinet.id,
        BaseComponent.is_auto_matched == True
    ).all()
    
    matched_material_ids = {c.material_id for c in matched_components}
    required_material_ids = {r.material_id for r in required_rules}
    
    assert required_material_ids.issubset(matched_material_ids)
    
    # 验证数量正确
    for component in matched_components:
        rule = next(r for r in required_rules if r.material_id == component.material_id)
        assert component.quantity == rule.default_quantity

# Feature: electrical-equipment-quotation-system, Property 21: 自动隐藏规则正确性
@given(
    num_plc_components=st.integers(min_value=0, max_value=5),
    num_other_components=st.integers(min_value=0, max_value=10)
)
@settings(max_examples=100)
def test_auto_hide_rules(num_plc_components, num_other_components):
    cabinet = create_cabinet(control_structure='非标控制')
    
    # 添加PLC相关元器件
    hidden_categories = ['PLC及模块', '开关电源', '信号隔离器', '触摸屏']
    for i in range(num_plc_components):
        category = hidden_categories[i % len(hidden_categories)]
        create_base_component(cabinet, component_category=category)
    
    # 添加其他元器件
    for i in range(num_other_components):
        create_base_component(cabinet, component_category='一次元器件')
    
    # 应用自动隐藏规则
    apply_auto_hide_rules(cabinet)
    
    # 验证PLC相关元器件被隐藏
    plc_components = BaseComponent.query.filter(
        BaseComponent.cabinet_id == cabinet.id,
        BaseComponent.component_category.in_(hidden_categories)
    ).all()
    
    assert all(c.is_hidden == True for c in plc_components)
    
    # 验证其他元器件未被隐藏
    other_components = BaseComponent.query.filter(
        BaseComponent.cabinet_id == cabinet.id,
        ~BaseComponent.component_category.in_(hidden_categories)
    ).all()
    
    assert all(c.is_hidden == False for c in other_components)

# Feature: electrical-equipment-quotation-system, Property 22: 人工费用计算正确性
@given(
    base_cost=st.decimals(min_value=Decimal('1000'), max_value=Decimal('1000000')),
    assembly_rate=st.decimals(min_value=Decimal('0.05'), max_value=Decimal('0.20')),
    management_rate=st.decimals(min_value=Decimal('0.03'), max_value=Decimal('0.15')),
    profit_rate=st.decimals(min_value=Decimal('0.10'), max_value=Decimal('0.30')),
    has_plc=st.booleans()
)
@settings(max_examples=100)
def test_labor_cost_calculation(base_cost, assembly_rate, management_rate, profit_rate, has_plc):
    # 创建人工费用规则
    rule = create_labor_cost_rule(
        assembly_fee_rate=assembly_rate,
        management_fee_rate=management_rate,
        profit_rate=profit_rate,
        programming_fee=Decimal('5000'),
        debugging_fee=Decimal('3000')
    )
    
    # 创建柜体
    control_structure = '自控型' if has_plc else '非标控制'
    cabinet = create_cabinet(control_structure=control_structure)
    
    # 计算人工费用
    result = calculate_labor_cost(cabinet, base_cost)
    
    # 验证计算正确性
    expected_assembly = base_cost * assembly_rate
    expected_management = base_cost * management_rate
    expected_profit = base_cost * profit_rate
    expected_programming = Decimal('5000') if has_plc else Decimal('0')
    expected_debugging = Decimal('3000') if has_plc else Decimal('0')
    expected_total = (expected_assembly + expected_management + expected_profit + 
                     expected_programming + expected_debugging)
    
    assert abs(result['assembly_fee'] - expected_assembly) < Decimal('0.01')
    assert abs(result['management_fee'] - expected_management) < Decimal('0.01')
    assert abs(result['profit'] - expected_profit) < Decimal('0.01')
    assert result['programming_fee'] == expected_programming
    assert result['debugging_fee'] == expected_debugging
    assert abs(result['total_labor_cost'] - expected_total) < Decimal('0.01')
```

### 单元测试重点

单元测试聚焦于以下场景（避免与属性测试重复）：

1. **具体示例**：Cabinet 复制后名称包含"(副本)"（需求 2.4）
2. **边界条件**：BOM 文件格式无效时的错误信息（需求 9.8）
3. **集成点**：JWT 令牌过期后 API 返回 401（需求 15.4）
4. **错误条件**：无效公式语法时使用默认公式（需求 16.5）
5. **权限示例**：viewer 角色尝试删除 Project 返回 403（需求 15.6）

### 测试覆盖目标

| 模块 | 单元测试 | 属性测试 |
|------|----------|----------|
| PriceEngine | 边界值示例 | 属性 6, 7, 8 |
| ProjectService | CRUD 示例 | 属性 1, 2, 18 |
| CabinetService | 复制/移动示例 | 属性 3, 4, 5 |
| MaterialService | 搜索示例 | 属性 13 |
| TemplateService | 应用示例 | 属性 11 |
| BomParser | 格式错误示例 | 属性 12 |
| ReportService | 内容验证示例 | 属性 9, 10 |
| AuthService | 登录/权限示例 | 属性 16 |
| AuditService | 日志字段示例 | 属性 17 |
| ConcurrencyHandler | 冲突示例 | 属性 15 |
| AutoMatchService | 匹配规则示例 | 属性 20, 24 |
| LaborCostService | PLC检测示例 | 属性 22 |
| CabinetTypeConfig | 配置查询示例 | 属性 23, 25 |
| AutoHideRules | 隐藏逻辑示例 | 属性 21 |
