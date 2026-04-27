from __future__ import annotations

import json

from ai_pipeline.agents.api_mapper_agent import ApiMapperAgent
from ai_pipeline.agents.requirement_agent import RequirementAgent
from ai_pipeline.agents.testcase_agent import TestcaseAgent


def test_requirement_agent_extracts_cart_requirement_sections(tmp_path):
    requirement_path = tmp_path / "cart_prd.md"
    requirement_path.write_text(
        "\n".join(
            [
                "# 宠物商店系统购物车功能 PRD",
                "",
                "## 需求目标",
                "- 将宠物加入购物车",
                "- 在购物车中查看已加入的商品",
                "- 修改购买数量",
                "- 从购物车发起结算并生成订单",
                "",
                "## 业务流程",
                "1. 用户登录",
                "2. 点击加入购物车",
                "3. 点击去结算",
                "4. 生成订单",
                "",
                "## 业务规则",
                "- 加入购物车时不锁库存",
                "- 结算生成订单时校验库存",
                "- 失效商品默认不可参与结算",
                "",
                "## 异常提示示例",
                "- 用户未登录：请先登录",
                "- 商品下架：该宠物已下架",
            ]
        ),
        encoding="utf-8",
    )

    outputs = RequirementAgent().run(requirement_path)
    requirement_model = outputs["requirement_model"]

    assert requirement_model["title"] == "宠物商店系统购物车功能"
    assert requirement_model["goals"]
    assert requirement_model["core_flows"]
    assert requirement_model["business_rules"]
    assert requirement_model["exception_scenarios"]
    assert requirement_model["impact_scope"]
    assert any("加入购物车" in scenario["name"] for scenario in requirement_model["scenarios"])
    assert any("购物车结算" in scenario["name"] for scenario in requirement_model["scenarios"])


def test_testcase_agent_generates_cart_cases_with_automation_candidates():
    requirement_model = {
        "requirement_id": "REQ-CART-001",
        "title": "宠物商店系统购物车功能",
        "scenarios": [],
    }
    acceptance_criteria = {"requirement_id": "REQ-CART-001", "criteria": []}

    outputs = TestcaseAgent().run(requirement_model, acceptance_criteria)
    cases = outputs["test_cases"]["cases"]

    assert any(case["test_case_id"] == "TC-CART-ADD-001" for case in cases)
    assert any(case["test_case_id"] == "TC-CART-CHECKOUT-001" for case in cases)
    assert all("priority" in case for case in cases)
    assert all("automation_candidate" in case for case in cases)
    assert any(case["automation_candidate"] is True for case in cases)


def test_api_mapper_agent_maps_cart_cases_to_matching_apifox_paths():
    test_cases = {
        "requirement_id": "REQ-CART-001",
        "cases": [
            {
                "test_case_id": "TC-CART-ADD-001",
                "title": "加入购物车成功",
                "payload": {"petId": 1, "quantity": 1},
                "expected_status_codes": [200, 201],
            },
            {
                "test_case_id": "TC-CART-CHECKOUT-001",
                "title": "购物车结算成功生成订单",
                "payload": {},
                "expected_status_codes": [200, 201],
            },
        ],
    }
    api_document = {
        "info": {"title": "Pet Store"},
        "paths": {
            "/api/front/cart/items": {
                "get": {"summary": "查询购物车列表"},
                "post": {"summary": "加入购物车"},
                "delete": {"summary": "批量删除购物车商品"},
            },
            "/api/front/cart/items/{id}": {
                "delete": {"summary": "删除购物车商品"},
            },
            "/api/front/cart/checkout": {
                "post": {"summary": "购物车结算"},
            },
        },
    }

    outputs = ApiMapperAgent().run(test_cases, api_document)
    mappings = outputs["endpoint_mapping"]["mappings"]

    assert mappings[0]["path"] == "/api/front/cart/items"
    assert mappings[0]["method"] == "POST"
    assert mappings[1]["path"] == "/api/front/cart/checkout"
    assert mappings[1]["method"] == "POST"
    assert outputs["api_catalog"]["selected_interfaces"]


