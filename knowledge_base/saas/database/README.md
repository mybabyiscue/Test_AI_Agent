# SAAS / 享佳云 数据库结构知识目录

## 文件说明
- 文件名称：README.md
- 文件作用：说明 SAAS / 享佳云 系统数据库结构知识文件的存放位置和维护方式。
- 文件主要内容：数据库范围、当前数据库结构文件、维护规则和安全边界。
- 所属阶段：Agent 3：接口与数据结构上下文获取阶段。
- 查看方式：直接用 VS Code、Typora、Markdown Preview 或记事本打开。

## 系统名称
- 稳定系统标识：`saas`
- 展示名称：`SAAS / 享佳云`
- 可识别别名：`SAAS`、`享佳云`、`xiangjiayun`

## 数据库范围规则
- 本目录只代表 SAAS / 享佳云 数据库结构知识库。
- 虽然运行记录目录对 `鲨域 / SAAS / 享佳云` 统一使用 `saas` 标识，但数据库结构不合并。
- 用户明确说 `鲨域` 时，数据库信息获取 Agent 必须使用 `knowledge_base/shark/database`。
- 用户明确说 `SAAS` 或 `享佳云` 时，数据库信息获取 Agent 使用本目录。

## 当前数据库结构文件
- `contact.json`
- `customer.json`
- `ec.json`
- `etl.json`
- `saas.json`
- `scrm.json`
- `shark.json`
- `shop.json`
- `sop.json`

## 安全说明
- 本目录只保存数据库结构信息。
- 不保存数据库账号密码。
- 不导出业务数据。
- 不包含表内记录。
