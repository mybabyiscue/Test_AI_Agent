# 接口获取 Agent 知识库设计说明

## 文件说明

- 文件名称：`接口获取Agent知识库设计说明.md`
- 文件作用：说明接口获取 Agent 如何维护接口与数据库结构知识库，并为测试用例 Agent、接口自动化 Agent 提供标准化上下文。
- 文件主要内容：包含知识库目录结构、数据库结构采集格式、Apifox 接口信息格式、新增/更新/删除/查询机制、差异比对机制、自动化交付格式和安全约束。
- 所属阶段：接口获取 Agent 方案设计阶段。

## 1. 角色定位

接口获取 Agent 是整套 AI 测试流程中的基础上下文 Agent，负责维护“接口文档 + 数据库结构”的本地知识库。

它不负责执行业务测试，也不直接生成最终自动化脚本。它的核心职责是把真实接口信息、数据库结构信息整理成后续 Agent 可以直接消费的标准化文件。

## 2. 核心目标

- 维护多个系统的接口知识库。
- 维护多个测试数据库的结构知识库。
- 从 Apifox 项目中提取完整接口信息。
- 从指定测试数据库中提取库、表、字段、索引等结构信息。
- 所有结果本地落盘，长期维护。
- 支持新增、更新、删除、查询和差异比对。
- 向自动化执行 Agent 交付标准化 JSON 上下文。

## 3. 当前系统范围

### 3.1 系统与数据库来源

当前规划管理三个数据库来源：

- `silkroad`：丝路测试数据库。
- `shark`：鲨域测试数据库。
- `saas`：SAAS 测试数据库。

数据库连接信息不写入代码、不写入 Prompt、不写入知识库文件，只通过环境变量或本地私有配置读取。

### 3.2 系统与接口来源

当前接口来源统一为 Apifox：

- `silkroad`：Apifox 项目 `776242`。
- `shark`：Apifox 项目 `7714336`。
- `callcenter`：Apifox 项目 `460082`。

接口信息必须来自 Apifox 实际项目内容，不能凭空补接口。

## 4. 推荐知识库目录结构

```text
knowledge_base/
  README.md
  registry.example.json
  _schemas/
    database_schema.schema.json
    apifox_project.schema.json
    automation_context.schema.json
    change_set.schema.json
  silkroad/
    README.md
    database/
      README.md
      center.json
      cms.json
      crm_core.json
      cx.json
      ec.json
      oms.json
      result.json
    apis/
      README.md
      apifox_project_776242.json
  shark/
    README.md
    database/
      README.md
      mall4cloud_saas_admin.json
      mall4cloud_saas_order.json
      ...
    apis/
      README.md
      apifox_project_7714336.json
  saas/
    README.md
    database/
      README.md
      contact.json
      customer.json
      ...
    apis/
      README.md
  callcenter/
    README.md
    apis/
      README.md
      apifox_project_460082.json
```

说明：

- 每个系统一个目录。
- 数据库结构统一放在 `database/`。
- 接口资产统一放在 `apis/`。
- 每个数据库一个 JSON 文件。
- 每个 Apifox 项目一个 JSON 文件。
- `_schemas/` 保存知识库文件格式约束。
- `registry.example.json` 只保存来源配置模板，不保存密钥。

## 5. 数据库结构采集格式

### 5.1 文件命名

```text
knowledge_base/<system>/database/<db_name>.json
```

示例：

```text
knowledge_base/silkroad/database/center.json
```

### 5.2 标准结构

