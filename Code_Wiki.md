# 电气设备报价系统 (Electrical Equipment Quotation System) - Code Wiki

## 1. 项目整体架构

本项目是一个基于前后端分离架构的**电气设备报价系统**。系统旨在通过灵活的配置与规则引擎，支持快速报价与详细报价双模式，实现设备元器件的自动匹配、人工费用计算以及最终报价单的导出。

- **前端架构**：基于 Vue 3 (Composition API) + TypeScript 构建，使用 Vite 作为构建工具，Pinia 进行状态管理，Element Plus 作为 UI 组件库。
- **后端架构**：基于 Python 3 + Flask 框架构建，使用 SQLAlchemy 作为 ORM 进行数据持久化，支持通过 SQLite/MySQL/SQL Server 进行数据存储。
- **核心业务流程**：创建报价项目 $\rightarrow$ 添加/配置柜体（选择控制大类、柜体类型、控制结构） $\rightarrow$ 自动匹配/手动添加元器件 $\rightarrow$ 联动计算基础物料费用与人工费用 $\rightarrow$ 生成并导出报价报表。

---

## 2. 主要模块职责

### 后端模块 (`backend/`)
后端采用经典的分层架构设计（API路由层 $\rightarrow$ 业务服务层 $\rightarrow$ 数据访问层）。

- **`app/api/` (路由控制器)**：定义 RESTful API 接口，负责处理 HTTP 请求与响应。
  - `projects.py` / `cabinets.py`：处理项目和柜体的 CRUD 操作。
  - `components.py` / `materials.py`：处理结构组件、基础元器件和物料库的交互。
  - `cabinet_configs.py`：处理柜体分类及匹配规则配置。
- **`app/services/` (核心业务逻辑层)**：封装复杂业务操作，解耦控制器与数据模型。
  - `price_engine.py`：报价计算引擎，负责层级价格汇总和动态公式计算。
  - `auto_match_service.py`：自动匹配规则引擎，负责自动填充元器件和应用隐藏规则。
  - `labor_cost_service.py`：人工费用计算服务。
- **`app/models/` (数据模型层)**：使用 SQLAlchemy 定义数据库表结构及关系。
  - `project.py`, `cabinet.py`, `structure_component.py`, `base_component.py`：报价项目核心四级结构。
  - `auto_match_rule.py`, `cabinet_type_config.py`：柜体配置及规则引擎相关数据表。
- **`migrations/` (数据库迁移)**：存放数据库结构的 SQL 及 Python 迁移脚本。

### 前端模块 (`frontend/src/`)
前端按功能和视图进行组件化拆分。

- **`api/`**：基于 Axios 封装与后端交互的接口函数。
- **`components/`**：可复用的业务与 UI 组件。
  - `CabinetTypeSelector`：柜体三级联动选择器。
  - `QuotationTable`：核心报价明细表格组件。
  - `BomImport`：BOM清单导入组件。
- **`composables/`**：Vue 3 组合式函数，封装可复用的视图逻辑。
  - `useAutoMatch.ts`：处理触发自动匹配、隐藏规则的视图逻辑。
  - `useProjectDetail.ts`：项目详情页的状态同步与数据刷新机制。
- **`stores/`**：Pinia 状态库，管理全局或跨组件的状态（如用户认证 `auth.ts`、项目缓存 `project.ts`、配置缓存 `cabinetConfig.ts`）。
- **`views/`**：应用路由对应的页面级组件（如项目列表 `ProjectList.vue`、项目详情 `ProjectDetail.vue`、管理后台 `AdminPanel.vue`）。

---

## 3. 关键类与函数说明

### 3.1 后端关键类与函数

