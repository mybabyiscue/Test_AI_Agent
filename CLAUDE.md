# AI 接口测试流水线

多 Agent 串行执行的接口测试流水线，4 个 Agent 按固定顺序执行：
`requirement_agent -> testcase_agent -> api_mapper_agent -> automation_agent`

## 快速命令

```bash
# 运行 Demo
python run_demo.py --run-demo --workspace ./workspace

# 运行测试
pytest -q

# 运行指定测试文件
pytest tests/test_orchestrator_stage_gates.py -v

# 知识库同步（全量）
python scripts/sync_knowledge.py

# 知识库同步（指定系统）
python scripts/sync_knowledge.py --system silkroad
python scripts/sync_knowledge.py --system saas --db-only
python scripts/sync_knowledge.py --system silkroad --db center
python scripts/sync_knowledge.py --system saas --project 4152663
```

## Skill 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/sync-knowledge` | 知识库同步 | `/sync-knowledge 丝路数据库`、`/sync-knowledge saas接口`、`/sync-knowledge 全部` |

## 用户必读：各阶段核心产物

| 阶段 | 必看文件 | 说明 |
|------|----------|------|
| Agent 1 需求分析 | `requirement_agent/output/business_flow.md` | 业务流程说明 |
| Agent 1 需求分析 | `requirement_agent/output/requirement_model.json` | 结构化需求模型 |
| Agent 2 测试用例 | `testcase_agent/output/test_cases.json` | 完整测试用例 |
| Agent 2 测试用例 | `testcase_agent/output/coverage_report.md` | 覆盖率说明 |
| Agent 3 接口映射 | `api_mapper_agent/output/mappings/endpoint_mapping.md` | 用例→接口映射 |
| Agent 3 接口映射 | `api_mapper_agent/output/apis/api_catalog.md` | 接口详情（请求体/响应体） |
| Agent 3 接口映射 | `api_mapper_agent/output/mappings/database_mapping.md` | 用例→数据库表映射 |
| Agent 4 自动化 | `automation_agent/output/execution_report.json` | 执行结果 |
| 全局 | `summary/manifest.json` | 运行总状态 |
| 全局 | `summary/blocking_report.json` | 阻断原因（如有） |

> `.json` 给程序消费，`.md` 给人阅读。优先看 `.md` 文件。

## 项目结构

```
src/ai_pipeline/               # 核心流水线代码
  orchestrator.py              # 流水线编排器（阶段门禁、顺序执行）
  agent_runner.py              # Agent 子进程执行器（含 LLM 调用与 fallback）
  llm_backend.py               # LLM 后端（Anthropic API，含多策略 JSON 提取）
  stage_gates.py               # 阶段门禁检查（职责识别、完成验证、越权检测）
  report_renderer.py           # 报告渲染（追溯链路、产物清单、文件说明）
  prompt_builder.py            # Prompt 构建（含 few-shot 示例）
  fallback_templates.py        # 降级模板加载器（从 knowledge_base 读取 JSON 模板）
  agents/                      # 4 个 Agent 实现（均继承 BaseAgent）
    base_agent.py              # Agent 基类（agent_name、role_profile、run 接口）
    requirement_agent.py       # Agent 1：需求分析
    testcase_agent.py          # Agent 2：测试用例设计
    api_mapper_agent.py        # Agent 3：接口映射
    automation_agent.py        # Agent 4：自动化脚本生成与执行
    allure_helper.py           # Allure 报告生成与查看指南
    test_generator.py          # pytest 测试文件生成（含 schema 示例值填充）
  platforms/apifox.py          # Apifox 平台集成
  credentials.py               # 凭证管理
  knowledge_sync.py            # 知识库同步
roles/                         # Agent 职责定义文件（Markdown）
prompts/                       # Agent Prompt 模板
schemas/                       # JSON Schema 定义
config/                        # 配置文件
  credentials.local.json       # （已 gitignore）平台令牌、数据库凭证、LLM 配置
  test_environment.local.json  # （已 gitignore）测试环境与登录账号
knowledge_base/                # 项目知识库（接口、数据库结构、同步报告）
  fallback_templates/          # 降级模板 JSON 文件（按 agent_name 分目录）
workspace/                     # 运行时工作区（已 gitignore）
tests/                         # pytest 测试套件
scripts/                       # 工具脚本
  sync_knowledge.py            # 知识库同步（支持全量/增量/指定库/指定项目）
.claude/commands/              # Claude Code Skill 命令
  sync-knowledge.md            # 知识库同步 skill
```

