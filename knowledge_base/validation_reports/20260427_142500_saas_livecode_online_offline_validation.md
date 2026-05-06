# SAAS 活码与获客链接自动上线/手动上下线补证报告

## 文件说明
- 文件名称：`20260427_142500_saas_livecode_online_offline_validation.md`
- 文件作用：沉淀本次“活码和链接自动上线与手动上下线”需求在 SAAS / 鲨域接口知识中的最新核实结论。
- 文件主要内容：目标接口清单、已确认契约、鉴权头补证、需求与接口文档冲突项、未补齐链路。
- 所属阶段：知识库验证与补证阶段。

## 来源说明
- 本报告基于本地知识库 `knowledge_base/saas/apis/apifox_project_4152663.json`。
- 本报告同时参考本次流程归档中的 Agent3 主文档与接口补证结果。
- 本报告不保存明文敏感信息；涉及 `CurrentUser` 的示例结构已做字段级说明，不保留可直接复用的账号值。

## 本次核实范围
- `POST /contact/way/save`
- `GET /contact/way/getId`
- `POST /contact/way/list`
- `POST /acquisition/link/saveOrUpdate`
- `GET /acquisition/link/detail`
- `POST /acquisition/link/list`
- `GET /acquisition/user/online/list`
- `POST /acquisition/user/online/change`

## 已确认事实
1. 上述 8 个接口都声明了 `CurrentUser` 请求头。
2. `CurrentUser` 在当前 OpenAPI 示例中表现为十六进制编码字符串，解码后对应用户上下文 JSON 结构。
3. 当前可确认的 `CurrentUser` 结构字段至少包括：
- `UserId`
- `Account`
- `Name`
- `OrgId`
- `TenantId`
4. 渠道活码链路已明确命中 `nextAutoEnableTime`：
- `POST /contact/way/save`
- `GET /contact/way/getId`
5. 员工上下线核心 HTTP 链路已明确：
- 查询：`GET /acquisition/user/online/list`
- 变更：`POST /acquisition/user/online/change`
6. `POST /acquisition/user/online/change` 的请求体关键字段已明确为：
- `corpId`
- `userId`
- `status`

## 需求与接口文档冲突
当前获客链接相关 3 个接口未在已核实 OpenAPI 中命中 `nextAutoEnableTime`：
- `POST /acquisition/link/saveOrUpdate`
- `GET /acquisition/link/detail`
- `POST /acquisition/link/list`

这与“获客链接新增/编辑、详情、列表支持自动上线时间保存与回显”的需求描述不一致。当前应视为真实冲突，而不是简单的“还没找到”。

## 当前仍未补齐的链路
1. `CurrentUser` 的真实生成规则未落地：
- 已确认它是必需头之一。
- 但仍不能从当前知识库直接推导出真实环境中的换取方式、签名方式或联动规则。
2. RocketMQ 自动上线链路未补齐：
- 未确认消息投递入口。
- 未确认消费入口。
- 未确认 topic/tag/消息体。
3. 旧消息因 `next_auto_enable_time` 不一致而丢弃的观测链路未补齐。
4. 自动上线后“重新同步企微”的真实调用链路未补齐。

## 候选但未证实的信息
本地 API 索引中可见下列候选接口，但当前不能直接视为本需求正式依赖链路：
- `POST /auth/ua/admin_login`
- `POST /ua/admin_login`
- `POST /auth/ua/token/refresh`
- `POST /cp/org/synchro`
- `POST /cp/org/synchro/{corpId}`

这些接口目前只能作为后续排查线索，不能直接当作执行依据写入自动化流程。

## 对知识库使用方的建议
1. 当需求涉及获客链接自动上线时间时，先检查 `apifox_project_4152663.json` 是否已补齐 `nextAutoEnableTime`。
2. 当接口仅声明 `CurrentUser` 而未给出换取规则时，不要直接构造真实请求，应继续补证鉴权来源。
3. 当需求涉及 MQ 自动上线、旧消息丢弃或企微同步时，不应仅凭当前 SAAS 接口知识库直接进入自动化执行。

## 本次更新结论
- SAAS 知识库中关于这批接口的最新状态，已经从“候选路径级认知”提升到“8 个目标接口的 HTTP 契约与主要冲突项已核实”。
- 但该知识仍不足以直接支撑自动化执行，需要把鉴权来源、MQ 链路和企微同步链路继续补齐。
