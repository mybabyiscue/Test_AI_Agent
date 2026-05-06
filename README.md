# AI API Testing Pipeline MVP

这是一个面向接口测试场景的 AI 多 Agent 流水线 MVP。

当前版本已经具备这些核心能力：

- 4 个 Agent Prompt 模板
- 5 份核心 JSON Schema
- 示例需求文档与示例 OpenAPI 文档
- 基于 Orchestrator 的流水线执行
- 4 个 Agent 的独立工作空间
- 4 个 Agent 的子进程执行模型
- 自动生成 pytest 风格接口脚本
- 自动生成执行报告与追踪报告

## 快速运行

运行 Demo：

```bash
python run_demo.py --run-demo --workspace ./workspace
```

使用 Apifox URL 获取接口资产：

```bash
set AI_PIPELINE_CREDENTIAL_APIFOX_TOKEN=your_apifox_access_token
python run_demo.py --requirement ./examples/requirements/sample_requirement.md --api-source-url "https://app.apifox.com/project/123456/api-789" --workspace ./workspace --run-id apifox-run
```

注意：真实令牌只允许通过环境变量或后续凭证配置层提供，禁止写入 Prompt、脚本或代码仓库。

运行测试：

```bash
pytest -q
```

## 配置说明

项目中的真实令牌、数据库密码和测试账号都应该放在本地私有配置里，不要直接写进仓库。

### 1. 平台令牌与数据库凭证

优先使用本地文件：

- `config/credentials.local.json`

可先参考：

- `config/credentials.example.json`

这个本地文件已被 `.gitignore` 忽略，适合填写：

- Apifox、TAPD 等平台个人令牌
- 各系统数据库连接信息

示例：

```json
{
  "platforms": {
    "apifox": {
      "default": {
        "token": "your_apifox_access_token"
      }
    },
    "tapd": {
      "default": {
        "token": "your_tapd_personal_token"
      }
    }
  },
  "databases": {
    "saas": {
      "type": "mysql",
      "host": "127.0.0.1",
      "port": 3306,
      "user": "root",
      "password": "your_password",
      "description": "SAAS local database"
    }
  }
}
```

如果你更习惯环境变量，也可以直接设置：

```bash
set AI_PIPELINE_CREDENTIAL_APIFOX_TOKEN=your_apifox_access_token
set AI_PIPELINE_CREDENTIAL_TAPD_TOKEN=your_tapd_personal_token
set SAAS_DB_HOST=127.0.0.1
set SAAS_DB_PORT=3306
set SAAS_DB_USER=root
set SAAS_DB_PASSWORD=your_password
```

### 2. 测试环境与登录账号

使用本地文件：

- `config/test_environment.local.json`

可先参考：

- `config/test_environment.example.json`

这个文件同样已被 `.gitignore` 忽略，适合填写：

- API 基础地址
- 前台/后台登录账号密码
- 登录接口路径
- Token 提取路径和请求头配置

启用某个环境配置时，可设置：

```bash
set AI_PIPELINE_TEST_ENV_PROFILE=local
```

### 3. 知识源配置

`config/knowledge_sources.example.json` 只用于登记知识来源、项目地址、库名和环境变量名，不应填写真实密码或真实 Token。

## 目录结构

```text
docs/
examples/
prompts/
schemas/
src/ai_pipeline/
tests/
run_demo.py
```

## 用户必读：各阶段核心产物

每次运行完成后，你需要查看以下文件来确认各阶段输出是否正确。

### Agent 1：需求分析

| 文件 | 说明 |
|------|------|
| `requirement_agent/output/requirement_model.json` | 结构化需求模型（子需求、验收条件、业务规则） |
| `requirement_agent/output/acceptance_criteria.json` | 验收标准清单 |
| `requirement_agent/output/business_flow.md` | 业务流程说明（可读性最好） |
| `requirement_agent/output/risk_points.json` | 风险点与待确认项 |

### Agent 2：测试用例设计

| 文件 | 说明 |
|------|------|
| `testcase_agent/output/test_cases.json` | 完整测试用例（含 payload、预期状态码） |
| `testcase_agent/output/test_points.json` | 测试点清单 |
| `testcase_agent/output/test_case_matrix.csv` | 用例矩阵（Excel 可直接打开） |
| `testcase_agent/output/coverage_report.md` | 覆盖率说明（可读性最好） |

### Agent 3：接口映射

