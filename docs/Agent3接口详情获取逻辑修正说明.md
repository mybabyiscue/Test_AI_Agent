# Agent 3 接口详情获取逻辑修正说明

## 修改内容

- 修正 `ApiMapperAgent`，让 Agent 3 在接口映射输出中包含请求头、Query 参数、Path 参数、完整请求体、完整响应体、鉴权方式、接口描述和接口详情获取状态。
- 新增递归 schema 展开逻辑，支持 `$ref`、`allOf`、`oneOf`、`anyOf`，避免把引用结构原样输出给后续流程。
- 修正 Orchestrator：当输入是 Apifox 基础知识库索引时，先保留该索引用于定位，再根据 `project_id/source_url` 通过 Apifox 凭证重新获取完整 OpenAPI，并将完整文档交给 Agent 3。
- 修正 `ApiDocumentResolver`：统一通过 Apifox 个人令牌获取项目 OpenAPI，并对权限、URL、网络和字段缺失问题给出明确错误分类。
- 重写 `prompts/api_mapper.md`，明确“知识库定位”和“Apifox 详情获取”是 Agent 3 的两个必经步骤。

## 修改原因

此前 Agent 3 的实现只把测试用例映射到接口路径和 HTTP 方法，输出中没有完整请求头、请求体和响应体。若输入来自基础知识库索引，流程也没有强制通过 Apifox 个人令牌再次获取详细定义，导致接口信息不完整。

## 修改结果

- Agent 3 不再只停留在接口名称和路径层面。
- 通过 Apifox 获取到的 OpenAPI 会被递归展开后输出。
- 基础知识库索引只用于候选接口定位，不再作为最终接口详情来源。
- 新增测试覆盖了“完整接口详情输出”和“基础知识库索引必须经 Apifox 详情获取再进入 Agent 3”两个场景。
- 本次修正未生成自动化脚本，未执行自动化测试阶段。
