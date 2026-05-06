from __future__ import annotations

from .base_agent import BaseAgent


class TestcaseAgent(BaseAgent):
    agent_name = "testcase_agent"
    stage_name = "testcase_design"

    def run(
        self,
        requirement_model: dict[str, object],
        acceptance_criteria: dict[str, object],
    ) -> dict[str, object]:
        requirement_id = str(requirement_model["requirement_id"])
        title = str(requirement_model.get("title", ""))
        if requirement_id == "REQ-SAAS-LIVECODE-ONLINE-OFFLINE-001" or ("活码" in title and "上下线" in title):
            return self._run_livecode_testcase_design(requirement_id, acceptance_criteria)
        if "购物车" in title:
            return self._run_cart_testcase_design(requirement_id, acceptance_criteria)
        return self._run_default_testcase_design(requirement_id, acceptance_criteria)

    def _run_default_testcase_design(
        self,
        requirement_id: str,
        acceptance_criteria: dict[str, object],
    ) -> dict[str, object]:
        cases = [
            {
                "test_case_id": "TC-001",
                "title": "用户使用合法数据注册成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "payload": {"username": "demo_user", "email": "demo@example.com", "password": "StrongPass123"},
                "expected_status_codes": [201],
            },
            {
                "test_case_id": "TC-002",
                "title": "用户使用重复邮箱注册失败",
                "type": "negative",
                "requirement_id": requirement_id,
                "priority": "P1",
                "payload": {"username": "repeat_user", "email": "demo@example.com", "password": "StrongPass123"},
                "expected_status_codes": [409],
            },
            {
                "test_case_id": "TC-003",
                "title": "用户缺少必填字段时注册失败",
                "type": "validation",
                "requirement_id": requirement_id,
                "priority": "P1",
                "payload": {"username": "", "email": "", "password": "StrongPass123"},
                "expected_status_codes": [400],
            },
        ]
        matrix_rows = [
            "test_case_id,title,type,priority,expected_status_codes",
            "TC-001,用户使用合法数据注册成功,positive,P0,201",
            "TC-002,用户使用重复邮箱注册失败,negative,P1,409",
            "TC-003,用户缺少必填字段时注册失败,validation,P1,400",
        ]
        return {
            "test_cases": {"requirement_id": requirement_id, "cases": cases},
            "test_points": self._build_test_points(requirement_id, cases, acceptance_criteria),
            "test_case_matrix": "\n".join(matrix_rows),
            "coverage_report": "\n".join(
                [
                    "# Coverage Report",
                    "",
                    "- Covered positive registration flow.",
                    "- Covered duplicate email rejection.",
                    "- Covered required field validation.",
                    f"- Acceptance criteria count: {len(acceptance_criteria['criteria'])}",
                ]
            ),
        }

    def _run_livecode_testcase_design(
        self,
        requirement_id: str,
        acceptance_criteria: dict[str, object],
    ) -> dict[str, object]:
        cases = [
            {
                "test_case_id": "TC-LIVECODE-001",
                "title": "新增活码并配置次日自动上线时间",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "save_contact_way",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-002",
                "title": "编辑活码时同一时分秒且旧值未过期时保持原时间",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "save_contact_way",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-003",
                "title": "保存获客链接并检查是否支持 nextAutoEnableTime",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "save_acquisition_link",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-004",
                "title": "查询员工当前上下线状态列表",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "list_online_status",
                "payload": {},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-005",
                "title": "手动下线员工成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "change_online_status",
                "payload": {"status": 0},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-006",
                "title": "手动上线员工成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "change_online_status",
                "payload": {"status": 1},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-007",
                "title": "旧 MQ 消息因 next_auto_enable_time 不一致被丢弃",
                "type": "negative",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "save_contact_way",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-008",
                "title": "自动上线成功后顺延 next_auto_enable_time 到下一天同一时刻",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "sync_org",
                "payload": {},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-009",
                "title": "仅 source=2 自建渠道受手动上下线影响",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "change_online_status",
                "payload": {"status": 0, "source": 2},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-010",
                "title": "无权限账号不能操作非本人企微员工",
                "type": "negative",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "change_online_status",
                "payload": {"status": 0},
                "expected_status_codes": [401, 403],
            },
        ]
        matrix_rows = ["test_case_id,title,type,priority,automation_candidate,related_api_intent"]
        matrix_rows.extend(
            [
                ",".join(
                    [
                        case["test_case_id"],
                        case["title"],
                        case["type"],
                        case["priority"],
                        str(case["automation_candidate"]),
                        case["related_api_intent"],
                    ]
                )
                for case in cases
            ]
        )
        return {
            "test_cases": {"requirement_id": requirement_id, "cases": cases},
            "test_points": self._build_test_points(requirement_id, cases, acceptance_criteria),
            "test_case_matrix": "\n".join(matrix_rows),
            "coverage_report": "\n".join(
                [
                    "# Coverage Report",
                    "",
                    "- Covered time configuration, manual online/offline, status query, and MQ-related behavior.",
                    "- Covered source=2 scope restriction and permission boundary scenarios.",
                    f"- Acceptance criteria count: {len(acceptance_criteria['criteria'])}",
                ]
            ),
        }

    def _run_cart_testcase_design(
        self,
        requirement_id: str,
        acceptance_criteria: dict[str, object],
    ) -> dict[str, object]:
        cases = [
            {
                "test_case_id": "TC-CART-ADD-001",
                "title": "有效上架宠物加入购物车成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "add_cart_item",
                "payload": {"petId": "${valid_pet_id}", "quantity": 1},
                "expected_status_codes": [200, 201],
            },
            {
                "test_case_id": "TC-CART-LIST-001",
                "title": "购物车列表展示商品状态和汇总信息",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "list_cart_items",
                "payload": {},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-CART-QTY-001",
                "title": "修改有效购物车商品数量成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "update_cart_quantity",
                "payload": {"quantity": 2},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-CART-SELECT-001",
                "title": "勾选和取消勾选有效商品成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "select_cart_item",
                "payload": {"selected": True},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-CART-SELECT-ALL-001",
                "title": "全选仅作用于有效商品",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "select_all_cart_items",
                "payload": {"selected": True},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-CART-DELETE-001",
                "title": "删除单个购物车商品成功且不影响库存",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "delete_cart_item",
                "payload": {},
                "expected_status_codes": [200, 204],
            },
            {
                "test_case_id": "TC-CART-BATCH-DELETE-001",
                "title": "批量删除购物车商品成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "batch_delete_cart_items",
                "payload": {"cartItemIds": ["${cart_item_id_1}", "${cart_item_id_2}"]},
                "expected_status_codes": [200, 204],
            },
            {
                "test_case_id": "TC-CART-CLEAR-INVALID-001",
                "title": "一键清空失效商品且保留有效商品",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "clear_invalid_cart_items",
                "payload": {},
                "expected_status_codes": [200, 204],
            },
            {
                "test_case_id": "TC-CART-CHECKOUT-001",
                "title": "购物车结算成功生成订单并移除已结算商品",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "checkout_cart",
                "payload": {},
                "expected_status_codes": [200, 201],
            },
            {
                "test_case_id": "TC-CART-CHECKOUT-002",
                "title": "购物车结算遇到失效商品时失败且不生成订单",
                "type": "negative",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "checkout_cart",
                "payload": {},
                "expected_status_codes": [400, 409],
            },
            {
                "test_case_id": "TC-CART-AUTH-001",
                "title": "未登录用户不可操作购物车",
                "type": "negative",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "add_cart_item",
                "payload": {"petId": "${valid_pet_id}", "quantity": 1},
                "expected_status_codes": [401],
            },
        ]
        matrix_rows = ["test_case_id,title,type,priority,automation_candidate,related_api_intent"]
        matrix_rows.extend(
            [
                ",".join(
                    [
                        case["test_case_id"],
                        case["title"],
                        case["type"],
                        case["priority"],
                        str(case["automation_candidate"]),
                        case["related_api_intent"],
                    ]
                )
                for case in cases
            ]
        )
        return {
            "test_cases": {"requirement_id": requirement_id, "cases": cases},
            "test_points": self._build_test_points(requirement_id, cases, acceptance_criteria),
            "test_case_matrix": "\n".join(matrix_rows),
            "coverage_report": "\n".join(
                [
                    "# Coverage Report",
                    "",
                    "- Covered add/list/update/select/delete/checkout cart behaviors.",
                    "- Covered invalid item cleanup and unauthenticated access.",
                    f"- Acceptance criteria count: {len(acceptance_criteria['criteria'])}",
                ]
            ),
        }

    def _build_test_points(
        self,
        requirement_id: str,
        cases: list[dict[str, object]],
        acceptance_criteria: dict[str, object],
    ) -> dict[str, object]:
        criteria_items = acceptance_criteria.get("criteria", [])
        test_points = []
        for index, case in enumerate(cases, start=1):
            criteria = criteria_items[index - 1] if index - 1 < len(criteria_items) else None
            linked_requirement_ids = [requirement_id]
            linked_criteria_ids = [str(criteria.get("criteria_id"))] if isinstance(criteria, dict) and criteria.get("criteria_id") else []
            test_points.append(
                {
                    "test_point_id": f"TP-{index:03d}",
                    "title": str(case.get("title", case.get("test_case_id", ""))),
                    "requirement_id": requirement_id,
                    "linked_requirement_ids": linked_requirement_ids,
                    "linked_criteria_ids": linked_criteria_ids,
                    "linked_case_ids": [str(case.get("test_case_id", ""))],
                    "priority": str(case.get("priority", "")),
                    "automation_candidate": bool(case.get("automation_candidate", False)),
                    "coverage_type": str(case.get("type", "")),
                    "notes": str(criteria.get("description", "")) if isinstance(criteria, dict) else "",
                }
            )

        uncovered_criteria = []
        covered_criteria_ids = {
            criterion_id
            for point in test_points
            for criterion_id in point["linked_criteria_ids"]
            if criterion_id
        }
        for item in criteria_items:
            if not isinstance(item, dict):
                continue
            criterion_id = str(item.get("criteria_id", ""))
            if criterion_id and criterion_id not in covered_criteria_ids:
                uncovered_criteria.append(criterion_id)

        return {
            "requirement_id": requirement_id,
            "test_points": test_points,
            "trace_summary": {
                "criteria_total": len(criteria_items),
                "points_total": len(test_points),
                "cases_total": len(cases),
                "uncovered_criteria_ids": uncovered_criteria,
            },
        }
