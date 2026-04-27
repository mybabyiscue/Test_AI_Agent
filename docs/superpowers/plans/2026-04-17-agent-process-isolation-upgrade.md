# Agent Process Isolation Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the MVP so each agent stage runs in its own Python subprocess, records richer execution metadata, and rebuilds the target run directory cleanly before each execution.

**Architecture:** Keep the current orchestrator-driven pipeline and per-agent workspaces, but move stage execution into a dedicated `agent_runner` module invoked by subprocess. The orchestrator will prepare stage inputs, spawn the worker process, then load outputs from the stage workspace and update the global manifest and reports.

**Tech Stack:** Python 3.12, pytest, pathlib, subprocess, json, dataclasses

---

### Task 1: Add failing tests for subprocess execution metadata and clean reruns

**Files:**
- Modify: `E:/xjcode/Test_AI_Agent/tests/test_pipeline_demo.py`

- [ ] **Step 1: Write failing tests**

```python
def test_demo_pipeline_rebuilds_existing_run_directory(tmp_path):
    ...

def test_stage_state_records_subprocess_execution_metadata(tmp_path):
    ...
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_pipeline_demo.py -q`
Expected: FAIL because rerun cleanup and subprocess execution metadata are not implemented yet

### Task 2: Implement stage subprocess runner and orchestrator integration

**Files:**
- Create: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/agent_runner.py`
- Modify: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/orchestrator.py`
- Modify: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/artifact_store.py`
- Modify: `E:/xjcode/Test_AI_Agent/src/ai_pipeline/agents/automation_agent.py`

- [ ] **Step 1: Add a standalone stage runner entrypoint**
- [ ] **Step 2: Make orchestrator prepare inputs and invoke stage workers by subprocess**
- [ ] **Step 3: Persist execution metadata into `state.json`**
- [ ] **Step 4: Rebuild an existing `run_id` directory before each run**

- [ ] **Step 5: Run focused tests**

Run: `pytest tests/test_pipeline_demo.py -q`
Expected: PASS

### Task 3: Refresh docs and verify the full suite

**Files:**
- Modify: `E:/xjcode/Test_AI_Agent/README.md`

- [ ] **Step 1: Document subprocess stage execution and rerun behavior**
- [ ] **Step 2: Run full verification**

Run: `pytest -q`
Expected: PASS
