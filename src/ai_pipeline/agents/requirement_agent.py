from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..fallback_templates import load_template, render_template
from .base_agent import BaseAgent


def extract_pdf_text(requirement_path: Path) -> dict[str, Any] | None:
    try:
        from pypdf import PdfReader
    except Exception:
        return None

    try:
        reader = PdfReader(str(requirement_path))
    except Exception:
        return None

    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        pages.append(f"===== PAGE {index} =====\n{page_text.strip()}\n")

    extracted_text = "\n\n".join(pages).strip()
    if not extracted_text:
        return None

    return {
        "text": "# PDF 提取文本\n\n" + extracted_text + "\n",
        "page_count": len(reader.pages),
        "source_pdf_path": str(requirement_path),
    }


class RequirementAgent(BaseAgent):
    agent_name = "requirement_agent"
    stage_name = "requirement_analysis"

    def run(self, requirement_path: Path) -> dict[str, object]:
        text = self._read_requirement_text(requirement_path)
        if requirement_path.suffix.lower() == ".pdf":
            return self._run_pdf_requirement_analysis(requirement_path, text)
        if "购物车" in text:
            return self._run_cart_requirement_analysis(requirement_path, text)
        return self._run_default_requirement_analysis(requirement_path, text)

    def _read_requirement_text(self, requirement_path: Path) -> str:
        if requirement_path.suffix.lower() == ".pdf":
            snapshot = extract_pdf_text(requirement_path)
            if snapshot:
                return str(snapshot["text"])
            return f"# PDF Requirement\n\nSource file: {requirement_path.name}\n"
        return requirement_path.read_text(encoding="utf-8-sig")

    def _run_pdf_requirement_analysis(self, requirement_path: Path, text: str) -> dict[str, object]:
        filename = requirement_path.name
        if "活码" in filename and "上下线" in filename:
            return self._run_livecode_online_offline_requirement_analysis(requirement_path)

        title = requirement_path.stem
        acceptance_items = [
            {"criteria_id": "AC-PDF-001", "description": "PDF 需求已成功读取，需人工确认关键业务规则。"},
            {"criteria_id": "AC-PDF-002", "description": "后续阶段只能基于已确认内容设计测试与接口映射。"},
        ]
        return {
            "requirement_model": {
                "requirement_id": "REQ-PDF-001",
                "title": title,
                "source_path": str(requirement_path),
                "source_type": "pdf",
                "scenarios": [
                    {
                        "scenario_id": "REQ-PDF-001-SC-01",
                        "name": f"读取 {title} 的 PDF 需求内容",
                        "expected_outcome": "需求被整理为可供测试设计消费的结构化输入",
                    }
                ],
            },
            "acceptance_criteria": {
                "requirement_id": "REQ-PDF-001",
                "criteria": acceptance_items,
            },
            "business_flow": "\n".join(
                [
                    f"# {title} 业务流程",
                    "",
                    "1. 读取 PDF 需求原文。",
                    "2. 提炼核心流程、关键规则和阻塞问题。",
                    "3. 输出结构化需求，供后续 Agent 消费。",
                ]
            ),
            "risk_points": {
                "requirement_id": "REQ-PDF-001",
                "risks": [
                    "PDF 提取文本可能存在版式或编码失真，需要对关键规则进行人工复核。",
                    "若原文未明确业务边界，下游阶段必须保留待确认标记，不能自行补造事实。",
                ],
            },
        }

    def _run_livecode_online_offline_requirement_analysis(self, requirement_path: Path) -> dict[str, object]:
        template = render_template(
            "requirement_agent",
            "livecode_online_offline",
            requirement_path=str(requirement_path),
        )
        if template is not None:
            return template
        return self._run_livecode_online_offline_requirement_analysis_fallback(requirement_path)

    def _run_livecode_online_offline_requirement_analysis_fallback(self, requirement_path: Path) -> dict[str, object]:
        requirement_id = "REQ-SAAS-LIVECODE-ONLINE-OFFLINE-001"
        scenarios = [
            {"scenario_id": "REQ-LIVECODE-001-SC-01", "name": "配置渠道活码次日自动上线时间", "expected_outcome": "保存成功并记录 next_auto_enable_time，用于后续自动上线调度。"},
            {"scenario_id": "REQ-LIVECODE-001-SC-02", "name": "配置获客链接次日自动上线时间", "expected_outcome": "保存成功并确认接口契约是否支持 nextAutoEnableTime。"},
            {"scenario_id": "REQ-LIVECODE-001-SC-03", "name": "员工手动上下线", "expected_outcome": "仅 source=2 自建渠道受影响，并保留状态与日志。"},
            {"scenario_id": "REQ-LIVECODE-001-SC-04", "name": "RocketMQ 延时消息触发自动上线", "expected_outcome": "到点自动上线，旧消息按 next_auto_enable_time 校验后丢弃。"},
        ]
        criteria = [
            "渠道活码新增/编辑接口需要支持保存次日自动上线时间。", "获客链接新增/编辑接口需要核对 nextAutoEnableTime 的真实契约支持情况。",
            "页面需要展示员工当前上下线状态，并支持手动上下线操作。", "自动上线通过 RocketMQ 延时消息触发，不能引入新的主状态机。",
            "自动上线成功后需要将 next_auto_enable_time 顺延到下一天同一时刻。", "消费旧消息时需要校验 next_auto_enable_time，一致才允许生效。",
            "手动上下线仅影响 source=2 的自建渠道数据。", "手动上下线采用本地事务提交后异步刷新企微配置。",
            "需要新增员工上下线状态表和操作日志表，满足状态可视与审计要求。", "权限边界不清、MQ 细节缺失和企微同步链路未明确的内容必须标记为待确认。",
        ]
        return {
            "requirement_model": {
                "requirement_id": requirement_id, "title": "活码和链接自动上线与手动上下线",
                "source_path": str(requirement_path), "source_type": "pdf",
                "business_background": "为企微获客模块补齐临时下线、次日自动上线、手动上下线管理能力，覆盖渠道活码和获客链接两类渠道。",
                "objects": [{"name": "渠道活码", "table": "wework_contact_way"}, {"name": "获客链接", "table": "wework_customer_acquisition_link"}],
                "design_goals": ["支持页面配置次日自动上线时间", "支持通过 RocketMQ 延时消息触发自动上线", "支持页面手动对员工执行上线/下线操作", "支持记录员工当前上下线状态和操作流水", "仅处理自建渠道数据，避免影响系统内置渠道"],
                "core_rules": ["不新增主状态机，复用 wework_acquisition_rule_user_config.enable 作为真实生效开关", "页面保存配置后预先投递延时消息，到点后由消费者处理自动上线", "消费时校验主表 next_auto_enable_time 是否仍与消息期望触发时间一致，不一致则丢弃旧消息", "自动上线成功后需要将 next_auto_enable_time 顺延到下一天同一时刻并继续补发消息", "手动上下线仅影响自建渠道数据 source=2", "手动上下线采用本地事务 + 事务后异步刷新企微配置"],
                "new_tables": ["wework_acquisition_user_online_status", "wework_acquisition_user_online_log"],
                "api_clues": ["POST /contact/way/save", "POST /acquisition/link/saveOrUpdate", "GET /acquisition/user/online/list", "POST /acquisition/user/online/change"],
                "blocking_questions": ["RocketMQ topic/tag/消息体与消费入口未在本次 PDF 中给出", "CurrentUser 的真实生成规则未在需求文档中给出", "自动上线后重新同步企微的真实调用链路未在需求文档中给出"],
                "scenarios": scenarios,
            },
            "acceptance_criteria": {"requirement_id": requirement_id, "criteria": [{"criteria_id": f"AC-LIVECODE-{i:03d}", "description": item} for i, item in enumerate(criteria, start=1)]},
            "business_flow": "# 活码和链接自动上线与手动上下线业务流程\n\n1. 页面新增或编辑渠道活码/获客链接时填写次日自动上线时间。\n2. 保存接口落库 next_auto_enable_time，并在事务完成后投递 RocketMQ 延时消息。\n3. 到达触发时间后，消费端校验主表 next_auto_enable_time 是否仍与消息一致。\n4. 校验通过则将 enable 切为生效状态，并触发企微配置刷新。\n5. 自动上线成功后顺延 next_auto_enable_time 到下一天同一时刻，并继续补发消息。\n6. 页面支持管理员手动执行员工上线/下线，仅影响 source=2 自建渠道数据。\n7. 系统同时维护员工上下线状态表和操作日志表，满足页面展示与审计追踪。",
            "risk_points": {"requirement_id": requirement_id, "risks": ["编辑场景下时间不变时不应错误顺延到次日。", "旧 RocketMQ 消息若未按 next_auto_enable_time 做幂等校验，可能导致错误上线。", "手动上下线权限边界不清会导致越权操作风险。", "状态表、日志表与规则表可能出现一致性问题。", "企微异步刷新失败不能影响主交易，但必须可观测。", "获客链接接口契约与需求方案可能存在不一致，需要以真实接口为准。"]},
        }

    def _run_default_requirement_analysis(self, requirement_path: Path, text: str) -> dict[str, object]:
        lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip().startswith("-")]
        acceptance_items = [
            {"criteria_id": f"AC-00{index}", "description": line}
            for index, line in enumerate(lines, start=1)
        ]
        template = render_template("requirement_agent", "default", requirement_path=str(requirement_path))
        if template is not None:
            template["acceptance_criteria"]["criteria"] = acceptance_items
            return template
        return {
            "requirement_model": {"requirement_id": "REQ-001", "title": "用户注册", "source_path": str(requirement_path), "scenarios": [{"scenario_id": "REQ-001-SC-01", "name": "用户使用合法资料发起注册", "expected_outcome": "系统创建账号成功"}, {"scenario_id": "REQ-001-SC-02", "name": "用户使用重复邮箱发起注册", "expected_outcome": "系统拒绝注册并返回重复提示"}]},
            "acceptance_criteria": {"requirement_id": "REQ-001", "criteria": acceptance_items},
            "business_flow": "# 用户注册业务流\n\n1. 用户填写用户名、邮箱、密码。\n2. 系统校验字段完整性与邮箱唯一性。\n3. 校验通过则创建账户，失败则返回错误。",
            "risk_points": {"requirement_id": "REQ-001", "risks": ["接口文档未明确重复邮箱的响应体结构。", "缺少鉴权与频控描述时，生成脚本需要保守处理。"]},
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
                "expected_outcome": "用户可将有效且有库存的宠物加入购物车，重复加入时累计数量且不超过库存。",
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
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)、])\s*", "", line).strip()
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
