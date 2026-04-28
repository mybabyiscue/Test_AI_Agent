# 接口与数据库结构知识库

## 文件说明

- 文件名称：`README.md`
- 文件作用：说明本地知识库的用途、目录结构、同步规则、维护边界和安全约束。
- 适用阶段：接口获取 Agent 知识库准备与同步阶段。

## 知识库用途

本目录用于长期保存接口获取 Agent 采集和整理后的数据库结构信息与接口基础索引信息。

知识库承担两个职责：

1. 为后续 Agent 提供可检索、可复用、可追溯的结构化基础上下文。
2. 作为候选接口和相关数据库结构的定位层，不替代任务阶段的一对一详情获取。

## 目录结构

```text
knowledge_base/
  _schemas/
  sync_reports/
  validation_reports/
  silkroad/
    database/
    apis/
  shark/
    database/
    apis/
  saas/
    database/
    apis/
  callcenter/
    apis/
```

## 数据库知识库同步规则

数据库知识库继续同步数据库结构元信息，只允许保存以下字段：

- 库名
- 表名
- 表注释
- 字段结构
- 字段类型
- 是否可空
- 默认值
- 主键信息
- 索引信息
- 字段注释

数据库同步边界固定如下：

- 只能查询 `information_schema.tables`
- 只能查询 `information_schema.columns`
- 只能查询 `information_schema.statistics`
- 不允许导出任何业务数据
- 不允许对业务表执行 `select *`

数据库主文件固定写入：

- `knowledge_base/<system>/database/<db_name>.json`

## 接口知识库同步规则

接口知识库只做基础接口索引同步，不同步完整接口契约。

接口基础索引固定包含以下字段：

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

接口主索引固定要求：

- `sync_mode` 必须为 `basic_api_index`
- `detail_fetch_policy` 必须明确说明：请求头、请求参数、请求体、响应体、示例和 schema 不保存在接口主索引中，只能由 Agent3 在处理具体接口时，针对本次涉及的接口一对一从 Apifox、接口文档或代码实现中按需获取，不允许在知识库同步阶段全量拉取或保存所有接口详情

接口主文件固定写入：

- `knowledge_base/<system>/apis/apifox_project_<project_id>.json`

## 接口主索引中禁止保存的内容

接口知识库主索引中不得保存以下完整详情：

- `headers`
- `path_params`
- `query_params`
- `request_body`
- `response_body`
- `examples.request`
- `examples.response`
- `components.schemas`
- 以及其他完整请求/响应/schema 契约内容

## Agent3 使用规则

Agent3 只能按以下流程使用接口知识库：

1. 先读取接口基础索引定位候选接口。
2. 再只针对本次命中的接口一对一获取详情。
3. 详情来源仅限 Apifox、接口文档或代码实现。
4. 不允许在 Agent3 主流程中全量获取整个项目的所有接口详情。
5. 无法确认的接口字段不得猜测，必须标记为“待确认”。

## 补证与同步报告

- 同步报告写入 `sync_reports/`，用于记录本次同步成功、失败和生成文件情况。
- 验证补证写入 `validation_reports/`，用于记录运行过程中核实出的事实、冲突项和阻塞项。

`validation_reports/` 只是补充说明，不替代数据库主文件或接口主索引主文件。

## 安全规则

- 不保存数据库明文密码
- 不保存 Apifox、TAPD 等平台令牌
- 不导出业务数据
- 不在日志或报告中打印密钥
- 所有知识文件必须包含 `file_info`

## 维护规则

- 新增系统：新增系统目录和 README，并在来源配置中登记。
- 新增数据库：在对应系统 `database/` 下新增 `<db_name>.json`。
- 新增 Apifox 项目：在对应系统 `apis/` 下新增 `apifox_project_<project_id>.json`。
- 更新数据库知识：重新采集元数据后覆盖主文件，并输出同步报告。
- 更新接口知识：重新同步基础索引后覆盖主文件，并输出同步报告。
- 运行中发现新事实或冲突：写入 `validation_reports/`。
