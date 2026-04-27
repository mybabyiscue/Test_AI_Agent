from __future__ import annotations

from .role_profiles import get_role_profile


class TestcaseAgent:
    agent_name = "testcase_agent"
    stage_name = "testcase_design"

    def role_profile(self) -> dict[str, object]:
        return get_role_profile(self.agent_name)

    def run(
        self,
        requirement_model: dict[str, object],
        acceptance_criteria: dict[str, object],
    ) -> dict[str, object]:
        requirement_id = str(requirement_model["requirement_id"])
        if "购物车" in str(requirement_model.get("title", "")):
            return self._run_cart_testcase_design(requirement_id, acceptance_criteria)

        cases = [
            {
                "test_case_id": "TC-001",
                "title": "用户使用合法数据注册成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "payload": {
                    "username": "demo_user",
                    "email": "demo@example.com",
                    "password": "StrongPass123"
                },
                "expected_status_codes": [201],
            },
            {
                "test_case_id": "TC-002",
                "title": "用户使用重复邮箱注册失败",
                "type": "negative",
                "requirement_id": requirement_id,
                "priority": "P1",
                "payload": {
                    "username": "repeat_user",
                    "email": "demo@example.com",
                    "password": "StrongPass123"
                },
                "expected_status_codes": [409],
            },
            {
                "test_case_id": "TC-003",
                "title": "用户缺少必填字段时注册失败",
                "type": "validation",
                "requirement_id": requirement_id,
                "priority": "P1",
                "payload": {
                    "username": "",
                    "email": "",
                    "password": "StrongPass123"
                },
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
            "test_cases": {
                "requirement_id": requirement_id,
                "cases": cases,
            },
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
                "preconditions": ["用户已登录", "宠物存在、未删除、上架且库存大于 0"],
                "steps": ["调用加入购物车接口", "查询购物车列表确认商品存在且默认勾选"],
                "payload": {"petId": "${valid_pet_id}", "quantity": 1},
                "expected_status_codes": [200, 201],
                "expected_result": "加入成功；若同一宠物已存在，则数量累加且不超过库存。",
            },
            {
                "test_case_id": "TC-CART-LIST-001",
                "title": "购物车列表展示商品状态和汇总信息",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "list_cart_items",
                "preconditions": ["用户已登录", "购物车中存在有效商品和可选失效商品"],
                "steps": ["调用购物车列表接口", "校验商品字段、失效标识、勾选数量和总金额"],
                "payload": {},
                "expected_status_codes": [200],
                "expected_result": "返回购物车商品明细、当前库存、勾选状态、失效状态和汇总信息。",
            },
            {
                "test_case_id": "TC-CART-QTY-001",
                "title": "修改有效购物车商品数量成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "update_cart_quantity",
                "preconditions": ["用户已登录", "购物车项有效", "目标数量在 1 到当前库存之间"],
                "steps": ["调用修改数量接口", "查询购物车列表确认数量、小计和总金额更新"],
                "payload": {"quantity": 2},
                "expected_status_codes": [200],
                "expected_result": "数量修改成功，库存不被扣减。",
            },
            {
                "test_case_id": "TC-CART-SELECT-001",
                "title": "勾选和取消勾选有效商品成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "select_cart_item",
                "preconditions": ["用户已登录", "购物车项有效"],
                "steps": ["调用勾选接口", "调用取消勾选接口", "查询购物车列表确认状态持久化"],
                "payload": {"selected": True},
                "expected_status_codes": [200],
                "expected_result": "有效商品勾选状态可修改并持久化。",
            },
            {
                "test_case_id": "TC-CART-SELECT-ALL-001",
                "title": "全选仅作用于有效商品",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "select_all_cart_items",
                "preconditions": ["用户已登录", "购物车同时存在有效商品和失效商品"],
                "steps": ["调用全选接口", "查询购物车列表确认有效商品被勾选、失效商品未被勾选"],
                "payload": {"selected": True},
                "expected_status_codes": [200],
                "expected_result": "全选只影响有效商品。",
            },
            {
                "test_case_id": "TC-CART-DELETE-001",
                "title": "删除单个购物车商品成功且不影响库存",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "delete_cart_item",
                "preconditions": ["用户已登录", "购物车中存在待删除商品"],
                "steps": ["调用删除单个购物车商品接口", "查询购物车列表确认商品移除"],
                "payload": {},
                "expected_status_codes": [200, 204],
                "expected_result": "商品从购物车移除，库存不变化。",
            },
            {
                "test_case_id": "TC-CART-BATCH-DELETE-001",
                "title": "批量删除购物车商品成功",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "batch_delete_cart_items",
                "preconditions": ["用户已登录", "购物车中存在多个待删除商品"],
                "steps": ["调用批量删除接口", "查询购物车列表确认目标商品移除"],
                "payload": {"cartItemIds": ["${cart_item_id_1}", "${cart_item_id_2}"]},
                "expected_status_codes": [200, 204],
                "expected_result": "目标购物车项被批量移除。",
            },
            {
                "test_case_id": "TC-CART-CLEAR-INVALID-001",
                "title": "一键清空失效商品且保留有效商品",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P1",
                "automation_candidate": True,
                "related_api_intent": "clear_invalid_cart_items",
                "preconditions": ["用户已登录", "购物车中同时存在有效商品和失效商品"],
                "steps": ["调用清空失效商品接口", "查询购物车列表确认失效商品被清理、有效商品保留"],
                "payload": {},
                "expected_status_codes": [200, 204],
                "expected_result": "仅删除失效商品。",
            },
            {
                "test_case_id": "TC-CART-CHECKOUT-001",
                "title": "购物车结算成功生成订单并移除已结算商品",
                "type": "positive",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "checkout_cart",
                "preconditions": ["用户已登录", "至少一条已勾选有效商品", "所有待结算商品实时校验通过"],
                "steps": ["调用购物车结算接口", "校验返回订单信息", "查询购物车确认已结算商品被移除"],
                "payload": {},
                "expected_status_codes": [200, 201],
                "expected_result": "生成 CREATED 状态订单，购物车中移除本次已结算商品。",
            },
            {
                "test_case_id": "TC-CART-CHECKOUT-002",
                "title": "购物车结算遇到失效商品时失败且不生成订单",
                "type": "negative",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "checkout_cart",
                "preconditions": ["用户已登录", "已勾选商品存在下架、删除或库存不足场景"],
                "steps": ["调用购物车结算接口", "校验失败原因", "确认不生成订单且购物车商品不删除"],
                "payload": {},
                "expected_status_codes": [400, 409],
                "expected_result": "结算失败，返回具体失败原因，不生成订单，不删除购物车商品。",
            },
            {
                "test_case_id": "TC-CART-AUTH-001",
                "title": "未登录用户不可操作购物车",
                "type": "negative",
                "requirement_id": requirement_id,
                "priority": "P0",
                "automation_candidate": True,
                "related_api_intent": "add_cart_item",
                "preconditions": ["未登录或登录态失效"],
                "steps": ["调用购物车接口", "校验系统返回未认证提示"],
                "payload": {"petId": "${valid_pet_id}", "quantity": 1},
                "expected_status_codes": [401],
                "expected_result": "系统拒绝请求并提示请先登录。",
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
            "test_cases": {
                "requirement_id": requirement_id,
                "cases": cases,
            },
            "test_case_matrix": "\n".join(matrix_rows),
            "coverage_report": "\n".join(
                [
                    "# 购物车测试覆盖报告",
                    "",
                    "- 覆盖加入购物车、列表、数量、勾选、全选、删除、清空失效、结算和未登录场景。",
                    "- P0 用例覆盖主链路和关键失败路径。",
                    "- automation_candidate=True 的用例可进入接口自动化候选集。",
                    f"- 验收标准数量：{len(acceptance_criteria['criteria'])}",
                ]
            ),
        }
