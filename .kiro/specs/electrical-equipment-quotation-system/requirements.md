# 需求文档 - 电气设备报价系统

## 简介

电气设备报价系统是一个面向电气设备制造行业的B/S架构报价管理系统，旨在解决传统Excel报价中的版本混乱、组件遗漏和计算繁琐等痛点。系统支持项目层级管理、智能材料匹配、动态报价计算、多格式报表生成、历史模块复用和BOM解析导入等核心功能。

## 术语表

- **Quotation_System**: 电气设备报价系统，本文档描述的整个系统
- **Project**: 项目，报价的顶层实体，包含多个配电柜
- **Cabinet**: 配电柜，项目下的二级实体，包含多个结构组件
- **Structure_Component**: 结构组件，配电柜下的三级实体，包含多个基础元器件
- **Base_Component**: 基础元器件，最小粒度的物料单元
- **BOM**: Bill of Materials，物料清单
- **Template**: 模板，保存的标准配置，可复用
- **Price_Formula**: 价格公式，用于动态计算报价的数学表达式
- **Internal_Pricing_Sheet**: 内部核价单，包含成本明细和公式的Excel报表
- **Customer_Quotation**: 客户报价单，面向客户的PDF格式报价文件
- **Material_Database**: 材料数据库，存储元器件型号、价格和关联关系的数据库
- **User**: 用户，使用系统的工程师或报价人员
- **Accessory**: 附件，与主元器件配套的辅助元器件

## 需求

### 需求 1: 项目层级管理

**用户故事:** 作为报价工程师，我希望按照"项目→配电柜→结构组件→基础元器件"的树状结构管理报价数据，以便清晰组织复杂项目的物料清单。

#### 验收标准

1. THE Quotation_System SHALL 支持创建包含名称、客户、日期和备注字段的Project
2. WHEN User创建Project时，THE Quotation_System SHALL 生成唯一的项目标识符
3. THE Quotation_System SHALL 支持在Project下创建多个Cabinet
4. THE Quotation_System SHALL 支持在Cabinet下创建多个Structure_Component
5. THE Quotation_System SHALL 支持在Structure_Component下添加多个Base_Component
6. THE Quotation_System SHALL 以树状结构展示Project的完整层级关系
7. WHEN User选择任意层级节点时，THE Quotation_System SHALL 高亮显示该节点及其所有子节点
8. THE Quotation_System SHALL 支持展开和折叠树状结构的任意节点

### 需求 2: 整柜复制功能

**用户故事:** 作为报价工程师，我希望快速复制已配置的配电柜，以便在同一项目中快速创建相似配置。

#### 验收标准

1. WHEN User选择一个Cabinet并执行复制操作时，THE Quotation_System SHALL 创建包含所有Structure_Component和Base_Component的新Cabinet
2. WHEN Cabinet被复制时，THE Quotation_System SHALL 为新Cabinet生成唯一标识符
3. WHEN Cabinet被复制时，THE Quotation_System SHALL 保留原Cabinet的所有价格参数和配置
4. THE Quotation_System SHALL 在复制后的Cabinet名称中添加"(副本)"标识

### 需求 3: 跨项目拖拽

**用户故事:** 作为报价工程师，我希望将配电柜从一个项目拖拽到另一个项目，以便复用已有配置。

#### 验收标准

1. WHEN User将Cabinet从一个Project拖拽到另一个Project时，THE Quotation_System SHALL 将该Cabinet及其所有子节点移动到目标Project
2. WHEN 拖拽操作执行时，THE Quotation_System SHALL 保留Cabinet的所有数据和配置
3. WHEN 拖拽操作完成时，THE Quotation_System SHALL 更新源Project和目标Project的统计数据
4. IF 拖拽操作失败，THEN THE Quotation_System SHALL 保持原Project结构不变并显示错误信息

### 需求 4: 智能材料匹配

**用户故事:** 作为报价工程师，我希望在输入主元器件后系统自动推荐配套附件，以便避免遗漏必要的辅助元器件。

