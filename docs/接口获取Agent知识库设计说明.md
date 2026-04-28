# 接口获取 Agent 知识库设计说明

## 1. 文档目的

本文档用于统一接口获取 Agent 的知识库设计规则，明确数据库知识库同步范围、接口知识库同步范围、同步边界、主文件格式、Agent3 的接口详情获取方式，以及补证与同步报告的职责分离。

本文档生效后，知识库的最终规则如下：

1. 数据库知识库继续同步数据库结构元信息。
2. 接口知识库只同步基础接口索引，不同步完整接口契约。
3. 接口完整详情只能由 Agent3 在处理具体任务时，对本次命中的接口一对一按需获取。

## 2. 设计目标

知识库需要同时满足以下目标：

1. 让后续 Agent 能快速定位相关接口和数据库结构。
2. 保持知识库长期可维护，避免沉淀体量过大且过期快的完整接口契约。
3. 将“全局沉淀”和“任务态详情获取”分层，降低同步成本与错误传播风险。
4. 对无法确认的信息不做猜测，统一标记为“待确认”。

## 3. 知识库范围

### 3.1 数据库知识库

数据库知识库保存数据库结构元信息，供后续 Agent 用于：

- 涉及表结构定位
- 字段含义理解
- 主键、索引、状态字段判断
- 数据准备提示
- 数据校验提示

数据库知识库不保存任何业务数据。

### 3.2 接口知识库

接口知识库只保存基础接口索引，供后续 Agent 用于：

- 候选接口定位
- 需求与接口的初步关联
- 项目范围与接口路径定位
- Agent3 的按需详情获取入口

接口知识库不是完整契约库。

## 4. 推荐目录结构

```text
knowledge_base/
├── _schemas/
├── sync_reports/
├── validation_reports/
├── silkroad/
│   ├── database/
│   └── apis/
├── shark/
│   ├── database/
│   └── apis/
├── saas/
│   ├── database/
│   └── apis/
└── callcenter/
    └── apis/
```

## 5. 数据库知识库设计

### 5.1 文件命名

```text
knowledge_base/<system>/database/<db_name>.json
```

### 5.2 数据库同步字段

数据库主文件必须包含：

- `system`
- `source_type`
- `db_name`
- `collected_at`
- `collector_version`
- `tables`
- `missing_fields`
- `warnings`

`tables` 中的每张表必须包含：

- `table_name`
- `table_comment`
- `columns`
- `indexes`

`columns` 中的每个字段必须包含：

- `column_name`
- `ordinal_position`
- `data_type`
- `column_type`
- `is_nullable`
- `default_value`
- `column_key`
- `extra`
- `column_comment`

`indexes` 中的每个索引必须包含：

- `index_name`
- `non_unique`
- `columns`
- `index_type`

### 5.3 数据库同步边界

数据库同步只能查询以下元数据表：

- `information_schema.tables`
- `information_schema.columns`
- `information_schema.statistics`

数据库同步禁止：

- 查询业务表数据
- 导出业务数据
- 对业务表执行 `select *`
- 将真实记录写入知识库、日志或报告

## 6. 接口知识库设计

### 6.1 文件命名

```text
knowledge_base/<system>/apis/apifox_project_<project_id>.json
```

### 6.2 接口主索引字段

接口知识库主文件保存的是基础接口索引。每条接口索引固定包含：

- `module`
- `folder_path`
- `api_name`
- `method`
- `path`
- `description`
- `operation_id`
- `tags`
- `source`
- `project_id`
- `updated_at`
- `sync_mode`
- `detail_fetch_policy`
- `missing_fields`

文件级元信息必须包含：

- `system`
- `platform`
- `project_id`
- `source_url`
- `collected_at`
- `collector_version`
- `sync_mode`
- `detail_fetch_policy`
- `apis`
- `missing_fields`
- `warnings`

### 6.3 接口主索引固定规则

- `sync_mode` 必须固定为 `basic_api_index`
- `detail_fetch_policy` 必须明确说明：
  - 请求头、请求参数、请求体、响应体、示例和 schema 不保存在接口主索引中
  - 只能由 Agent3 在处理具体接口时，针对本次涉及的接口一对一从 Apifox、接口文档或代码实现中按需获取
  - 不允许在知识库同步阶段全量拉取或保存所有接口详情

### 6.4 接口主索引禁止保存的字段

接口知识库中不得保存：

- `headers`
- `path_params`
- `query_params`
- `request_body`
- `response_body`
- `examples.request`
- `examples.response`
- `components.schemas`
- 以及其他完整契约详情

### 6.5 缺失字段处理

当接口文档或索引来源中缺失字段时：

1. 不允许猜测
2. 必须将缺失字段写入 `missing_fields`
3. 字段值无法确认时，必须标记为“待确认”

## 7. 同步机制

### 7.1 数据库同步

数据库同步步骤固定为：

1. 读取来源配置和数据库凭证
2. 查询 `information_schema`
3. 标准化结构
4. 覆盖数据库主文件
5. 生成同步报告

### 7.2 接口同步

接口同步步骤固定为：

1. 读取来源配置和 Apifox 凭证
2. 拉取项目接口清单或基础索引所需信息
3. 标准化为基础接口索引
4. 覆盖接口主索引文件
5. 生成同步报告

接口同步阶段禁止：

- 拉取完整请求头、参数、请求体、响应体、示例和 schema 并写入主知识库
- 把整项目完整 OpenAPI 当作知识库主索引保存

## 8. Agent3 一对一按需获取规则

Agent3 处理接口时必须遵循以下流程：

1. 先读取接口主索引定位候选接口。
2. 根据本次需求和测试用例确定本次真正涉及的接口集合。
3. 只针对这些接口一对一获取详情。
4. 详情来源仅限：
   - Apifox
   - 接口文档
   - 代码实现
5. 获取到详情后，才能输出 headers、参数、请求体、响应体、鉴权方式、schema 展开结果等任务态产物。
6. 无法确认的字段必须标记为“待确认”。

Agent3 禁止：

- 跳过接口索引定位步骤
- 将知识库主索引直接当成完整接口契约
- 全量拉取整个项目所有接口详情
- 对无法确认的字段做猜测

## 9. 同步报告与补证报告

### 9.1 同步报告

同步报告写入：

```text
knowledge_base/sync_reports/<timestamp>_*.json
knowledge_base/sync_reports/<timestamp>_*.md
```

同步报告用于记录：

- 成功同步的数据库
- 成功同步的接口项目
- 失败对象和失败原因
- 生成的主文件

### 9.2 补证报告

补证报告写入：

```text
knowledge_base/validation_reports/<timestamp>_*.md
```

补证报告用于记录：

- 运行阶段核实出的新事实
- 文档冲突项
- 阻塞项
- 风险项

补证报告不是主知识库文件，不替代数据库主文件或接口主索引主文件。

## 10. 安全规则

必须遵守：

- 不保存数据库明文密码
- 不保存平台 token
- 不导出业务数据
- 不在日志或报告中打印密钥
- 不把真实业务记录写入知识库

## 11. 变更控制

当知识库规则调整时，必须同步修改：

- 设计说明
- `knowledge_base/README.md`
- 知识库同步代码
- Agent3 角色配置或流程逻辑
- 相关测试

避免规则、文档、代码和测试长期漂移。
