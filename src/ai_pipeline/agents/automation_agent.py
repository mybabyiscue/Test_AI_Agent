from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from ..artifact_store import StageWorkspace
from ..test_environment import load_test_environment
from .role_profiles import get_role_profile


class AutomationAgent:
    agent_name = "automation_agent"
    stage_name = "automation_execution"

    def __init__(self, test_environment_config_path: Path | None = None) -> None:
        self.test_environment_config_path = test_environment_config_path

    def role_profile(self) -> dict[str, object]:
        return get_role_profile(self.agent_name)

    def run(
        self,
        run_id: str,
        run_dir: Path,
        endpoint_mapping: dict[str, Any],
        stage_workspace: StageWorkspace,
    ) -> dict[str, object]:
        generated_tests = endpoint_mapping["mappings"]
        test_file = stage_workspace.write_output_text(
            "generated_tests/test_generated_api_cases.py",
            self._build_generated_test_file(generated_tests),
        )

        automation_plan = {
            "run_id": run_id,
            "mode": "execute_with_skip_when_api_base_url_missing",
            "generated_tests": generated_tests,
        }
        stage_workspace.write_output_json("automation_plan.json", automation_plan)

        allure_results_dir = stage_workspace.output_dir / "allure-results"
        pytest_command = [sys.executable, "-m", "pytest", str(test_file.resolve()), "-q"]
        if find_spec("allure_pytest") is not None:
            pytest_command.append(f"--alluredir={allure_results_dir}")

        completed = subprocess.run(
            pytest_command,
            cwd=run_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            env=self._build_pytest_env(),
        )
        summary = self._parse_pytest_summary(completed.stdout + completed.stderr)
        html_report = self._generate_allure_html_report(allure_results_dir, stage_workspace.output_dir / "allure-report")
        viewing_guide_path = None
        if html_report.get("index_path"):
            viewing_guide = self._build_allure_viewing_guide(
                report_dir=Path(str(html_report["report_dir"])),
                results_dir=allure_results_dir,
            )
            viewing_guide_path = stage_workspace.write_output_text(
                "allure_report_viewing_guide.md",
                viewing_guide,
            )

        execution_report = {
            "run_id": run_id,
            "pytest_exit_code": completed.returncode,
            "generated_test_count": len(generated_tests),
            "summary": summary,
            "allure_results_dir": str(allure_results_dir),
            "allure_html_report": html_report,
            "allure_viewing_guide": str(viewing_guide_path) if viewing_guide_path else None,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        stage_workspace.write_output_json("execution_report.json", execution_report)

        failure_summary = "\n".join(
            [
                "# Failure Summary",
                "",
                f"- pytest exit code: {completed.returncode}",
                f"- passed: {summary['passed']}",
                f"- failed: {summary['failed']}",
                f"- skipped: {summary['skipped']}",
            ]
        )
        stage_workspace.write_output_text("failure_summary.md", failure_summary)
        stage_workspace.write_log(
            "execution.log",
            "\n".join(
                [
                    f"run_id={run_id}",
                    f"pytest_exit_code={completed.returncode}",
                    "--- stdout ---",
                    completed.stdout,
                    "--- stderr ---",
                    completed.stderr,
                ]
            ),
        )
        return {
            "automation_plan": automation_plan,
            "execution_report": execution_report,
            "generated_test_file": str(test_file),
        }

    def _build_generated_test_file(self, generated_tests: list[dict[str, Any]]) -> str:
        cases_json = json.dumps(generated_tests, ensure_ascii=False, indent=2)
        return "\n".join(
            [
                "from __future__ import annotations",
                "",
                "import json",
                "import os",
                "import urllib.error",
                "import urllib.request",
                "",
                "import pytest",
                "",
                "try:",
                "    import allure",
                "except ImportError:  # pragma: no cover - generated tests still need to be importable without Allure.",
                "    class _NoopAttachmentType:",
                "        JSON = 'application/json'",
                "        TEXT = 'text/plain'",
                "",
                "    class _NoopDynamic:",
                "        def epic(self, *_args, **_kwargs) -> None:",
                "            return None",
                "",
                "        def feature(self, *_args, **_kwargs) -> None:",
                "            return None",
                "",
                "        def story(self, *_args, **_kwargs) -> None:",
                "            return None",
                "",
                "        def title(self, *_args, **_kwargs) -> None:",
                "            return None",
                "",
                "    class _NoopStep:",
                "        def __enter__(self):",
                "            return self",
                "",
                "        def __exit__(self, *_args):",
                "            return False",
                "",
                "    class _NoopAllure:",
                "        attachment_type = _NoopAttachmentType()",
                "        dynamic = _NoopDynamic()",
                "",
                "        def step(self, *_args, **_kwargs):",
                "            return _NoopStep()",
                "",
                "        def attach(self, *_args, **_kwargs) -> None:",
                "            return None",
                "",
                "    allure = _NoopAllure()",
                "",
                "BASE_URL = os.getenv('API_BASE_URL')",
                "FRONT_USERNAME = os.getenv('FRONT_USERNAME')",
                "FRONT_PASSWORD = os.getenv('FRONT_PASSWORD')",
                "FRONT_LOGIN_PATH = os.getenv('FRONT_LOGIN_PATH', '/api/front/auth/login')",
                "FRONT_TOKEN_JSON_PATH = os.getenv('FRONT_TOKEN_JSON_PATH', 'data.token')",
                "AUTH_HEADER_NAME = os.getenv('AUTH_HEADER_NAME', 'Authorization')",
                "AUTH_SCHEME = os.getenv('AUTH_SCHEME', 'Bearer')",
                "CONTEXT: dict[str, object] = {}",
                "pytestmark = pytest.mark.skipif(",
                "    not BASE_URL,",
                "    reason='Set API_BASE_URL to execute generated API tests.',",
                ")",
                "",
                f"CASES = json.loads({cases_json!r})",
                "",
                "def _json_attachment(name: str, value: object) -> None:",
                "    allure.attach(",
                "        json.dumps(value, ensure_ascii=False, indent=2),",
                "        name=name,",
                "        attachment_type=allure.attachment_type.JSON,",
                "    )",
                "",
                "def _extract_json_path(payload: dict[str, object], path: str) -> object:",
                "    current: object = payload",
                "    for part in path.split('.'):",
                "        if not isinstance(current, dict) or part not in current:",
                "            raise AssertionError(f'Missing token field: {path}')",
                "        current = current[part]",
                "    return current",
                "",
                "def _send_json(",
                "    method: str,",
                "    path: str,",
                "    payload_obj: object | None = None,",
                "    headers: dict[str, str] | None = None,",
                ") -> tuple[int, str]:",
                "    body = None if method == 'GET' else json.dumps(payload_obj or {}).encode('utf-8')",
                "    request = urllib.request.Request(",
                "        url=f'{BASE_URL}{path}',",
                "        data=body,",
                "        headers={'Content-Type': 'application/json', **(headers or {})},",
                "        method=method,",
                "    )",
                "    try:",
                "        with urllib.request.urlopen(request, timeout=10) as response:",
                "            return response.getcode(), response.read().decode('utf-8')",
                "    except urllib.error.HTTPError as exc:",
                "        return exc.code, exc.read().decode('utf-8')",
                "",
                "def _login_front_user() -> dict[str, str]:",
                "    if 'front_auth_headers' in CONTEXT:",
                "        return CONTEXT['front_auth_headers']  # type: ignore[return-value]",
                "    if not FRONT_USERNAME or not FRONT_PASSWORD:",
                "        pytest.skip('缺少 FRONT_USERNAME 或 FRONT_PASSWORD，无法执行需要登录态的接口用例。')",
                "    status_code, response_text = _send_json(",
                "        'POST',",
                "        FRONT_LOGIN_PATH,",
                "        {'username': FRONT_USERNAME, 'password': FRONT_PASSWORD},",
                "    )",
                "    allure.attach(",
                "        response_text,",
                "        name='前台登录响应',",
                "        attachment_type=allure.attachment_type.JSON,",
                "    )",
                "    assert status_code == 200",
                "    token = str(_extract_json_path(json.loads(response_text), FRONT_TOKEN_JSON_PATH))",
                "    CONTEXT['front_auth_headers'] = {AUTH_HEADER_NAME: f'{AUTH_SCHEME} {token}'}",
                "    _reset_cart_once(CONTEXT['front_auth_headers'])  # type: ignore[arg-type]",
                "    return CONTEXT['front_auth_headers']  # type: ignore[return-value]",
                "",
                "def _reset_cart_once(headers: dict[str, str]) -> None:",
                "    if CONTEXT.get('cart_reset_done'):",
                "        return",
                "    CONTEXT['cart_reset_done'] = True",
                "    status_code, response_text = _send_json('GET', '/api/front/cart/items', headers=headers)",
                "    if status_code != 200:",
                "        return",
                "    body = _json_body(response_text)",
                "    data = body.get('data', {})",
                "    items = data.get('items', []) if isinstance(data, dict) else []",
                "    ids = [int(item['id']) for item in items if isinstance(item, dict) and item.get('id') is not None]",
                "    if ids:",
                "        _send_json('DELETE', '/api/front/cart/items', {'ids': ids}, headers=headers)",
                "",
                "def _auth_headers(case: dict[str, object]) -> dict[str, str]:",
                "    if 401 in case.get('expected_status_codes', []):",
                "        return {}",
                "    return _login_front_user()",
                "",
                "def _json_body(response_text: str) -> dict[str, object]:",
                "    try:",
                "        body = json.loads(response_text)",
                "    except json.JSONDecodeError:",
                "        return {}",
                "    return body if isinstance(body, dict) else {}",
                "",
                "def _effective_status_code(http_status_code: int, response_text: str) -> int:",
                "    body = _json_body(response_text)",
                "    code = body.get('code')",
                "    return int(code) if isinstance(code, int) else http_status_code",
                "",
                "def _front_get(path: str) -> dict[str, object]:",
                "    status_code, response_text = _send_json('GET', path, headers=_login_front_user())",
                "    assert status_code == 200",
                "    return _json_body(response_text)",
                "",
                "def _valid_pet_ids() -> list[int]:",
                "    if 'valid_pet_ids' in CONTEXT:",
                "        return CONTEXT['valid_pet_ids']  # type: ignore[return-value]",
                "    body = _front_get('/api/front/pets')",
                "    records = body.get('data', {}).get('records', []) if isinstance(body.get('data'), dict) else []",
                "    ids = [",
                "        int(item['id'])",
                "        for item in records",
                "        if isinstance(item, dict)",
                "        and item.get('id') is not None",
                "        and item.get('pet_status') == 1",
                "        and int(item.get('stock_quantity') or 0) > 0",
                "    ]",
                "    if not ids:",
                "        pytest.skip('缺少上架且库存大于 0 的宠物测试数据。')",
                "    CONTEXT['valid_pet_ids'] = ids",
                "    return ids",
                "",
                "def _ensure_cart_items(count: int = 1) -> list[int]:",
                "    for pet_id in _valid_pet_ids()[:count]:",
                "        _send_json(",
                "            'POST',",
                "            '/api/front/cart/items',",
                "            {'pet_id': pet_id, 'quantity': 1},",
                "            headers=_login_front_user(),",
                "        )",
                "    body = _front_get('/api/front/cart/items')",
                "    data = body.get('data', {})",
                "    items = data.get('items', []) if isinstance(data, dict) else []",
                "    ids = [int(item['id']) for item in items if isinstance(item, dict) and item.get('id') is not None]",
                "    if len(ids) < count:",
                "        pytest.skip(f'购物车测试数据不足，需要 {count} 条，当前 {len(ids)} 条。')",
                "    return ids[:count]",
                "",
                "def _resolve_placeholder(value: str) -> object:",
                "    if value == '${valid_pet_id}':",
                "        return _valid_pet_ids()[0]",
                "    if value == '${cart_item_id}' or value == '${cart_item_id_1}':",
                "        return _ensure_cart_items(1)[0]",
                "    if value == '${cart_item_id_2}':",
                "        return _ensure_cart_items(2)[1]",
                "    return value",
                "",
                "def _resolve_value(value: object) -> object:",
                "    if isinstance(value, str):",
                "        return _resolve_placeholder(value)",
                "    if isinstance(value, list):",
                "        return [_resolve_value(item) for item in value]",
                "    if isinstance(value, dict):",
                "        return {key: _resolve_value(item) for key, item in value.items()}",
                "    return value",
                "",
                "def _resolve_path(path: str) -> str:",
                "    if '{id}' in path:",
                "        path = path.replace('{id}', str(_ensure_cart_items(1)[0]))",
                "    return path",
                "",
                "def _request(case: dict[str, object]) -> tuple[int, str]:",
                "    method = str(case['method']).upper()",
                "    payload_obj = _resolve_value(case.get('payload', {}))",
                "    payload = json.dumps(payload_obj).encode('utf-8')",
                "    resolved_path = _resolve_path(str(case['path']))",
                "    url = f\"{BASE_URL}{resolved_path}\"",
                "    headers = {'Content-Type': 'application/json', **_auth_headers(case)}",
                "    _json_attachment(",
                "        '请求信息',",
                "        {'method': method, 'url': url, 'headers': headers, 'body': payload_obj},",
                "    )",
                "    request = urllib.request.Request(",
                "        url=url,",
                "        data=None if method == 'GET' else payload,",
                "        headers=headers,",
                "        method=method,",
                "    )",
                "    try:",
                "        with urllib.request.urlopen(request, timeout=10) as response:",
                "            status_code = response.getcode()",
                "            response_text = response.read().decode('utf-8')",
                "    except urllib.error.HTTPError as exc:",
                "        status_code = exc.code",
                "        response_text = exc.read().decode('utf-8')",
                "    _json_attachment('响应信息', {'status_code': status_code, 'body': response_text})",
                "    return status_code, response_text",
                "",
                "@pytest.mark.parametrize(",
                "    'case',",
                "    CASES,",
                "    ids=[str(case['automation_id']) for case in CASES],",
                ")",
                "def test_generated_api_case(case: dict[str, object]) -> None:",
                "    allure.dynamic.epic(str(case.get('epic', '宠物商店系统')))",
                "    allure.dynamic.feature(str(case.get('feature', '接口自动化')))",
                "    allure.dynamic.story(str(case.get('story', case.get('test_case_id', '自动化用例'))))",
                "    allure.dynamic.title(str(case.get('title', case.get('automation_id', '接口自动化用例'))))",
                "",
                "    with allure.step('前置条件：读取环境变量与测试用例数据'):",
                "        assert BASE_URL, '缺少 API_BASE_URL，无法执行接口自动化用例'",
                "        _json_attachment('测试用例元数据', case)",
                "",
                "    with allure.step('执行步骤：发送接口请求并采集响应'):",
                "        if case.get('test_case_id') == 'TC-CART-CHECKOUT-002':",
                "            pytest.skip('该用例需要稳定失效商品 fixture，当前先保留 Allure 设计和接口映射。')",
                "        if case.get('test_case_id') == 'TC-CART-CHECKOUT-001':",
                "            _ensure_cart_items(1)",
                "        status_code, response_text = _request(case)",
                "",
                "    with allure.step('断言结果：校验响应状态码符合预期'):",
                "        expected_status_codes = case['expected_status_codes']",
                "        effective_status_code = _effective_status_code(status_code, response_text)",
                "        _json_attachment(",
                "            '断言结果',",
                "            {",
                "                'actual_http_status_code': status_code,",
                "                'actual_effective_status_code': effective_status_code,",
                "                'expected_status_codes': expected_status_codes,",
                "                'response_preview': response_text[:1000],",
                "            },",
                "        )",
                "        assert effective_status_code in expected_status_codes",
            ]
        )

    def _parse_pytest_summary(self, output: str) -> dict[str, int]:
        summary = {"passed": 0, "failed": 0, "skipped": 0}
        for key in summary:
            match = re.search(rf"(\d+) {key}", output)
            if match:
                summary[key] = int(match.group(1))
        return summary

    def _generate_allure_html_report(self, results_dir: Path, report_dir: Path) -> dict[str, object]:
        if not results_dir.exists() or not any(results_dir.iterdir()):
            return {
                "generated": False,
                "reason": "allure_results_missing",
                "results_dir": str(results_dir),
                "report_dir": str(report_dir),
                "index_path": None,
            }

        allure_command = shutil.which("allure")
        if not allure_command:
            return {
                "generated": False,
                "reason": "allure_cli_missing",
                "results_dir": str(results_dir),
                "report_dir": str(report_dir),
                "index_path": None,
            }

        completed = subprocess.run(
            [allure_command, "generate", str(results_dir), "-o", str(report_dir), "--clean"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        index_path = report_dir / "index.html"
        return {
            "generated": completed.returncode == 0 and index_path.exists(),
            "reason": None if completed.returncode == 0 and index_path.exists() else "allure_generate_failed",
            "results_dir": str(results_dir),
            "report_dir": str(report_dir),
            "index_path": str(index_path) if index_path.exists() else None,
            "command": [allure_command, "generate", str(results_dir), "-o", str(report_dir), "--clean"],
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    def _build_allure_viewing_guide(
        self,
        *,
        report_dir: Path,
        results_dir: Path,
        port: int = 18088,
    ) -> str:
        resolved_report_dir = report_dir.resolve()
        resolved_results_dir = results_dir.resolve()
        index_path = (resolved_report_dir / "index.html").resolve()
        return "\n".join(
            [
                "# Allure 报告查看方式说明",
                "",
                "## index.html 的用途",
                "`index.html` 是 Allure HTML 报告的前端入口文件，它会读取同目录下的 `widgets/`、`data/`、`history/` 等 JSON 数据来展示测试结果。",
                "",
                "## 报告文件所在目录",
                f"- 报告目录：`{resolved_report_dir}`",
                f"- 入口文件：`{index_path}`",
                f"- Allure 原始结果目录：`{resolved_results_dir}`",
                "",
                "## 查看方式 1：使用 Python 启动本地静态服务（推荐）",
                "直接用 `file://` 打开时，部分浏览器会因为本地文件安全策略导致页面一直 loading。推荐使用本地 HTTP 服务查看。",
                "",
                "```powershell",
                f"Set-Location -LiteralPath \"{resolved_report_dir}\"",
                f"python -m http.server {port} --bind 127.0.0.1",
                "```",
                "",
                "然后在浏览器访问：",
                "",
                f"`http://127.0.0.1:{port}/index.html`",
                "",
                "查看完成后，在启动服务的终端按 `Ctrl+C` 关闭。",
                "",
                "## 查看方式 2：使用 Allure CLI 直接打开原始结果",
                "如果本机已安装 Allure CLI，可以直接执行：",
                "",
                "```powershell",
                f"allure open \"{resolved_results_dir}\"",
                "```",
                "",
                "该命令会自动启动一个本地 Web 服务并打开浏览器。",
                "",
                "## 查看方式 3：直接打开 index.html（不推荐作为唯一方式）",
                "如果浏览器允许本地文件读取，可以执行：",
                "",
                "```powershell",
                f"Start-Process -FilePath \"{index_path}\"",
                "```",
                "",
                "如果页面一直停留在 loading，请改用“查看方式 1”。",
            ]
        )

    def _build_pytest_env(self) -> dict[str, str]:
        env = {"PYTHONDONTWRITEBYTECODE": "1", **os.environ}
        profile = env.get("AI_PIPELINE_TEST_ENV_PROFILE")
        if not profile:
            return env

        runtime = load_test_environment(profile, self.test_environment_config_path)
        if not runtime:
            return env

        self._set_if_present(env, "API_BASE_URL", runtime.get("api_base_url"))
        auth = runtime.get("auth", {}) if isinstance(runtime.get("auth"), dict) else {}
        front = auth.get("front_user", {}) if isinstance(auth.get("front_user"), dict) else {}
        token = auth.get("token", {}) if isinstance(auth.get("token"), dict) else {}

        self._set_if_present(env, "FRONT_USERNAME", front.get("username"))
        self._set_if_present(env, "FRONT_PASSWORD", front.get("password"))
        self._set_if_present(env, "FRONT_LOGIN_PATH", front.get("login_path"))
        self._set_if_present(env, "FRONT_TOKEN_JSON_PATH", token.get("json_path"))
        self._set_if_present(env, "AUTH_HEADER_NAME", token.get("header_name"))
        self._set_if_present(env, "AUTH_SCHEME", token.get("scheme"))
        return env

    def _set_if_present(self, env: dict[str, str], key: str, value: object) -> None:
        if value is not None and not env.get(key):
            env[key] = str(value)