#### 验收标准

1. WHEN User添加Base_Component时，THE Quotation_System SHALL 查询Material_Database中的关联Accessory
2. WHEN 关联Accessory存在时，THE Quotation_System SHALL 在界面上显示推荐的Accessory列表
3. THE Quotation_System SHALL 显示每个推荐Accessory的型号、名称和价格
4. WHEN User选择推荐的Accessory时，THE Quotation_System SHALL 将其添加到当前Structure_Component
5. THE Quotation_System SHALL 允许User忽略推荐的Accessory
6. WHEN Base_Component被删除时，THE Quotation_System SHALL 提示User是否同时删除关联的Accessory

### 需求 5: 动态报价计算

**用户故事:** 作为报价工程师，我希望系统根据配置的公式自动计算报价，以便快速获得准确的价格结果。

#### 验收标准

1. THE Quotation_System SHALL 从Material_Database读取Price_Formula配置
2. THE Quotation_System SHALL 支持在Price_Formula中使用折扣率、损耗率、辅材费、人工费和税金参数
3. WHEN Base_Component的数量或单价变化时，THE Quotation_System SHALL 实时重新计算该组件的总价
4. WHEN Structure_Component的任意Base_Component价格变化时，THE Quotation_System SHALL 更新Structure_Component的总价
5. WHEN Cabinet的任意子节点价格变化时，THE Quotation_System SHALL 更新Cabinet的总价
6. WHEN Project的任意子节点价格变化时，THE Quotation_System SHALL 更新Project的总价
7. THE Quotation_System SHALL 在前端显示实时计算的价格预览
8. THE Quotation_System SHALL 在后端验证前端计算结果的正确性
9. IF 前端计算与后端验证结果不一致，THEN THE Quotation_System SHALL 使用后端结果并记录差异日志

### 需求 6: 内部核价单生成

**用户故事:** 作为报价工程师，我希望生成包含成本明细和计算公式的Excel核价单，以便内部审核和成本分析。

#### 验收标准

1. WHEN User请求生成Internal_Pricing_Sheet时，THE Quotation_System SHALL 创建Excel格式文件
2. THE Quotation_System SHALL 在Internal_Pricing_Sheet中包含Project的所有层级数据
3. THE Quotation_System SHALL 在Internal_Pricing_Sheet中保留Price_Formula作为Excel公式
4. THE Quotation_System SHALL 在Internal_Pricing_Sheet中包含每个Base_Component的型号、名称、数量、单价和总价
5. THE Quotation_System SHALL 在Internal_Pricing_Sheet中包含折扣率、损耗率、辅材费、人工费和税金等参数
6. THE Quotation_System SHALL 在Internal_Pricing_Sheet中使用层级缩进展示树状结构
7. WHEN Internal_Pricing_Sheet生成完成时，THE Quotation_System SHALL 提供下载链接

### 需求 7: 客户报价单生成

**用户故事:** 作为报价工程师，我希望生成带水印的PDF客户报价单，以便向客户提供专业的报价文件。

#### 验收标准

1. WHEN User请求生成Customer_Quotation时，THE Quotation_System SHALL 创建PDF格式文件
2. THE Quotation_System SHALL 在Customer_Quotation中包含Project名称、客户名称和日期
3. THE Quotation_System SHALL 在Customer_Quotation中包含Cabinet级别的汇总价格
4. THE Quotation_System SHALL 在Customer_Quotation中隐藏成本明细和Price_Formula
5. THE Quotation_System SHALL 在Customer_Quotation的每一页添加公司水印
6. THE Quotation_System SHALL 在Customer_Quotation中包含项目总价
7. WHEN Customer_Quotation生成完成时，THE Quotation_System SHALL 提供下载链接

### 需求 8: 历史模块复用

**用户故事:** 作为报价工程师，我希望将标准配置保存为模板，以便在新项目中快速复用。

