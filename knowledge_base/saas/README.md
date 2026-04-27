# SAAS / 享佳云 / 鲨域 系统知识库

## 文件说明
- 文件名称：README.md
- 文件作用：说明 SAAS / 享佳云 / 鲨域 在知识库中的命名、归档和使用规则。
- 文件主要内容：系统名称、系统别名、运行记录目录规则、接口知识目录、数据库结构目录、安全边界和查看方式。
- 所属阶段：Agent 3：接口与数据结构上下文获取阶段。
- 查看方式：直接用 VS Code、Typora、Markdown Preview 或记事本打开。

## 系统名称
- 稳定系统标识：`saas`
- 展示名称：`SAAS / 享佳云 / 鲨域`
- 可识别别名：`SAAS`、`享佳云`、`鲨域`、`xiangjiayun`、`shark`

## 运行记录目录规则
- 后续用户提到 `SAAS`、`享佳云`、`鲨域`、`xiangjiayun`、`shark` 时，新需求运行记录目录统一使用稳定系统标识 `saas`。
- 示例：同一份需求不再分别生成 `*-saas-*` 和 `*-shark-*` 两套运行目录。
- 用户原始叫法需要写入报告说明，例如 `source_scope=鲨域`，但不参与运行目录命名。

## 数据库范围规则
- 数据库结构仍然需要区分，不随运行目录合并。
- 用户明确说 `鲨域` 时，数据库信息获取 Agent 使用 `knowledge_base/shark/database`。
- 用户明确说 `SAAS` 或 `享佳云` 时，数据库信息获取 Agent 使用 `knowledge_base/saas/database`。
- 也就是说：运行目录统一归到 `saas`，但数据库上下文按用户原始系统范围选择。

## 目录说明
- `apis/`：保存 SAAS / 享佳云 / 鲨域相关接口知识文件。
- `database/`：保存 SAAS / 享佳云相关数据库结构知识文件。
- 鲨域数据库结构文件不放在本目录，仍保留在 `knowledge_base/shark/database`。

## 当前规划
- 接口来源：Apifox 项目 `4152663`。
- SAAS / 享佳云数据库结构：`contact`、`customer`、`ec`、`etl`、`saas`、`scrm`、`shark`、`shop`、`sop`。
- 鲨域数据库结构：仍以 `knowledge_base/shark/database` 为准。

## 安全说明
- 不保存 Apifox Token。
- 不保存数据库明文密码。
- 不保存业务数据。
- 数据库目录只保存表结构、字段结构和索引结构。
