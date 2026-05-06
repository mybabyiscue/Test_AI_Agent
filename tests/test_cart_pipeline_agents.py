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
    assert outputs["test_points"]["requirement_id"] == "REQ-CART-001"
    assert outputs["test_points"]["test_points"]
    assert any(point["linked_case_ids"] for point in outputs["test_points"]["test_points"])


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


def test_api_mapper_agent_request_schema_contains_full_interface_contract():
    test_cases = {
        "requirement_id": "REQ-DETAIL-002",
        "cases": [
            {
                "test_case_id": "TC-DETAIL-002",
                "title": "save livecode with full schema",
                "related_api_intent": "save_contact_way",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            }
        ],
    }
    api_document = {
        "openapi": "3.1.0",
        "info": {"title": "Livecode Service"},
        "paths": {
            "/contact/way/save": {
                "post": {
                    "summary": "save contact way",
                    "parameters": [
                        {
                            "name": "CurrentUser",
                            "in": "header",
                            "required": False,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["state", "categoryId"],
                                    "properties": {
                                        "state": {"type": "string"},
                                        "name": {"type": "string"},
                                        "categoryId": {"type": "integer"},
                                        "corpId": {"type": "string"},
                                        "welcomeConfigVO": {
                                            "type": "object",
                                            "properties": {
                                                "configType": {"type": "integer"},
                                            },
                                        },
                                    },
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
    }

    outputs = ApiMapperAgent().run(test_cases, api_document)
    request_schema = outputs["request_schema"]

    assert request_schema["path"] == "/contact/way/save"
    assert request_schema["method"] == "POST"
    assert request_schema["body_type"] == "application/json"
    assert request_schema["required_fields"] == ["state", "categoryId"]
    assert request_schema["interfaces"]
    interface = request_schema["interfaces"][0]
    assert interface["headers"][0]["name"] == "CurrentUser"
    assert interface["request_body"]["content"]["application/json"]["schema"]["properties"]["welcomeConfigVO"][
        "properties"
    ]["configType"]["type"] == "integer"


def test_api_mapper_agent_reads_database_context_from_knowledge_base_for_livecode_cases():
    test_cases = {
        "requirement_id": "REQ-SAAS-LIVECODE-ONLINE-OFFLINE-001",
        "cases": [
            {
                "test_case_id": "TC-LIVECODE-001",
                "title": "save contact way with next auto enable time",
                "related_api_intent": "save_contact_way",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-005",
                "title": "change online status manually",
                "related_api_intent": "change_online_status",
                "payload": {"status": 0, "source": 2},
                "expected_status_codes": [200],
            },
        ],
    }
    api_document = {
        "info": {"title": "Livecode Service"},
        "paths": {
            "/api/contact/way/save": {"post": {"summary": "save contact way"}},
            "/api/acquisition/user/online/change": {"post": {"summary": "change online status"}},
        },
    }

    outputs = ApiMapperAgent().run(test_cases, api_document, database_scope="saas")

    table_names = {
        table["table_name"]
        for table in outputs["database_catalog"]["tables"]
    }
    case_mappings = outputs["database_mapping"]["mappings"]

    assert outputs["database_catalog"]["knowledge_scope"] == "saas"
    assert "wework_contact_way" in table_names
    assert any(item["matched_tables"] for item in case_mappings)
    assert "wework_acquisition_user_online_status" in outputs["database_mapping"]["summary"]["missing_tables"]


def test_api_mapper_agent_prefers_livecode_endpoints_for_livecode_intents():
    test_cases = {
        "requirement_id": "REQ-SAAS-LIVECODE-ONLINE-OFFLINE-001",
        "cases": [
            {
                "test_case_id": "TC-LIVECODE-001",
                "title": "新增活码并配置次日自动上线时间",
                "related_api_intent": "save_contact_way",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-003",
                "title": "保存获客链接并检查是否支持 nextAutoEnableTime",
                "related_api_intent": "save_acquisition_link",
                "payload": {"nextAutoEnableTime": "2099-12-31 10:00:00"},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-004",
                "title": "查询员工当前上下线状态列表",
                "related_api_intent": "list_online_status",
                "payload": {},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-005",
                "title": "手动下线员工成功",
                "related_api_intent": "change_online_status",
                "payload": {"status": 0},
                "expected_status_codes": [200],
            },
            {
                "test_case_id": "TC-LIVECODE-008",
                "title": "自动上线成功后顺延 next_auto_enable_time 到下一天同一时刻",
                "related_api_intent": "sync_org",
                "payload": {},
                "expected_status_codes": [200],
            },
        ],
    }
    api_document = {
        "info": {"title": "Livecode Service"},
        "paths": {
            "/cc/quality/inspectors/add": {"post": {"summary": "无关接口"}},
            "/groupcontact/way/save": {"post": {"summary": "群活码保存"}},
            "/contact/way/save": {"post": {"summary": "活码保存"}},
            "/acquisition/link/saveOrUpdate": {"post": {"summary": "新增或保存获客链接"}},
            "/acquisition/user/online/list": {"get": {"summary": "查询员工当前上下线状态列表"}},
            "/acquisition/user/online/change": {"post": {"summary": "手动调整员工上下线状态"}},
            "/tenant/shop/sync": {"post": {"summary": "同步店铺"}},
            "/cp/org/synchro": {"post": {"summary": "同步企微组织"}},
        },
    }

    outputs = ApiMapperAgent().run(test_cases, api_document)
    mappings = {item["test_case_id"]: item for item in outputs["endpoint_mapping"]["mappings"]}

    assert mappings["TC-LIVECODE-001"]["path"] == "/contact/way/save"
    assert mappings["TC-LIVECODE-003"]["path"] == "/acquisition/link/saveOrUpdate"
    assert mappings["TC-LIVECODE-004"]["path"] == "/acquisition/user/online/list"
    assert mappings["TC-LIVECODE-005"]["path"] == "/acquisition/user/online/change"
    assert mappings["TC-LIVECODE-008"]["path"] == "/cp/org/synchro"