#### 验收标准

1. WHEN User选择Cabinet或Structure_Component并执行保存为模板操作时，THE Quotation_System SHALL 创建Template记录
2. THE Quotation_System SHALL 在Template中保存选定节点及其所有子节点的完整配置
3. THE Quotation_System SHALL 要求User为Template提供名称和描述
4. THE Quotation_System SHALL 维护Template库供User浏览和搜索
5. WHEN User选择Template并应用到Project时，THE Quotation_System SHALL 创建包含Template所有配置的新节点
6. WHEN Template被应用时，THE Quotation_System SHALL 使用Material_Database中的最新价格更新Base_Component单价
7. THE Quotation_System SHALL 允许User编辑和删除自己创建的Template

### 需求 9: BOM解析与导入

**用户故事:** 作为报价工程师，我希望从Excel文件导入设计部门的BOM清单，以便快速创建报价项目。

#### 验收标准

1. THE Quotation_System SHALL 支持User通过拖拽上传Excel格式的BOM文件
2. WHEN BOM文件上传时，THE Quotation_System SHALL 解析文件中的型号、名称、数量和规格列
3. WHEN BOM文件解析完成时，THE Quotation_System SHALL 将每行数据与Material_Database中的Base_Component进行匹配
4. WHEN Base_Component匹配成功时，THE Quotation_System SHALL 自动填充单价和关联信息
5. WHEN Base_Component匹配失败时，THE Quotation_System SHALL 标记该行为待确认状态
6. THE Quotation_System SHALL 显示BOM导入预览界面供User确认
7. WHEN User确认导入时，THE Quotation_System SHALL 将BOM数据创建为Project的Structure_Component和Base_Component
8. IF BOM文件格式无效，THEN THE Quotation_System SHALL 显示格式错误信息并拒绝导入

### 需求 10: 类Excel交互体验

**用户故事:** 作为报价工程师，我希望使用类似Excel的快捷键和交互方式，以便提高数据录入效率。

#### 验收标准

1. WHEN User在可编辑单元格中按下Enter键时，THE Quotation_System SHALL 将焦点移动到下一行的相同列
2. WHEN User在可编辑单元格中按下Tab键时，THE Quotation_System SHALL 将焦点移动到同一行的下一列
3. WHEN User按下Shift+Tab键时，THE Quotation_System SHALL 将焦点移动到同一行的上一列
4. WHEN User选择一个或多个单元格并按下Ctrl+C时，THE Quotation_System SHALL 将选中内容复制到剪贴板
5. WHEN User在可编辑单元格中按下Ctrl+V时，THE Quotation_System SHALL 粘贴剪贴板内容
6. THE Quotation_System SHALL 支持通过鼠标拖拽选择多个连续单元格
7. THE Quotation_System SHALL 在选中的单元格周围显示高亮边框

### 需求 11: 材料数据库搜索

**用户故事:** 作为报价工程师，我希望快速搜索和选择元器件，以便高效完成报价配置。

#### 验收标准

1. WHEN User在Base_Component输入框中输入文本时，THE Quotation_System SHALL 在Material_Database中执行模糊搜索
2. THE Quotation_System SHALL 在输入框下方显示匹配的Base_Component列表
3. THE Quotation_System SHALL 在搜索结果中显示型号、名称、规格和单价
4. THE Quotation_System SHALL 限制搜索结果最多显示20条记录
5. WHEN User输入停止超过300毫秒时，THE Quotation_System SHALL 执行搜索请求
6. WHEN User选择搜索结果中的某项时，THE Quotation_System SHALL 自动填充该Base_Component的所有字段
7. WHEN 搜索无结果时，THE Quotation_System SHALL 显示"未找到匹配项"提示

### 需求 12: 批量操作

**用户故事:** 作为报价工程师，我希望批量修改多个元器件的参数，以便快速调整报价。

#### 验收标准

