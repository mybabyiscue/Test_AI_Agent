# 接口与数据库结构知识库

## 文件说明

- 文件名称：`README.md`
- 文件作用：说明本地知识库的用途、目录结构、维护规则和安全边界。
- 文件主要内容：包含系统目录规划、数据库结构文件、Apifox 接口文件、Schema 目录、更新/删除/查询原则和密钥安全要求。
- 所属阶段：接口获取 Agent 知识库准备阶段。

## 知识库用途

本目录用于长期保存接口获取 Agent 采集和整理后的接口信息与数据库结构信息。

这些文件会为后续测试用例 Agent 和接口自动化 Agent 提供真实、完整、可维护的上下文。

## 目录结构

```text
knowledge_base/
  _schemas/
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

## 安全规则

- 不保存数据库明文密码。
- 不保存 Apifox、TAPD 等平台令牌。
- 不导出业务数据。
- 数据库只采集 `information_schema` 结构信息。
- 所有知识文件必须包含 `file_info` 中文说明。

## 文件维护规则

- 新增系统：新增系统目录和 README。
- 新增数据库：在系统 `database/` 下新增 `<db_name>.json`。
- 新增 Apifox 项目：在系统 `apis/` 下新增 `apifox_project_<project_id>.json`。
- 更新知识：重新采集后覆盖主文件，并生成差异记录。
- 删除知识：按系统、库名或项目 ID 删除对应文件，并记录删除原因。
