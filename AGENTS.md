# agents:Test_AI_Agents

本项目采用多 Agent 串行执行，固定顺序为：`agent1 -> agent2 -> agent3 -> agent4`。
当前代码中的实际阶段映射为：
- `agent1 = requirement_agent`
- `agent2 = testcase_agent`
- `agent3 = api_mapper_agent`
- `agent4 = automation_agent`

## 职责文件路径

- `agent1` 职责文件：`roles/requirement_agent.md`
- `agent2` 职责文件：`roles/testcase_agent.md`
- `agent3` 职责文件：`roles/api_mapper_agent.md`
- `agent4` 职责文件：`roles/automation_agent.md`

## 全局执行规则

- 每个 Agent 执行前，必须先读取自己的职责 md 文件。
- 每个 Agent 执行前，必须将职责内容注入当前 Agent 的 LLM prompt。
- 职责不能只存在于 Python 文件、日志、校验、阻塞判断或产物落盘中。
- 每个 Agent 执行时，必须先进行职责确认，再开始正式输出。
- 每个 Agent 输出后，必须检查生成内容是否符合当前职责要求。
- 不要只检查是否生成了文档，还要检查文档内容是否符合当前 Agent 职责。
- 每执行完一个 Agent，都要告诉用户：生成了哪些文档、文档用途、内容概要、检查结果。
- 如遇到需要用户确认的信息，必须暂停并提问，不能自行猜测。
- `agent4` 如需模板，必须先向用户确认模板信息，不能自行假设。

## Agent 职责边界

- `agent1`
  - 负责：需求分析、结构化需求整理、验收标准提炼、风险点识别。
  - 输出：`requirement_model.json`、`acceptance_criteria.json`、`business_flow.md`、`risk_points.json`。
  - 不应做：测试用例设计、真实接口映射、自动化脚本生成、业务事实脑补。
- `agent2`
  - 负责：基于结构化需求设计测试用例、覆盖矩阵、覆盖说明和追踪关系。
  - 输出：`test_cases.json`、`test_case_matrix.csv`、`coverage_report.md`。
  - 不应做：决定真实接口契约、编写自动化脚本、补造未确认业务规则。
- `agent3`
  - 负责：定位候选接口、补齐接口详情、生成接口映射、请求结构和依赖关系。
  - 输出：`api_catalog.json`、`api_source_request.json`、`endpoint_mapping.json`、`request_schema.json`、`dependency_graph.json` 及配套 md。
  - 不应做：替上游修改测试意图、全量乱拉接口、生成自动化脚本、伪造待确认字段。
- `agent4`
  - 负责：在模板和环境确认后生成并执行自动化脚本，输出执行报告。
  - 输出：`automation_plan.json`、`generated_tests/test_generated_api_cases.py`、`execution_report.json`、`failure_summary.md`。
  - 不应做：跳过模板确认、假设凭证和环境、回补前序 Agent 未确认内容、吞掉失败。

## 禁止行为

- 禁止跨阶段越权执行其他 Agent 的职责。
- 禁止将未确认信息包装成确定结论向下游传递。
- 禁止使用历史值、默认值或猜测值替代本次用户确认。
- 禁止把敏感信息明文写入 Prompt、脚本、日志或报告。

## 验收要求

- 当前 Agent 的输出必须可被下游阶段直接消费，或明确阻塞原因。
- 当前 Agent 的结果必须同时通过“文件存在检查”和“职责符合性检查”。
- 每个阶段完成后，必须能向用户说明：产物名称、产物用途、内容概要、检查结论。