1. THE Quotation_System SHALL 支持User通过复选框选择多个Base_Component
2. WHEN 多个Base_Component被选中时，THE Quotation_System SHALL 显示批量操作工具栏
3. THE Quotation_System SHALL 支持批量修改选中Base_Component的折扣率
4. THE Quotation_System SHALL 支持批量删除选中的Base_Component
5. WHEN 批量操作执行时，THE Quotation_System SHALL 显示操作进度
6. WHEN 批量操作完成时，THE Quotation_System SHALL 更新所有受影响节点的价格
7. IF 批量操作部分失败，THEN THE Quotation_System SHALL 显示失败项的详细信息

### 需求 13: 性能要求

**用户故事:** 作为报价工程师，我希望系统能够流畅处理大型项目，以便应对复杂的报价场景。

#### 验收标准

1. WHEN Project包含50个Cabinet且每个Cabinet包含200个Base_Component时，THE Quotation_System SHALL 在5秒内完成Project加载
2. WHEN User修改Base_Component数量时，THE Quotation_System SHALL 在500毫秒内完成价格重新计算
3. WHEN User滚动包含10000行数据的列表时，THE Quotation_System SHALL 使用懒加载技术仅渲染可见区域
4. THE Quotation_System SHALL 在用户输入停止后300毫秒内触发搜索请求
5. WHEN Internal_Pricing_Sheet包含10000行数据时，THE Quotation_System SHALL 在30秒内完成Excel文件生成
6. WHEN Customer_Quotation包含100页时，THE Quotation_System SHALL 在20秒内完成PDF文件生成

### 需求 14: 数据持久化与事务

**用户故事:** 作为报价工程师，我希望系统可靠地保存我的工作，以便避免数据丢失。

#### 验收标准

1. WHEN User修改Project、Cabinet、Structure_Component或Base_Component时，THE Quotation_System SHALL 将变更保存到SQL Server数据库
2. THE Quotation_System SHALL 在数据库事务中执行所有写操作
3. IF 数据库写操作失败，THEN THE Quotation_System SHALL 回滚事务并保持数据一致性
4. THE Quotation_System SHALL 在每次数据修改后返回操作成功或失败的状态
5. WHEN 网络连接中断时，THE Quotation_System SHALL 在前端缓存User的未保存修改
6. WHEN 网络连接恢复时，THE Quotation_System SHALL 提示User同步缓存的修改
7. THE Quotation_System SHALL 记录每次数据修改的时间戳和操作User

### 需求 15: 用户认证与权限

**用户故事:** 作为系统管理员，我希望控制用户的访问权限，以便保护敏感的报价数据。

#### 验收标准

1. THE Quotation_System SHALL 要求User提供用户名和密码进行身份验证
2. WHEN User身份验证成功时，THE Quotation_System SHALL 创建会话并返回会话令牌
3. WHEN User身份验证失败时，THE Quotation_System SHALL 拒绝访问并显示错误信息
4. THE Quotation_System SHALL 在会话令牌过期后要求User重新登录
5. THE Quotation_System SHALL 支持为User分配查看、编辑或管理员角色
6. WHEN User角色为查看时，THE Quotation_System SHALL 禁止该User修改或删除数据
7. WHEN User角色为编辑时，THE Quotation_System SHALL 允许该User创建和修改自己的Project
8. WHEN User角色为管理员时，THE Quotation_System SHALL 允许该User访问所有Project和系统配置

### 需求 16: 价格公式配置解析器

**用户故事:** 作为系统管理员，我希望在数据库中配置价格计算公式，以便灵活调整报价逻辑。

#### 验收标准