## Agent 职责边界

### Agent 1：requirement_agent（需求分析）

- **职责文件**：`roles/requirement_agent.md`
- **负责**：需求分析、结构化需求整理、验收标准提炼、风险点识别
- **输出**：`requirement_model.json`、`acceptance_criteria.json`、`business_flow.md`、`risk_points.json`
- **禁止**：测试用例设计、真实接口映射、自动化脚本生成、业务事实脑补

### Agent 2：testcase_agent（测试用例设计）

- **职责文件**：`roles/testcase_agent.md`
- **负责**：基于结构化需求设计测试用例、覆盖矩阵、覆盖说明和追踪关系
- **输出**：`test_cases.json`、`test_points.json`、`test_case_matrix.csv`、`coverage_report.md`
- **禁止**：决定真实接口契约、编写自动化脚本、补造未确认业务规则

### Agent 3：api_mapper_agent（接口映射）

- **职责文件**：`roles/api_mapper_agent.md`
- **负责**：定位候选接口、补齐接口详情、生成接口映射、请求结构和依赖关系
- **输出**：`api_catalog.json`、`endpoint_mapping.json`、`request_schema.json`、`dependency_graph.json` 及配套 md
- **禁止**：替上游修改测试意图、全量乱拉接口、生成自动化脚本、伪造待确认字段

### Agent 4：automation_agent（自动化执行）

- **职责文件**：`roles/automation_agent.md`
- **负责**：在模板和环境确认后生成并执行自动化脚本，输出执行报告
- **输出**：`automation_plan.json`、`generated_tests/test_generated_api_cases.py`、`execution_report.json`
- **禁止**：跳过模板确认、假设凭证和环境、回补前序 Agent 未确认内容、吞掉失败

## 全局执行规则

- 每个 Agent 执行前必须先读取自己的职责 md 文件，并将职责注入 LLM prompt
- 每个 Agent 输出后必须检查生成内容是否符合当前职责要求
- 禁止跨阶段越权执行其他 Agent 的职责
- 禁止将未确认信息包装成确定结论向下游传递
- 禁止使用历史值、默认值或猜测值替代本次用户确认
- 禁止把敏感信息明文写入 Prompt、脚本、日志或报告
- 如遇到需要用户确认的信息，必须暂停并提问，不能自行猜测

## LLM 配置

LLM 后端配置在 `config/credentials.local.json` 的 `llm` 字段：
- `base_url`：API 地址
- `api_key`：API 密钥
- `model`：模型名称（默认 mimo-v2.5-pro，注意全小写）
- 超时默认 10 秒，API 不可用时自动降级到硬编码逻辑
- 可通过环境变量 `AI_PIPELINE_LLM_ENABLED=0` 禁用 LLM
- JSON 解析支持 4 种策略：原始 JSON、花括号提取、代码块提取、最大 JSON 对象
- LLM 输出部分字段时自动合并，不会因缺少字段而整体丢弃

## 关键约定

- Python 3.12+，使用 `from __future__ import annotations`
- 测试使用 pytest，conftest.py 将 `src/` 加入 sys.path
- 凭证仅通过环境变量或 `config/credentials.local.json` 提供，禁止写入代码
- 编排器在任何 Agent 阶段门禁失败时阻断流水线
- 使用相同 `run_id` 重新运行会先清理旧产物
- 所有 Agent 继承 `BaseAgent` 基类，统一 `agent_name`、`role_profile()`、`run()` 接口
- 降级模板存放在 `knowledge_base/fallback_templates/` 目录，按 agent_name 分子目录
