# AI API Testing Pipeline MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first runnable MVP of a document-driven AI API testing pipeline with 4 agent prompt templates, JSON Schemas, a deterministic orchestrator demo, and basic verification tests.

**Architecture:** Use a Python `src` layout with a lightweight orchestrator, file-based artifact store, deterministic agent implementations for MVP, and generated pytest API tests that skip cleanly when no target environment is configured. Keep the runtime dependency-light so the workspace can run immediately without a separate install step.

**Tech Stack:** Python 3.12, pytest, standard library JSON/pathlib/subprocess/dataclasses, Markdown prompt templates, JSON Schema files

---

### Task 1: Bootstrap project metadata and failing tests

**Files:**
- Create: `E:/xjcode/Test_AI_Agent/pyproject.toml`
- Create: `E:/xjcode/Test_AI_Agent/README.md`
- Create: `E:/xjcode/Test_AI_Agent/tests/conftest.py`
- Create: `E:/xjcode/Test_AI_Agent/tests/test_pipeline_demo.py`
- Create: `E:/xjcode/Test_AI_Agent/tests/test_schema_registry.py`
- Create: `E:/xjcode/Test_AI_Agent/tests/test_prompt_registry.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_demo_pipeline_creates_manifest_and_stage_outputs(tmp_path):
    ...

def test_schema_registry_contains_required_schemas():
    ...

def test_prompt_registry_contains_four_agent_templates():
    ...
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest -q`
Expected: FAIL because the `ai_pipeline` package and registry modules do not exist yet

- [ ] **Step 3: Add minimal project metadata**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 4: Re-run tests and confirm failures still point to missing implementation**

Run: `pytest -q`
Expected: FAIL with import or attribute errors, not syntax errors

### Task 2: Add prompt templates, example inputs, and schema files

**Files:**
- Create: `E:/xjcode/Test_AI_Agent/prompts/requirement_analyst.md`
- Create: `E:/xjcode/Test_AI_Agent/prompts/testcase_designer.md`
- Create: `E:/xjcode/Test_AI_Agent/prompts/api_mapper.md`
- Create: `E:/xjcode/Test_AI_Agent/prompts/automation_engineer.md`
- Create: `E:/xjcode/Test_AI_Agent/examples/requirements/sample_requirement.md`
- Create: `E:/xjcode/Test_AI_Agent/examples/apis/sample_openapi.json`
- Create: `E:/xjcode/Test_AI_Agent/schemas/requirement_model.schema.json`
- Create: `E:/xjcode/Test_AI_Agent/schemas/test_cases.schema.json`
- Create: `E:/xjcode/Test_AI_Agent/schemas/endpoint_mapping.schema.json`
- Create: `E:/xjcode/Test_AI_Agent/schemas/automation_plan.schema.json`
- Create: `E:/xjcode/Test_AI_Agent/schemas/execution_report.schema.json`

- [ ] **Step 1: Add the prompt templates with explicit role boundaries**

```markdown
# Requirement Analyst
You are the requirement analyst agent...
```

- [ ] **Step 2: Add example requirement and API documents**

```markdown
# 用户注册
- 用户可以创建账号
```

```json
{
  "openapi": "3.0.0",
  "paths": {
    "/users": {
      "post": {
        "summary": "Create user"
      }
    }
  }
}
```

- [ ] **Step 3: Add schema files that match the planned artifact contracts**

```json
{
  "type": "object",
  "required": ["requirement_id", "title", "scenarios"]
}
```

- [ ] **Step 4: Keep tests pending for missing registry implementation**

Run: `pytest -q`
Expected: FAIL because registry code has not been implemented yet

### Task 3: Implement registries, artifact store, and orchestrator domain models

**Files:**
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/__init__.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/contracts.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/config.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/schema_registry.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/prompt_registry.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/artifact_store.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/openapi_loader.py`

- [ ] **Step 1: Implement schema and prompt registries**

```python
class SchemaRegistry:
    def get_required_schema_names(self) -> list[str]:
        return [...]
```

- [ ] **Step 2: Implement typed contracts for pipeline context and results**

```python
@dataclass(slots=True)
class PipelineRun:
    run_id: str
    run_dir: Path
```

- [ ] **Step 3: Implement file-based artifact writing helpers**

```python
def write_json(self, relative_path: str, payload: dict[str, Any]) -> Path:
    ...
```

- [ ] **Step 4: Run tests to verify registry behavior starts passing**

Run: `pytest tests/test_schema_registry.py tests/test_prompt_registry.py -q`
Expected: PASS

### Task 4: Implement deterministic MVP agents and end-to-end pipeline execution

**Files:**
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/agents/__init__.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/agents/requirement_agent.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/agents/testcase_agent.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/agents/api_mapper_agent.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/agents/automation_agent.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/orchestrator.py`
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/cli.py`

- [ ] **Step 1: Write the pipeline behavior expected by the end-to-end test**

```python
result = orchestrator.run_demo(tmp_path)
assert result.manifest["stages"] == [...]
```

- [ ] **Step 2: Implement deterministic requirement, testcase, mapping, and automation agents**

```python
class RequirementAgent:
    def run(...):
        return {"requirement_id": "REQ-001", ...}
```

- [ ] **Step 3: Generate pytest scripts that skip cleanly without `API_BASE_URL`**

```python
pytestmark = pytest.mark.skipif(not BASE_URL, reason="Set API_BASE_URL to execute generated API tests.")
```

- [ ] **Step 4: Execute generated tests via subprocess and persist an execution report**

```python
completed = subprocess.run([...], capture_output=True, text=True, check=False)
```

- [ ] **Step 5: Run the focused end-to-end test**

Run: `pytest tests/test_pipeline_demo.py -q`
Expected: PASS

### Task 5: Finalize docs, verify the whole MVP, and record usage instructions

**Files:**
- Modify: `E:/xjcode/Test_AI_Agent/README.md`
- Modify: `E:/xjcode/Test_AI_Agent/docs/superpowers/specs/2026-04-17-ai-api-testing-pipeline-design.md`
- Modify: `E:/xjcode/Test_AI_Agent/docs/superpowers/plans/2026-04-17-ai-api-testing-pipeline-mvp.md`

- [ ] **Step 1: Document the actual directory structure and demo command**

```bash
python -m ai_pipeline.cli --run-demo --workspace ./workspace
```

- [ ] **Step 2: Run the complete verification suite**

Run: `pytest -q`
Expected: PASS

- [ ] **Step 3: Review outputs and confirm they match the MVP scope**

Check:
- prompt templates exist
- schema files exist
- pipeline creates stage artifacts
- generated pytest scripts are produced
- execution report is written

- [ ] **Step 4: Inline execution choice**

The user already requested direct inline execution in the current directory, so proceed with implementation here instead of pausing for execution mode selection.
