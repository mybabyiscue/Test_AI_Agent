from __future__ import annotations

from pathlib import Path
import re

from .role_profiles import get_role_profile


class RequirementAgent:
    agent_name = "requirement_agent"
    stage_name = "requirement_analysis"

    def role_profile(self) -> dict[str, object]:
        return get_role_profile(self.agent_name)

    def run(self, requirement_path: Path) -> dict[str, object]:
        text = requirement_path.read_text(encoding="utf-8-sig")
        if "购物车" in text:
            return self._run_cart_requirement_analysis(requirement_path, text)

        lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip().startswith("-")]

        scenarios = [
            {
                "scenario_id": "REQ-001-SC-01",
                "name": "用户使用合法资料发起注册",
                "expected_outcome": "系统创建账号成功",
            },
            {
                "scenario_id": "REQ-001-SC-02",
                "name": "用户使用重复邮箱发起注册",
                "expected_outcome": "系统拒绝注册并返回重复提示",
            },
        ]

        acceptance_items = [
            {"criteria_id": f"AC-00{index}", "description": line}
            for index, line in enumerate(lines, start=1)
        ]

        return {
            "requirement_model": {
                "requirement_id": "REQ-001",
                "title": "用户注册",
                "source_path": str(requirement_path),
                "scenarios": scenarios,
            },
            "acceptance_criteria": {
                "requirement_id": "REQ-001",
                "criteria": acceptance_items,
            },
            "business_flow": "\n".join(
                [
                    "# 用户注册业务流",
                    "",
                    "1. 用户填写用户名、邮箱、密码。",
                    "2. 系统校验字段完整性与邮箱唯一性。",
                    "3. 校验通过则创建账号，失败则返回错误。",
                ]
            ),
            "risk_points": {
                "requirement_id": "REQ-001",
                "risks": [
                    "接口文档未明确重复邮箱的响应体结构。",
                    "缺少鉴权与频控描述时，生成脚本需要保守处理。",
                ],
            },
        }

    def _run_cart_requirement_analysis(self, requirement_path: Path, text: str) -> dict[str, object]:
        title = self._extract_title(text, fallback="宠物商店系统购物车功能")
        goals = self._extract_section_items(text, ["需求目标"])
        core_flows = self._extract_section_items(text, ["主流程", "业务流程"])
        business_rules = self._extract_keyword_lines(
            text,
            ["库存", "失效", "勾选", "全选", "删除", "结算", "下单", "订单", "WMS", "数量", "登录"],
        )
        exception_scenarios = self._extract_keyword_lines(
            text,
            ["未登录", "不存在", "已删除", "下架", "库存不足", "失效", "数量不能", "失败"],
        )
        in_scope = self._extract_section_items(text, ["本期范围", "In Scope"])
        out_scope = self._extract_section_items(text, ["本期不做", "Out of Scope"])

        scenarios = [
            {
                "scenario_id": "REQ-CART-001-SC-01",
                "name": "加入购物车",
                "expected_outcome": "用户可将有效且有库存的宠物加入购物车，重复加入时累加数量且不超过库存。",
            },
            {
                "scenario_id": "REQ-CART-001-SC-02",
                "name": "购物车列表查询",
                "expected_outcome": "用户可查看购物车商品、勾选状态、失效状态、当前库存与汇总金额。",
            },
            {
                "scenario_id": "REQ-CART-001-SC-03",
                "name": "修改购物车商品数量",
                "expected_outcome": "用户可修改有效商品数量，数量必须在 1 到当前库存之间。",
            },
            {
                "scenario_id": "REQ-CART-001-SC-04",
                "name": "勾选、取消勾选与全选",
                "expected_outcome": "用户只能勾选有效商品，全选仅作用于有效商品，勾选状态需持久化。",
            },
            {
                "scenario_id": "REQ-CART-001-SC-05",
                "name": "删除和清空失效商品",
                "expected_outcome": "用户可删除单个、批量删除购物车商品，也可一键清空失效商品。",
            },
            {
                "scenario_id": "REQ-CART-001-SC-06",
                "name": "购物车结算",
                "expected_outcome": "系统只基于已勾选有效商品生成订单，成功后移除已结算购物车商品。",
            },
        ]
        acceptance_items = [
            {"criteria_id": f"AC-CART-{index:03d}", "description": item}
            for index, item in enumerate(self._dedupe(goals + business_rules + exception_scenarios), start=1)
        ]

        return {
            "requirement_model": {
                "requirement_id": "REQ-CART-001",
                "title": title,
                "source_path": str(requirement_path),
                "goals": goals,
                "core_flows": core_flows,
                "business_rules": business_rules,
                "exception_scenarios": exception_scenarios,
                "impact_scope": {
                    "systems": ["pet-store-web", "pet-store-server", "pet-store-wms"],
                    "in_scope": in_scope,
                    "out_of_scope": out_scope,
                    "wms_boundary": "WMS 平台仅感知购物车结算后的订单，不直接维护购物车。",
                },
                "scenarios": scenarios,
            },
            "acceptance_criteria": {
                "requirement_id": "REQ-CART-001",
                "criteria": acceptance_items,
            },
            "business_flow": "\n".join(
                ["# 购物车业务主流程", ""]
                + [f"{index}. {item}" for index, item in enumerate(core_flows, start=1)]
            ),
            "risk_points": {
                "requirement_id": "REQ-CART-001",
                "risks": [
                    "结算前必须实时校验商品存在、上下架、库存和数量合法性，否则会出现订单与购物车状态不一致。",
                    "购物车不锁库存，自动化测试必须准备库存充足、库存不足、下架、失效等稳定数据。",
                    "WMS 不直接处理购物车，接口自动化不能把购物车操作误映射到 WMS 接口。",
                ],
            },
        }

    def _extract_title(self, text: str, fallback: str) -> str:
        for line in text.splitlines():
            match = re.match(r"^\s*\.?\s*#\s+(.+?)\s*$", line)
            if match:
                return match.group(1).replace(" PRD", "").strip()
        return fallback

    def _extract_section_items(self, text: str, heading_keywords: list[str]) -> list[str]:
        lines = text.splitlines()
        items: list[str] = []
        in_section = False
        heading_level = 0
        for line in lines:
            stripped = line.strip()
            heading = re.match(r"^(#{2,4})\s+(.+)$", stripped)
            if heading:
                current_level = len(heading.group(1))
                heading_text = heading.group(2)
                if any(keyword in heading_text for keyword in heading_keywords):
                    in_section = True
                    heading_level = current_level
                    continue
                if in_section and current_level <= heading_level:
                    break
            if not in_section:
                continue

            cleaned = self._clean_list_item(stripped)
            if cleaned:
                items.append(cleaned)
        return self._dedupe(items)

    def _extract_keyword_lines(self, text: str, keywords: list[str]) -> list[str]:
        items = []
        for raw_line in text.splitlines():
            cleaned = self._clean_list_item(raw_line.strip())
            if cleaned and any(keyword in cleaned for keyword in keywords):
                items.append(cleaned)
        return self._dedupe(items)

    def _clean_list_item(self, line: str) -> str | None:
        if not line:
            return None
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.、])\s*", "", line).strip()
        cleaned = cleaned.strip("` ")
        if not cleaned or cleaned.startswith("#") or cleaned == "---":
            return None
        return cleaned

    def _dedupe(self, items: list[str]) -> list[str]:
        seen = set()
        result = []
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            result.append(item)
        return result