| 文件 | 说明 |
|------|------|
| `api_mapper_agent/output/mappings/endpoint_mapping.md` | 测试用例到接口的映射关系（必看） |
| `api_mapper_agent/output/apis/api_catalog.md` | 接口详情：请求体、响应体、鉴权方式（必看） |
| `api_mapper_agent/output/apis/request_schema.md` | 请求结构摘要 |
| `api_mapper_agent/output/mappings/database_mapping.md` | 测试用例到数据库表的映射 |
| `api_mapper_agent/output/mappings/dependency_graph.md` | 接口依赖关系 |
| `api_mapper_agent/output/mappings/missing_database_report.md` | 缺失数据库表/字段报告 |

### Agent 4：自动化执行

| 文件 | 说明 |
|------|------|
| `automation_agent/output/execution_report.json` | 执行结果（通过/失败/错误详情） |
| `automation_agent/output/generated_tests/test_generated_api_cases.py` | 生成的 pytest 脚本 |
| `automation_agent/output/automation_plan.json` | 自动化执行计划 |

### 全局汇总

| 文件 | 说明 |
|------|------|
| `summary/manifest.json` | 本次运行总状态（completed/blocked） |
| `summary/blocking_report.json` | 阻断原因（如有） |
| `summary/traceability_report.md` | 需求→用例→接口→脚本全链路追溯 |

> 提示：每个 Agent 的 `output/` 下同时有 `.json` 和 `.md` 两种格式。`.json` 给程序消费，`.md` 给人阅读。优先看 `.md` 文件。

## 每次运行的产物结构

每次运行都会生成一个 `run_id` 目录，例如：

```text
workspace/
  runs/
    demo-run/
      manifest.json
      event_log.jsonl
      requirement_agent/
        input/
        output/
        logs/
        state.json
      testcase_agent/
        input/
        output/
        logs/
        state.json
      api_mapper_agent/
        input/
        output/
        logs/
        state.json
      automation_agent/
        input/
        output/
        logs/
        state.json
      reports/
```

含义如下：

- `manifest.json`：本次运行总清单
- `event_log.jsonl`：全局事件流，记录每个 stage 的开始、完成、退出码和命令
- `<agent>/input/`：该 Agent 本次执行的输入
- `<agent>/output/`：该 Agent 本次执行的产出
- `<agent>/logs/`：该 Agent 子进程日志
- `<agent>/state.json`：该 Agent 的状态、时间、输入输出清单、执行命令、PID、退出码
- `reports/`：全局追踪报告和最终摘要

每个 Agent 的 `output/` 下都会单独生成职责说明：

- `role_profile.md`：给人阅读的 Markdown 职责卡
- `role_profile.json`：给程序读取和审计的结构化职责数据

这两份文件都只存在于当前 Agent 自己的空间中，互相不会覆盖，后续新增 Agent 时也可以按同样结构扩展。

## 当前执行模型

当前版本不是“4 个类顺序调用”而已，而是：

1. Orchestrator 创建本次 `run_id`
2. 为每个 Agent 准备独立工作空间
3. 由 Orchestrator 启动独立 Python 子进程执行单个 Agent
4. 子进程完成后，把输出写回对应 `output/`
5. Orchestrator 更新 `state.json` 和 `event_log.jsonl`
6. 最后汇总生成追踪报告

这意味着你后续排查问题时，可以按 Agent 粒度定位。

## 重跑行为

如果你用同一个 `run_id` 重新执行，例如 Demo 的 `demo-run`，系统会先清理旧的该次运行目录，再重新生成新产物。

这样可以避免：

- 历史文件混入新结果
- 旧报告误导排查
- 旧测试脚本污染当前执行

## 你怎么排查一个失败的流程

推荐顺序：

1. 先看 `manifest.json`
2. 再看 `event_log.jsonl`
3. 定位到失败 Agent 的 `state.json`
4. 查看对应 `logs/worker_stdout.log` 和 `logs/worker_stderr.log`
5. 查看对应 `output/` 里的结构化工件

## 当前 MVP 边界

当前版本重点是先打通工程闭环，而不是直接接入真实生产级大模型和真实测试环境。

当前已经能完成：

1. 读取需求文档
2. 生成结构化需求工件
3. 生成测试用例
4. 解析 OpenAPI 文档并映射接口
5. 生成 pytest 接口脚本
6. 执行生成脚本
7. 输出执行报告和追踪报告

## 后续推荐升级

- 接入真实 LLM Provider
- 接入真实环境配置与鉴权
- 增强 Markdown/API 文档解析
- 增加阶段失败重试与断点续跑
- 增加 Web/API 服务层
- 增加任务队列与并发调度