- **`PriceEngine`** ([backend/app/services/price_engine.py](file:///workspace/backend/app/services/price_engine.py))
  - **职责**：整个系统的价格计算核心。
  - `calculate_base_price(quantity, unit_price, discount_rate)`：计算单项元器件的总价。
  - `apply_formula(base_cost, formula_str, **params)`：使用 `sympy` 库解析并执行自定义价格公式，包含安全关键字过滤，执行失败时回退到默认公式。
  - `calculate_project_total(project)`：自下而上（基础元器件 $\rightarrow$ 结构组件 $\rightarrow$ 柜体 $\rightarrow$ 项目）递归计算总价。

- **`AutoMatchService`** ([backend/app/services/auto_match_service.py](file:///workspace/backend/app/services/auto_match_service.py))
  - **职责**：处理快速报价模式下的元器件自动匹配逻辑。
  - `apply_auto_match(cabinet)`：根据柜体的分类（控制大类/柜体类型/控制结构），查询 `AutoMatchRule`，自动为该柜体填充对应的默认基础元器件。
  - `apply_auto_hide_rules(cabinet)`：当控制结构为"非标控制"时，自动隐藏特定的 PLC 及相关元器件。

- **数据模型关联设计** ([backend/app/models/](file:///workspace/backend/app/models/))
  - **`Project` $\rightarrow$ `Cabinet` $\rightarrow$ `StructureComponent` $\rightarrow$ `BaseComponent`** 构成一对多层级关系，支持级联删除(`cascade='all, delete-orphan'`)。
  - 表中广泛引入 `version` 字段实现**乐观锁**，防止多用户并发编辑时的脏写。

### 3.2 前端关键设计

- **`useAutoMatch` (Composable)** ([frontend/src/composables/useAutoMatch.ts](file:///workspace/frontend/src/composables/useAutoMatch.ts))
  - 封装了调用后端 `apply_auto_match` 接口的逻辑，并在成功匹配后，联动触发项目数据 (`projectStore`) 的刷新，确保 UI 实时呈现匹配出的元器件。

- **`cabinetConfig` (Pinia Store)** ([frontend/src/stores/cabinetConfig.ts](file:///workspace/frontend/src/stores/cabinetConfig.ts))
  - 缓存从后端拉取的柜体类型配置（控制大类/柜体类型/控制结构），避免在选择器联动时频繁发起 HTTP 请求。

---

## 4. 依赖关系

### 4.1 后端主要依赖 (`backend/requirements.txt`)
- **Flask (>=3.0.0)**：核心 Web 框架。
- **SQLAlchemy (>=2.0.0) / Flask-SQLAlchemy**：ORM 框架。
- **PyJWT**：用于生成和解析 JSON Web Tokens，实现用户身份认证。
- **sympy**：强大的数学符号计算库，用于动态解析和计算用户自定义的价格公式。
- **openpyxl / reportlab**：用于生成并导出 Excel 表格与 PDF 格式的报价单。
- **Flask-CORS**：处理前后端跨域请求。

### 4.2 前端主要依赖 (`frontend/package.json`)
- **vue (^3.4.0)**：前端核心视图框架。
- **vite (^5.1.0)**：极速前端构建与开发服务器。
- **pinia (^2.1.0)**：Vue 官方推荐的全局状态管理库。
- **vue-router (^4.3.0)**：前端路由管理。
- **element-plus (^2.6.0)**：基于 Vue 3 的组件库，提供大量现成的 UI 控件。
- **axios (^1.6.0)**：用于发送 HTTP 异步请求。

---

## 5. 项目运行方式

### 5.1 后端环境启动

1. **进入后端目录**：
   ```bash
   cd backend
   ```
2. **创建并激活虚拟环境** (推荐)：
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # Linux/Mac: source venv/bin/activate
   ```
3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
4. **数据库初始化与迁移** (首次运行)：
   ```bash
   python init_db.py
   python migrate_db.py
   # 或使用提供的快捷批处理文件（如 use_sqlite.bat）
   ```
5. **启动后端服务**：
   ```bash
   python run.py
   ```
   > 默认服务将运行在 `http://localhost:5000`。

### 5.2 前端环境启动

1. **进入前端目录**：
   ```bash
   cd frontend
   ```
2. **安装 Node 依赖**：
   ```bash
   npm install
   ```
3. **启动开发服务器**：
   ```bash
   npm run dev
   ```
   > 默认会启动 Vite 开发服务器，并在控制台输出访问地址（通常为 `http://localhost:5173`）。

4. **生产环境构建**：
   ```bash
   npm run build
   ```
   > 构建产物将生成在 `frontend/dist` 目录下，可部署至 Nginx 或与其他静态服务器集成。