```json
{
  "file_info": {
    "file_name": "center.json",
    "purpose": "保存 center 库的数据库结构知识，供接口获取 Agent 和自动化执行 Agent 使用。",
    "main_contents": "包含库名、表名、表注释、字段结构、字段类型、是否可为空、默认值、主键信息、索引信息和字段注释。",
    "stage": "接口获取 Agent 阶段"
  },
  "system": "silkroad",
  "source_type": "mysql_schema",
  "db_name": "center",
  "collected_at": "2026-04-21T00:00:00+08:00",
  "collector_version": "mvp-v1",
  "tables": [
    {
      "table_name": "",
      "table_comment": "",
      "columns": [
        {
          "column_name": "",
          "ordinal_position": 1,
          "data_type": "",
          "column_type": "",
          "is_nullable": "",
          "default_value": null,
          "column_key": "",
          "extra": "",
          "column_comment": ""
        }
      ],
      "indexes": [
        {
          "index_name": "",
          "non_unique": false,
          "columns": [],
          "index_type": ""
        }
      ]
    }
  ],
  "missing_fields": [],
  "warnings": []
}
```

### 5.3 采集 SQL 范围

只允许查询元数据表，例如：

- `information_schema.tables`
- `information_schema.columns`
- `information_schema.statistics`

禁止：

- `select * from 业务表`
- 导出表内业务数据
- 保存用户、订单、客户、支付等真实记录

## 6. Apifox 接口信息格式

### 6.1 文件命名

```text
knowledge_base/<system>/apis/apifox_project_<project_id>.json
```

示例：

```text
knowledge_base/silkroad/apis/apifox_project_776242.json
```

### 6.2 标准结构

```json
{
  "file_info": {
    "file_name": "apifox_project_776242.json",
    "purpose": "保存 Apifox 项目 776242 的接口知识，供测试用例 Agent 和自动化执行 Agent 使用。",
    "main_contents": "包含接口名称、分组、路径、方法、参数、请求体、响应体、鉴权方式、示例和缺失字段。",
    "stage": "接口获取 Agent 阶段"
  },
  "system": "silkroad",
  "platform": "apifox",
  "project_id": "776242",
  "source_url": "https://app.apifox.com/project/776242",
  "collected_at": "2026-04-21T00:00:00+08:00",
  "collector_version": "mvp-v1",
  "apis": [
    {
      "module": "",
      "folder_path": [],
      "api_name": "",
      "method": "",
      "path": "",
      "description": "",
      "headers": {},
      "path_params": [],
      "query_params": [],
      "request_body": {},
      "response_body": {},
      "examples": {
        "request": {},
        "response": {}
      },
      "auth_type": "",
      "tags": [],
      "missing_fields": []
    }
  ],
  "missing_fields": [],
  "warnings": []
}
```

### 6.3 缺失字段处理

如果 Apifox 文档里没有某项信息，不允许猜测，需要写入 `missing_fields`。

示例：

```json
{
  "api_name": "创建订单",
  "method": "POST",
  "path": "/orders",
  "missing_fields": ["auth_type", "response_body.examples"]
}
```

## 7. 新增、更新、删除、查询机制

### 7.1 新增

新增系统时：

1. 在 `knowledge_base/` 下创建系统目录。
2. 创建 `database/` 和 `apis/` 子目录。
3. 在 `registry.local.json` 或配置层登记来源。
4. 执行采集任务生成知识文件。
5. 更新索引和变更记录。

新增数据库时：

1. 在对应系统的 `database/` 下新增 `<db_name>.json`。
2. 只采集结构，不采集业务数据。
3. 写入中文 `file_info`。

新增 Apifox 项目时：

1. 在对应系统的 `apis/` 下新增 `apifox_project_<project_id>.json`。
2. 通过统一凭证管理读取 Apifox token。
3. 拉取接口信息并标准化。

### 7.2 更新

更新数据库结构时：

1. 重新采集元数据。
2. 与旧文件做差异比对。
3. 生成 `change_set`。
4. 覆盖主知识文件。
5. 保留更新时间和采集版本。

更新接口信息时：

1. 重新从 Apifox 拉取项目接口。
2. 标准化接口数据。
3. 对比新增、变更、删除接口。
4. 覆盖主知识文件。
5. 输出变更摘要。

### 7.3 删除

删除按范围执行：

- 按系统删除：删除 `knowledge_base/<system>/`。
- 按数据库删除：删除 `knowledge_base/<system>/database/<db_name>.json`。
- 按 Apifox 项目删除：删除 `knowledge_base/<system>/apis/apifox_project_<project_id>.json`。