def test_api_mapper_agent_normalizes_cart_payloads_from_openapi_contract():
    test_cases = {
        "requirement_id": "REQ-CART-001",
        "cases": [
            {
                "test_case_id": "TC-CART-ADD-001",
                "title": "加入购物车成功",
                "payload": {"petId": "${valid_pet_id}", "quantity": 1},
                "expected_status_codes": [200, 201],
            },
            {
                "test_case_id": "TC-CART-BATCH-DELETE-001",
                "title": "批量删除购物车商品成功",
                "related_api_intent": "batch_delete_cart_items",
                "payload": {"cartItemIds": ["${cart_item_id_1}", "${cart_item_id_2}"]},
                "expected_status_codes": [200, 204],
            },
        ],
    }
    api_document = {
        "info": {"title": "Pet Store"},
        "paths": {
            "/api/front/cart/items": {
                "post": {"summary": "加入购物车"},
                "delete": {"summary": "批量删除购物车商品"},
            },
        },
    }

    outputs = ApiMapperAgent().run(test_cases, api_document)
    mappings = outputs["endpoint_mapping"]["mappings"]

    assert mappings[0]["payload"] == {"pet_id": "${valid_pet_id}", "quantity": 1}
    assert mappings[1]["payload"] == {"ids": ["${cart_item_id_1}", "${cart_item_id_2}"]}


def test_api_mapper_agent_prefers_single_delete_cart_item_path():
    test_cases = {
        "requirement_id": "REQ-CART-001",
        "cases": [
            {
                "test_case_id": "TC-CART-DELETE-001",
                "title": "删除单个购物车商品成功且不影响库存",
                "related_api_intent": "delete_cart_item",
                "payload": {},
                "expected_status_codes": [200, 204],
            },
        ],
    }
    api_document = {
        "info": {"title": "Pet Store"},
        "paths": {
            "/api/front/cart/items": {
                "delete": {"summary": "批量删除购物车商品"},
            },
            "/api/front/cart/items/{id}": {
                "delete": {"summary": "删除购物车商品"},
            },
        },
    }

    outputs = ApiMapperAgent().run(test_cases, api_document)
    mapping = outputs["endpoint_mapping"]["mappings"][0]

    assert mapping["path"] == "/api/front/cart/items/{id}"
    assert mapping["method"] == "DELETE"


def test_api_mapper_agent_outputs_expanded_interface_details_from_apifox_openapi():
    test_cases = {
        "requirement_id": "REQ-DETAIL-001",
        "cases": [
            {
                "test_case_id": "TC-DETAIL-001",
                "title": "create order with detail",
                "related_api_intent": "create_order",
                "payload": {"name": "demo"},
                "expected_status_codes": [200],
            }
        ],
    }
    api_document = {
        "openapi": "3.1.0",
        "info": {"title": "Detail Service"},
        "paths": {
            "/orders": {
                "post": {
                    "summary": "Create order",
                    "description": "Create order detail",
                    "tags": ["Order"],
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "CurrentUser",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "current user context",
                        },
                        {
                            "name": "dryRun",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "boolean"},
                        },
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CreateOrderRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "allOf": [
                                            {"$ref": "#/components/schemas/BaseResponse"},
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "data": {
                                                        "$ref": "#/components/schemas/OrderDetail"
                                                    }
                                                },
                                            },
                                        ]
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "CreateOrderRequest": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string", "description": "order name"},
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/OrderItem"},
                        },
                    },
                },
                "OrderItem": {
                    "type": "object",
                    "properties": {
                        "sku": {"type": "string", "description": "SKU"},
                        "quantity": {"type": "integer", "description": "quantity"},
                    },
                },
                "BaseResponse": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "msg": {"type": "string"},
                    },
                },
                "OrderDetail": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "format": "int64"},
                        "status": {"type": "string"},
                    },
                },
            }
        },
    }

    outputs = ApiMapperAgent().run(test_cases, api_document)
    interface = outputs["api_catalog"]["selected_interfaces"][0]
    mapping = outputs["endpoint_mapping"]["mappings"][0]

    assert interface["headers"][0]["name"] == "CurrentUser"
    assert interface["query_params"][0]["name"] == "dryRun"
    assert interface["request_body"]["content"]["application/json"]["schema"]["properties"]["items"]["items"][
        "properties"
    ]["sku"]["description"] == "SKU"
    assert interface["response_body"]["200"]["content"]["application/json"]["schema"]["properties"]["data"][
        "properties"
    ]["status"]["type"] == "string"
    assert mapping["interface_detail_status"] == "detail_fetched_from_apifox_openapi"
    assert "$ref" not in json.dumps(interface, ensure_ascii=False)
    assert "allOf" not in json.dumps(interface, ensure_ascii=False)