1. THE Quotation_System SHALL 从Material_Database读取以字符串形式存储的Price_Formula
2. THE Quotation_System SHALL 解析Price_Formula中的变量名和数学运算符
3. THE Quotation_System SHALL 支持Price_Formula中使用加法、减法、乘法、除法和括号运算
4. WHEN Price_Formula被解析时，THE Quotation_System SHALL 验证公式的语法正确性
5. IF Price_Formula语法无效，THEN THE Quotation_System SHALL 记录错误并使用默认公式
6. THE Quotation_System SHALL 将解析后的Price_Formula应用于价格计算
7. THE Pretty_Printer SHALL 将Price_Formula格式化为可读的Excel公式
8. FOR ALL 有效的Price_Formula，解析后计算再格式化再解析 SHALL 产生等价的计算结果

### 需求 17: 数据导出格式往返验证

**用户故事:** 作为报价工程师，我希望导出的Excel文件能够准确反映系统数据，以便确保数据一致性。

#### 验收标准

1. WHEN Internal_Pricing_Sheet被生成时，THE Quotation_System SHALL 将Project数据序列化为Excel格式
2. THE Quotation_System SHALL 支持将Internal_Pricing_Sheet重新导入系统
3. FOR ALL Project数据，导出为Excel再导入 SHALL 产生与原始数据等价的Project结构
4. THE Quotation_System SHALL 在往返过程中保留所有Base_Component的型号、数量和单价
5. THE Quotation_System SHALL 在往返过程中保留所有Price_Formula
6. IF 往返验证失败，THEN THE Quotation_System SHALL 记录差异并拒绝导入

### 需求 18: 数据完整性约束

**用户故事:** 作为系统管理员，我希望系统维护数据的完整性，以便避免无效或不一致的数据。

#### 验收标准

1. THE Quotation_System SHALL 确保每个Project具有唯一的标识符
2. THE Quotation_System SHALL 确保每个Cabinet关联到有效的Project
3. THE Quotation_System SHALL 确保每个Structure_Component关联到有效的Cabinet
4. THE Quotation_System SHALL 确保每个Base_Component关联到有效的Structure_Component
5. WHEN Project被删除时，THE Quotation_System SHALL 级联删除所有关联的Cabinet、Structure_Component和Base_Component
6. THE Quotation_System SHALL 拒绝创建没有名称的Project或Cabinet
7. THE Quotation_System SHALL 拒绝创建数量小于或等于0的Base_Component
8. THE Quotation_System SHALL 拒绝创建单价小于0的Base_Component

### 需求 19: 并发编辑冲突处理

**用户故事:** 作为报价工程师，我希望系统能够处理多人同时编辑同一项目的情况，以便避免数据覆盖。

#### 验收标准

1. WHEN 多个User同时编辑同一Project时，THE Quotation_System SHALL 检测并发修改
2. WHEN 并发修改被检测到时，THE Quotation_System SHALL 使用乐观锁机制防止数据覆盖
3. IF User尝试保存已被其他User修改的数据，THEN THE Quotation_System SHALL 拒绝保存并显示冲突提示
4. WHEN 冲突发生时，THE Quotation_System SHALL 显示当前数据库中的最新值
5. THE Quotation_System SHALL 允许User选择保留自己的修改或接受其他User的修改
6. THE Quotation_System SHALL 在每条记录中维护版本号以支持并发控制

### 需求 20: 审计日志

**用户故事:** 作为系统管理员，我希望记录所有关键操作，以便追溯数据变更历史。

#### 验收标准

1. WHEN User创建、修改或删除Project时，THE Quotation_System SHALL 记录审计日志
2. WHEN User创建、修改或删除Cabinet时，THE Quotation_System SHALL 记录审计日志
3. WHEN User生成Internal_Pricing_Sheet或Customer_Quotation时，THE Quotation_System SHALL 记录审计日志
4. THE Quotation_System SHALL 在审计日志中包含操作时间、操作User、操作类型和受影响的数据标识符
5. THE Quotation_System SHALL 在审计日志中记录修改前和修改后的数据值
6. THE Quotation_System SHALL 将审计日志存储在独立的数据库表中
7. THE Quotation_System SHALL 保留审计日志至少12个月
8. WHEN 管理员User请求时，THE Quotation_System SHALL 提供审计日志查询和导出功能