删除必须记录：

- 删除对象。
- 删除时间。
- 删除原因。
- 操作人或触发来源。

### 7.4 查询

支持查询维度：

- 系统名。
- 数据库名。
- 表名。
- 字段名。
- Apifox 项目 ID。
- 接口名称。
- 接口路径。
- HTTP 方法。

查询返回结果应该包含：

- 命中的知识文件路径。
- 命中的表或接口。
- 关键字段。
- 中文说明。
- 是否存在缺失信息。

## 8. 差异比对机制

### 8.1 数据库结构比对

需要识别：

- 新增库。
- 删除库。
- 新增表。
- 删除表。
- 表注释变化。
- 新增字段。
- 删除字段。
- 字段类型变化。
- 是否可为空变化。
- 默认值变化。
- 字段注释变化。
- 索引变化。

### 8.2 接口信息比对

需要识别：

- 新增接口。
- 删除接口。
- 请求方法变化。
- 请求路径变化。
- 请求头变化。
- Query 参数变化。
- Body 参数变化。
- 响应体变化。
- 鉴权方式变化。
- 示例变化。
- 接口描述变化。

### 8.3 差异文件格式

差异文件建议保存在：

```text
knowledge_base/<system>/changes/<yyyyMMdd_HHmmss>_<source>_change_set.json
```

## 9. 交付给自动化执行 Agent 的标准格式

自动化执行 Agent 不应该直接读取所有知识库原始文件，而应该读取接口获取 Agent 整理后的上下文包。

建议格式：

```json
{
  "file_info": {
    "file_name": "automation_context.json",
    "purpose": "向自动化执行 Agent 交付需求相关接口、数据库结构和缺失信息。",
    "main_contents": "包含需求相关接口清单、请求响应结构、接口依赖、涉及库表、造数字段建议和缺失信息。",
    "stage": "接口获取 Agent 阶段"
  },
  "requirement_id": "",
  "system": "",
  "related_apis": [],
  "related_database_tables": [],
  "api_dependencies": [],
  "data_setup_hints": [],
  "missing_fields": [],
  "warnings": []
}
```

## 10. 与数据库造数的关系

接口获取 Agent 不直接执行业务造数，但需要为自动化执行 Agent 提供结构依据。

需要识别：

- 主键字段。
- 外键或关联字段。
- 状态字段。
- 时间字段。
- 逻辑删除字段。
- 租户字段。
- 用户字段。
- 订单、商品、客户、库存等关键业务实体字段。

输出方式：

- 在 `data_setup_hints` 中给出“可能需要造数的表和字段”。
- 明确标记哪些字段只能从接口或业务规则确认，不能凭数据库结构猜测。

## 11. 安全约束

必须遵守：

- 不保存明文数据库密码。
- 不保存明文平台 token。
- 不导出业务数据。
- 不执行 `select *`。
- 不保存表内记录。
- 不在报告或日志中打印密钥。
- 所有文件必须有中文说明。
- 所有新需求相关输出必须归档到当前需求运行目录。

## 12. 当前准备产物

本次准备会落地以下文件：

- `knowledge_base/README.md`：知识库总说明。
- `knowledge_base/registry.example.json`：来源配置模板，不含密钥。
- `knowledge_base/_schemas/database_schema.schema.json`：数据库结构知识文件 Schema。
- `knowledge_base/_schemas/apifox_project.schema.json`：Apifox 接口知识文件 Schema。
- `knowledge_base/_schemas/automation_context.schema.json`：交付自动化 Agent 的上下文 Schema。
- `knowledge_base/_schemas/change_set.schema.json`：差异比对结果 Schema。
- 各系统目录下的 `README.md`：系统级中文说明。

## 13. 后续实现建议

建议分三步实现：

1. 先实现知识库文件格式、目录创建和查询能力。
2. 再实现 MySQL 元数据采集和 Apifox 项目采集。
3. 最后实现差异比对、自动化上下文打包和按需求归档。

当前阶段先完成方案和本地结构准备，不连接真实数据库，也不拉取真实接口。
