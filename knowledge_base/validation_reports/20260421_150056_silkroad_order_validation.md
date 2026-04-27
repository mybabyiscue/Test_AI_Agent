# 丝路订单相关知识库验证报告

## 文件说明

- 文件名称：20260421_150056_silkroad_order_validation.md
- 文件作用：验证当前本地知识库中“丝路订单”相关数据库结构和接口文档是否已同步、是否完整、是否可支撑后续测试使用。
- 文件主要内容：订单相关数据表、订单相关接口详细信息、同步完整性检查、缺失项、问题清单和后续测试可用性结论。
- 所属阶段：接口获取 Agent 知识库验证阶段。
- 查看方式：本文件已使用 UTF-8 with BOM 编码保存，建议使用 VS Code、Typora、Notepad++、WPS 或 Windows 记事本打开。

## 1. 验证范围

- 数据库来源目录：`E:\xjcode\Test_AI_Agent\knowledge_base\silkroad\database`
- 接口来源文件：`E:\xjcode\Test_AI_Agent\knowledge_base\silkroad\apis\apifox_project_776242.json`
- 丝路接口总数：2646 条。
- 丝路数据库总表数：1137 张。
- 关键词：`订单`、`order`、`oms`、`下单`、`支付`、`履约`、`发货`、`售后`、`退款`、`结算`。
- 说明：由于“工单 work_order”也包含 `order`，本报告将其识别为扩展相关，不作为订单主链路核心对象。

## 2. 验证结论

- 广义订单相关表：433 张。
- 核心订单相关表：266 张。
- 广义订单相关接口：643 条。
- 核心订单相关接口：542 条。
- 核心接口方法分布：GET=187，POST=355
- 核心接口涉及模块数：112 个。
- 可用性结论：当前知识库可以支撑后续“接口枚举、接口检索、字段结构理解、测试用例到接口候选映射、自动化脚本初稿生成”；但若要直接稳定执行自动化，还需要补齐鉴权规则、环境 Base URL、部分接口路径规范和缺失描述。

## 3. 订单相关数据表检查

### 3.1 数据库命中分布

- `ec`：广义命中 301 张表。
- `crm_core`：广义命中 66 张表。
- `oms`：广义命中 27 张表。
- `center`：广义命中 25 张表。
- `cx`：广义命中 14 张表。

### 3.2 核心订单表清单

| 库名 | 表名 | 表注释 | 字段数 | 索引数 | 主键 | 关键关联字段 |
|---|---|---|---:|---:|---|---|
| `ec` | `20210528order` |  | 1 | 0 | 未识别 | orderCode() |
| `ec` | `aa1_orders` | 订单表 | 65 | 14 | Id, OrderTime | Code(订单编号), CustomerId(客户ID) |
| `ec` | `aa1_order_batch_task` | 批量任务 | 13 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_cancel` | 订单撤单表 | 12 | 1 | Id | OrderId(订单ID) |
| `ec` | `aa1_order_code_rule` | 订单编号规则 | 9 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_coupon` | 订单使用礼券记录表 | 9 | 3 | Id | OrderId(订单ID) |
| `ec` | `aa1_order_customer_reject_statistics` | 客户拒收统计表 | 11 | 3 | Id | CustomerId(客户ID) |
| `ec` | `aa1_order_department_control` | 商品下单控制 | 7 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_department_goods_detail` | 下单部门商品明细 | 13 | 4 | Id | GoodsId(商品ID) |
| `ec` | `aa1_order_express_fee` | 订单快递费用 | 21 | 2 | Id | OrderId(订单Id) |
| `ec` | `aa1_order_extend` | 订单扩展表 | 11 | 5 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `aa1_order_financial_confirm` | 财务确认回款表 | 17 | 3 | Id | OrderId(订单id) |
| `ec` | `aa1_order_financial_review` | 财务审单表 | 14 | 2 | Id | OrderId(订单ID) |
| `ec` | `aa1_order_flow` | 订单操作记录表 | 17 | 2 | Id | OrderId(订单ID) |
| `ec` | `aa1_order_inner` | 出库订单 | 35 | 9 | Id | Code(订单编号), CustomerId(客户id) |
| `ec` | `aa1_order_inner_item` | 出库订单明细 | 14 | 4 | Id | OrderId(订单id), ProductId(商品id) |
| `ec` | `aa1_order_item` | 订单条目表 | 24 | 6 | Id | OrderId(订单ID), GoodsId(商品ID) |
| `ec` | `aa1_order_manage_subsidy_flow` | 经理补贴流水表 | 12 | 1 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `aa1_order_media_asses_config` | 媒体中心考核办法 | 9 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_media_asses_detail` | 媒体考核办法明细 | 15 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_member_asses_config` | 会员,启航考核办法 | 9 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_member_asses_detail` | 会员启航考核办法明细 | 14 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_money` | 订单金额表 | 33 | 3 | Id | OrderId(订单ID) |
| `ec` | `aa1_order_package_goods` | 订单套餐商品明细 | 17 | 4 | Id | OrderId(订单ID), GoodsId(商品ID), FictitiousGoodsId(套餐商品ID) |
| `ec` | `aa1_order_reject_record` | 订单拒收记录 | 10 | 1 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `aa1_order_reject_return_freight` | 订单拒收返还运费 | 15 | 4 | Id | OrderId(订单ID), CustomerId(客户ID) |
| `ec` | `aa1_order_review` | 审单表 | 33 | 9 | Id | OrderId(订单id), Code(订单编号), CustomerId(客户id) |
| `ec` | `aa1_order_reviewer` | 审单员表 | 11 | 5 | Id | 未明显识别 |
| `ec` | `aa1_order_review_manager` | 经理审单表 | 12 | 4 | Id | OrderId(订单id) |
| `ec` | `aa1_order_review_rule_row` | 必审规则行'; | 11 | 2 | Id | 未明显识别 |
| `ec` | `aa1_order_review_rule_type` | 必审规则类型 | 8 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_review_task` | 审单任务表 | 11 | 4 | Id | OrderId(订单ID) |
| `ec` | `aa1_order_statistics` | 订单统计表 | 11 | 2 | Id | CustomerId(客户ID) |
| `ec` | `aa1_order_status` | 订单状态值 | 9 | 1 | Id | 未明显识别 |
| `ec` | `aa1_order_stock_release` | 订单释放库存表 | 10 | 2 | Id | OrderId(订单ID) |
| `ec` | `aa1_order_suit_examine_rule` | 符合订单必审规则 | 17 | 1 | Id | OrderId(订单ID), GoodsIds(必审商品) |
| `ec` | `aa1_order_user_reject_statistics` | 用户坐席拒收统计表 | 14 | 3 | Id | 未明显识别 |
| `ec` | `after_sale_big_award` | 售后工单订单扣除奖励计算结果表 | 10 | 1 | Id | OrderId(订单id) |
| `ec` | `after_sale_product_award` | 售后工单订单扣除奖励计算结果表 | 10 | 1 | Id | OrderId(订单id) |
| `ec` | `after_sale_upgrade_award` | 售后工单订单扣除奖励计算结果表 | 10 | 1 | Id | OrderId(订单id) |
| `ec` | `distribution_order` | 经销商订单 | 43 | 5 | Id | CustomerId(客户id), Code(订单编号), PlatformOrderCode(平台订单编号) |
| `ec` | `distribution_order_express_fee` | 经销商订单快递费用 | 21 | 2 | Id | OrderId(订单Id) |
| `ec` | `distribution_order_flow` | 订单流水表 | 10 | 3 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `distribution_order_freight_warn` | 订单预估运费表 | 11 | 2 | Id | OrderId(订单ID) |
| `ec` | `distribution_order_item` | 分销商订单商品条目表 | 16 | 2 | Id | OrderId(订单ID), GoodsId(商品ID) |
| `ec` | `distribution_order_policy` | 订单套餐表 | 11 | 3 | Id | OrderId(订单ID) |
| `ec` | `distribution_order_waybill_code` | 订单发运运单号表 | 11 | 1 | Id | OrderId(订单id) |
| `ec` | `goods_order_control` | 下单控制商品表 | 9 | 3 | ID | GoodsId(商品ID) |
| `ec` | `goods_order_dept_control` | 下单部门控制 | 6 | 1 | Id | 未明显识别 |
| `ec` | `goods_order_dept_control_dept` | 下单部门控制部门明细 | 9 | 3 | Id | 未明显识别 |
| `ec` | `goods_order_dept_control_product` | 下单部门控制商品 | 8 | 3 | Id | GoodsId(商品ID) |
| `ec` | `goods_order_dept_control_product_sku` | 下单控制商品对应的SKU表 | 11 | 1 | Id | ControlProductId(控制部门商品id), GoodsId(商品ID) |
| `ec` | `goods_order_dept_control_user` | 下单部门控制用户明细 | 10 | 5 | Id | 未明显识别 |
| `ec` | `goods_sku_control` | 配置商品是否可下单 | 9 | 2 | Id | 未明显识别 |
| `ec` | `gy_order` | 管易订单-主表 | 60 | 1 | Id | ConvertOrderId(转换成丝路订单id) |
| `ec` | `gy_order_delivery` | 管易订单-物流信息 | 19 | 1 | Id | GyOrderId(管易订单id), GyOrderCode(管易订单编号) |
| `ec` | `gy_order_invoice` | 管易订单-开票信息 | 18 | 1 | Id | GyOrderId(管易订单id), GyOrderCode(管易订单编号), InvoiceContent(管易订单编号) |
| `ec` | `gy_order_item` | 管易订单-商品信息 | 25 | 1 | Id | GyOrderId(管易订单id), GyOrderCode(管易订单编号) |
| `ec` | `gy_order_payment` | 管易订单-支付信息 | 12 | 1 | Id | GyOrderId(管易订单id), GyOrderCode(管易订单编号) |
| `ec` | `invoice_make_history` | 丝路订单开票记录表 | 21 | 4 | Id | WxOrderId(授权给微信的订单号), OrderCode(丝路订单编号) |
| `ec` | `kai_mon_rabbit_order` | 凯蒙灵兔订单主表 | 42 | 1 | id | id(订单ID（UUID）) |
| `ec` | `kai_mon_rabbit_order_item` | 凯蒙灵兔订单子表 | 6 | 1 | id | 未明显识别 |
| `ec` | `logistics_check_fee` | 物流订单核算表 | 38 | 3 | Id | 未明显识别 |
| `ec` | `logistics_check_fee_copy1` | 物流订单核算表 | 38 | 3 | Id | 未明显识别 |
| `ec` | `logistics_order_filter_flow` | 物流筛单请求流水表，存放每次筛单请求后快递商返回的响应结果 | 10 | 1 | Id | 未明显识别 |
| `ec` | `logistics_route_order_status` | 路由代码订单状态信息 | 13 | 1 | Id | 未明显识别 |
| `ec` | `orders` | 订单表 | 42 | 14 | Id, OrderTime | Code(订单编号), CustomerId(客户ID) |
| `ec` | `orders_copy1` | 订单表 | 42 | 7 | Id | Code(订单编号), CustomerId(客户ID) |
| `ec` | `orders_copy2` | 订单表 | 42 | 7 | Id | Code(订单编号), CustomerId(客户ID) |
| `ec` | `orders_copy3` | 订单表 | 42 | 7 | Id | Code(订单编号), CustomerId(客户ID) |
| `ec` | `orders_t` | 订单表 | 44 | 7 | UUID | Code(订单编号), CustomerId(客户ID) |
| `ec` | `order_ai_outbound_address_mark_record` | AI外呼地址异常记录表 | 12 | 3 | Id | CustomerId(客户Id) |
| `ec` | `order_area_control` | 下单区域控制 | 6 | 1 | ID | 未明显识别 |
| `ec` | `order_area_detail` | 下单区域详细表 | 10 | 5 | Id | 未明显识别 |
| `ec` | `order_area_diff` | 第三方与丝路省市区映射表 | 17 | 2 | Id | 未明显识别 |
| `ec` | `order_attachment` | 订单附件表 | 8 | 2 | Id | OrderId(订单ID) |
| `ec` | `order_batch_task` | 批量任务 | 13 | 1 | Id | 未明显识别 |
| `ec` | `order_cancel_flow` | 订单撤单记录表 | 9 | 3 | Id | OrderId(订单ID) |
| `ec` | `order_channel_push` | 视频号小店推送表 | 13 | 3 | Id | OuterOrderId(外部订单号) |
| `ec` | `order_claim_carrier_config` | 理赔承运商倍率表 | 12 | 1 | Id | 未明显识别 |
| `ec` | `order_claim_relation` | 理赔订单和原订单关联表 | 9 | 1 | Id | OriginOrderCode(原订单编码), OrderId(原订单ID) |
| `ec` | `order_code_rule` | 订单编号规则 | 15 | 5 | Id | 未明显识别 |
| `ec` | `order_collection_other` |  | 8 | 2 | Id | OrderId(订单id) |
| `ec` | `order_config` | 订单包邮配置 | 19 | 2 | Id | GoodsIds(商品ID) |
| `ec` | `order_config_free` | 订单包邮多个配置 | 12 | 2 | Id | GoodsIds(商品ID) |
| `ec` | `order_consumption_config` |  | 10 | 1 | Id | 未明显识别 |
| `ec` | `order_continue_times_user` | 连续未处理坐席表 | 10 | 1 | Id | 未明显识别 |
| `ec` | `order_continue_times_user_cutomer` | 连续未处理客户表 | 9 | 1 | Id | CustomerId(客户id) |
| `ec` | `order_coupon` | 订单使用礼券表 | 11 | 3 | Id | OrderId(订单ID) |
| `ec` | `order_customer_channel` | 客户渠道表 | 12 | 3 | Id | 未明显识别 |
| `ec` | `order_customer_channel_item` | 客户渠道配置项表 | 12 | 6 | Id | GoodsId(商品ID  tips: ec.goods表ID) |
| `ec` | `order_customer_channel_record` | 客户下单渠道记录表 | 9 | 2 | Id | OrderId(订单ID) |
| `ec` | `order_customer_consumable_quota_config` | 客户消费额度配置 | 12 | 1 | Id | CustomerId(客户id) |
| `ec` | `order_customer_monthly_spending_limits` | 客户标签对应每月消费限制表 | 10 | 2 | Id | 未明显识别 |
| `ec` | `order_customer_monthly_spending_limits_detail` | 客户标签对应每月消费限制详情表 | 12 | 2 | Id | 未明显识别 |
| `ec` | `order_dealer` |  | 10 | 2 | Id | OrderId(订单Id) |
| `ec` | `order_dealer_cancel` |  | 11 | 3 | Id | OrderId(订单Id) |
| `ec` | `order_dealer_cancel_item` |  | 12 | 2 | Id | 未明显识别 |
| `ec` | `order_delivery_batch` | 订单发货批次表 | 22 | 9 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `order_delivery_batch_copy1` | 订单发货批次表 | 22 | 9 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `order_delivery_batch_goods` | 订单批次商品详情 | 30 | 8 | Id | OrderId(订单ID), BatchId(批次ID), GoodsId(商品ID) |
| `ec` | `order_delivery_batch_goods_revise` | 订单批次商品详情修订 | 29 | 1 | Id | OrderId(订单ID), BatchId(批次ID), GoodsId(商品ID) |
| `ec` | `order_delivery_rate_call_interval` | 妥投率外呼时间间隔配置表 | 9 | 1 | Id | 未明显识别 |
| `ec` | `order_delivery_waybill_code` | 订单发运运单号表 | 15 | 1 | Id | OrderId(订单id), BatchId(发货批次id) |
| `ec` | `order_detail_config` | 订单备注配置表 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_distributin0623` |  | 14 | 0 | 未识别 | 未明显识别 |
| `ec` | `order_distribution_push` | 分销商订单导入推送信息 | 27 | 2 | Id | BatchId(导入批次号), PlatformOrderCode(平台订单编号) |
| `ec` | `order_double_achievement_detail` | 业绩双算表 | 21 | 1 | Id | CustomerId(客户id), OrderId(订单id) |
| `ec` | `order_douyin_flow` | OMS调用抖音流水表 | 11 | 2 | Id | 未明显识别 |
| `ec` | `order_douyin_push` | 抖音推送信息表 | 25 | 2 | Id | OrderId(订单号) |
| `ec` | `order_employee_delivery_rate` | 员工妥投率表 | 8 | 2 | Id | 未明显识别 |
| `ec` | `order_erp_config` |  | 18 | 1 | Id | 未明显识别 |
| `ec` | `order_erp_config_temp` |  | 15 | 1 | Id | 未明显识别 |
| `ec` | `order_erp_flow` | 订单调用erp流水表 | 12 | 3 | Id | OrderCode(订单编号) |
| `ec` | `order_erp_org_config` | 部门推送ERP特殊配置 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_erp_ratio` | erp推送公司商品倍率 | 8 | 2 | Id | 未明显识别 |
| `ec` | `order_erp_revise` |  | 7 | 1 | Id | OrderCode() |
| `ec` | `order_erp_rule` | 订单推送ERP规则表 | 10 | 1 | Id | 未明显识别 |
| `ec` | `order_erp_sku_config` | SKU推送ERP特殊逻辑配置 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_erp_temp` |  | 2 | 2 | Id | orderCode() |
| `ec` | `order_erp_type` | 订单类型对应ERP销售类型 | 8 | 2 | Id | 未明显识别 |
| `ec` | `order_examine_config` | 审单配置 | 22 | 1 | Id | 未明显识别 |
| `ec` | `order_examine_customer_grade` | 审单配置客户级别 | 9 | 3 | Id | 未明显识别 |
| `ec` | `order_examine_department` | 审单配置部门 | 9 | 3 | Id | 未明显识别 |
| `ec` | `order_examine_goods` | 审单配置商品 | 9 | 3 | Id | GoodsId(商品ID) |
| `ec` | `order_examine_segmentation` | 审单必审标签 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_examine_user` | 审单配置坐席 | 9 | 3 | Id | 未明显识别 |
| `ec` | `order_express_fee` | 订单快递费用 | 23 | 2 | Id | OrderId(订单Id) |
| `ec` | `order_extend` | 订单扩展表 | 44 | 3 | Id | OrderId(订单ID), CustomerId(客户ID), OuterOrderCode(外部系统订单号), BatchOrderCode(中台订单号) |
| `ec` | `order_extend2` | 订单扩展表 | 31 | 4 | Id | OrderId(订单ID), CustomerId(客户ID), OuterOrderCode(外部系统订单号) |
| `ec` | `order_extend_wx` |  | 12 | 1 | Id | OrderId(订单ID) |
| `ec` | `order_extend_yuanshu` |  | 38 | 3 | Id | OrderId(订单Id), CustomerId(客户ID), OrderCode(订单编号) |
| `ec` | `order_external_payment` |  | 17 | 3 | Id | OrderId(订单Id), CustomerId(客户Id) |
| `ec` | `order_external_push` | 外部订单推送信息表 | 11 | 2 | Id | 未明显识别 |
| `ec` | `order_file` | 订单图片信息表 | 9 | 1 | Id | OrderId(订单id) |
| `ec` | `order_financial_confirm` | 订单财务确认表 | 22 | 2 | Id | OrderId() |
| `ec` | `order_financial_statistics_config` |  | 10 | 1 | Id | 未明显识别 |
| `ec` | `order_flow` | 订单流水表 | 11 | 4 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `order_flow1` | 订单流水表 | 10 | 4 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `order_flow_20220812` | 订单流水表 | 10 | 3 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `order_flow_20230517` | 订单流水表 | 10 | 4 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `order_freight_rule` | 订单运费规则（废弃） | 10 | 2 | Id | 未明显识别 |
| `ec` | `order_freight_warn` | 订单预估运费表 | 12 | 2 | Id | OrderId(订单ID) |
| `ec` | `order_freight_warn_receiver` | 订单运费超标消息接收人配置表 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_goods_collection` | 订单商品收藏表 | 9 | 1 | Id | 未明显识别 |
| `ec` | `order_goods_collection_item` | 订单商品收藏项表 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_goods_customer_habits` | 用户产品服用习惯表 | 15 | 2 | Id | CustomerId(用户ID) |
| `ec` | `order_goods_detail` | 订单商品明细表 | 30 | 8 | Id | OrderId(订单ID), GoodsId(商品ID) |
| `ec` | `order_goods_detail_summary` |  | 12 | 3 | Id | OrderId(订单ID), GoodsId(商品ID) |
| `ec` | `order_goods_habits_tag` | 需配置的商品标签表 | 7 | 1 | Id | 未明显识别 |
| `ec` | `order_goods_sale_customer_unlimited_config` | 产品购买不限制客户配置表 | 8 | 1 | Id | CustomerId(客户id) |
| `ec` | `order_inventory_check` | 订单库存校验表 | 11 | 3 | Id | OrderId(订单ID) |
| `ec` | `order_invoice_corp_config` | 订单发票公司配置表 | 15 | 1 | Id | 未明显识别 |
| `ec` | `order_invoice_message` | 订单发票信息表 | 9 | 1 | Id | CustomerId(客户id), OrderCode(订单号) |
| `ec` | `order_item` | 订单套餐表 | 23 | 3 | Id | OrderId(订单ID) |
| `ec` | `order_jd_push` | 京东推送信息表 | 23 | 2 | Id | OrderId(订单号), BatchId(导入批次号) |
| `ec` | `order_jst_push` | 聚水潭推送信息表 | 22 | 2 | Id | OrderId(第三方订单号), BatchId(导入批次号) |
| `ec` | `order_jushutan_config` |  | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_kuaishou_push` |  | 25 | 4 | Id | Oid(订单id), OrderId(聚水潭第三方订单编号) |
| `ec` | `order_manage_review_flow` | 订单经理审核流水表 | 11 | 4 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `order_money` | 订单金额表 | 41 | 2 | Id | OrderId(订单ID), CustomerId(客户ID) |
| `ec` | `order_one_key` |  | 10 | 3 | Id | CustomerId(), OrderId() |
| `ec` | `order_outer_data_carrier` |  | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_outer_extend` | 外部订单扩展表 | 8 | 2 | Id | OrderId(订单ID) |
| `ec` | `order_outer_goods_detail` | 第三方店铺订单商品明细表 | 14 | 2 | Id | OrderId(订单ID) |
| `ec` | `order_partial_payments` | 订单部分支付表 | 9 | 3 | Id | OrderId(订单ID), CustomerId(客户ID) |
| `ec` | `order_partner` | 合作方表 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_partner_export_flow` |  | 7 | 1 | Id | OrderCode(订单编号) |
| `ec` | `order_partner_goods` | 合作方配置商品表 | 9 | 2 | Id | SkuGoodsCode(商品Id) |
| `ec` | `order_partner_user` | 用户合作方权限配置表 | 8 | 2 | Id | 未明显识别 |
| `ec` | `order_payment_flow` | 客户收款项目生成流水 | 12 | 5 | Id | CustomerId(客户Id) |
| `ec` | `order_payment_info` | 订单代付表 | 10 | 1 | Id | CustomerId(客户id) |
| `ec` | `order_pdd_push` | 拼多多推送信息表 | 23 | 3 | Id | OrderId(订单号) |
| `ec` | `order_plateform` |  | 2 | 1 | Id | 未明显识别 |
| `ec` | `order_printer_fee_config` |  | 16 | 1 | Id | 未明显识别 |
| `ec` | `order_printer_limit_flow` |  | 9 | 3 | Id | OrderId(订单id), CustomerId(客户id) |
| `ec` | `order_push_config` | 订单推送配置信息表 | 10 | 1 | Id | 未明显识别 |
| `ec` | `order_rabbit_push` | 兔灵推送信息表 | 22 | 3 | Id | OrderCode(订单号 兔灵), OrderId(订单号 兔灵uuid), BatchId(导入批次号) |
| `ec` | `order_reject_record` | 订单拒收记录 | 10 | 3 | Id | OrderId(订单ID), OrderCode(订单编号) |
| `ec` | `order_reminder_config` | 服用提醒配置表 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_review` | 订单审核表 | 43 | 3 | Id | OrderId(订单ID), OrderCode(订单编号), CustomerId(客户ID) |
| `ec` | `order_review_appraise` | 订单满意度调研表 | 11 | 2 | Id | OrderId(订单ID) |
| `ec` | `order_review_config` | 审单配置表 | 16 | 2 | Id | 未明显识别 |
| `ec` | `order_review_config_record` | 经理补贴配置修改记录表 | 9 | 2 | Id | 未明显识别 |
| `ec` | `order_review_info_person` | 订单审核信息接收人表 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_revise` | 订单修订工单表 | 43 | 2 | Id | OrderId(订单ID), OrderCode(订单编号), CustomerId(客户ID) |
| `ec` | `order_revise_before` | 订单修订前工单表 | 24 | 1 | Id | OrderId(订单ID), OrderCode(订单编号), CustomerId(客户ID), OrderReviseId(修正订单ID) |
| `ec` | `order_revise_picurls` | 订单修订图片urls | 8 | 2 | Id | 未明显识别 |
| `ec` | `order_risk_control_config` | 订单风险控制参数配置表 | 9 | 1 | Id | 未明显识别 |
| `ec` | `order_saas_push` | Saas推送信息表 | 12 | 5 | Id | OrderCode(订单编号(Saas)) |
| `ec` | `order_service_charge_detail` | 订单服务费详细商品 | 16 | 3 | Id | GoodsId(添加商品ID) |
| `ec` | `order_service_line_count` |  | 3 | 1 | Id | 未明显识别 |
| `ec` | `order_shark_push` | 鲨域推送信息表 | 17 | 2 | Id | OrderCode(鲨域订单号) |
| `ec` | `order_shop` | 店铺基础信息表 | 35 | 2 | Id | ThirdCustomerId(第三方运单号使用默认客户) |
| `ec` | `order_shop_copy1` | 店铺基础信息表 | 32 | 2 | Id | ThirdCustomerId(第三方运单号使用默认客户) |
| `ec` | `order_shop_extend` | 店铺基础信息表 | 17 | 1 | Id | 未明显识别 |
| `ec` | `order_shop_extend_231128` | 店铺基础信息表 | 16 | 1 | Id | 未明显识别 |
| `ec` | `order_shop_notice` | 店铺异常信息-通知配置表 | 9 | 1 | Id | 未明显识别 |
| `ec` | `order_shop_shipper` | 货主对应关系 | 8 | 1 | Id | 未明显识别 |
| `ec` | `order_shop_temp` | 店铺基础信息表 | 32 | 2 | Id | ThirdCustomerId(第三方运单号使用默认客户) |
| `ec` | `order_shop_template` | 订单发送提示信息表 | 9 | 1 | Id | 未明显识别 |
| `ec` | `order_shop_template_231128` | 订单发送提示信息表 | 9 | 1 | Id | 未明显识别 |
| `ec` | `order_sidebar_refund_flow` | 侧边栏下单退款流水表 | 12 | 1 | Id | OrderCode(订单号) |
| `ec` | `order_sidebar_reorder_flow` | 侧边栏下单重新制单流水表 | 8 | 1 | Id | OrderCode(原订单号), NewOrderCode(新订单号) |
| `ec` | `order_sku_statistic` | 订单商品统计配置表 | 11 | 2 | Id | 未明显识别 |
| `ec` | `order_sms_flow` | 订单短信流水表 | 12 | 4 | Id | OrderId(订单ID), CustomerId(客户ID) |
| `ec` | `order_stock` |  | 4 | 1 | id | orderCode() |
| `ec` | `order_suit_examine_rule` | 符合订单必审规则 | 21 | 1 | Id | OrderId(订单ID), GoodsIds(必审商品) |
| `ec` | `order_suit_examine_seg` | 符合订单必审标签 | 9 | 2 | Id | OrderId(订单ID) |
| `ec` | `order_taobao_push` | 淘宝推送信息表 | 17 | 1 | Id | 未明显识别 |
| `ec` | `order_tb_push` | 淘宝推送信息表 | 21 | 2 | Id | OrderId(订单号), BatchId(导入批次号) |
| `ec` | `order_test123` |  | 2 | 0 | 未识别 | CustomerId() |
| `ec` | `order_test456` |  | 2 | 0 | 未识别 | CustomerId() |
| `ec` | `order_third_party_mapping` |  | 8 | 1 | Id | OrderId(订单Id), JuShuiTanOrderId(聚水潭订单) |
| `ec` | `order_tm_push` | 天猫推送信息表 | 17 | 2 | Id | OrderId(订单号), BatchId(导入批次号) |
| `ec` | `order_transfer_code` | 订单交易表 | 10 | 3 | Id | OrderCode(), OrderId() |
| `ec` | `order_transform_goods_detail` | 订单移交商品信息表 | 20 | 3 | Id | GoodsId(商品id) |
| `ec` | `order_transform_info` | 订单移交信息 | 18 | 6 | Id | CustomerId(客户id), OrderId(订单id), NewOrderId(72小时未下单生成的享悦订单id) |
| `ec` | `order_transform_info_temp` |  | 7 | 1 | Id | 未明显识别 |
| `ec` | `order_transform_item` | 订单套餐表 | 23 | 3 | Id | TransformId(移交订单ID) |
| `ec` | `order_transform_money` |  | 9 | 2 | Id | TransformId(移交订单id) |
| `ec` | `order_transform_money_copy1` |  | 9 | 2 | Id | TransformId(移交订单id) |
| `ec` | `order_transform_punish` | 订单处罚坐席表 | 10 | 3 | Id | 未明显识别 |
| `ec` | `order_transform_punish_customer` | 订单处罚客户表 | 9 | 3 | Id | CustomerId(客户id) |
| `ec` | `order_weimob_push` | 微盟推送信息表 | 28 | 2 | Id | OrderId(订单号) |
| `ec` | `order_work_flow` |  | 9 | 2 | Id | OrderCode(订单编号) |
| `ec` | `order_wxapp_config` | 订单使用付款小程序配置表 | 11 | 1 | Id | 未明显识别 |
| `ec` | `order_xiaoe_push` | 小鹅通推送信息表 | 15 | 2 | Id | 未明显识别 |
| `ec` | `order_youzan_flow` | 订单调用erp流水表 | 11 | 2 | Id | OrderCode(订单编号) |
| `ec` | `order_youzan_push` | 有赞推送信息表 | 17 | 2 | Id | 未明显识别 |
| `ec` | `order_youzan_push_item` |  | 31 | 4 | Id | Tid(外部订单id，关联ec.order_extend.Outer...), ItemId(商品id) |
| `ec` | `order_yuanshu_push` | 元数推送信息表 | 14 | 3 | Id | 未明显识别 |
| `ec` | `policy_coupon_grant_customer_level` | 礼券发放下单前客户级别 | 8 | 3 | Id | 未明显识别 |
| `ec` | `policy_order_with_goods_gift` | 随货资料配置表 | 17 | 1 | Id | 未明显识别 |
| `ec` | `policy_order_with_goods_gift_contains_goods` | 随货资料配置订单包含商品表 | 10 | 1 | Id | GoodsId(商品id) |
| `ec` | `policy_order_with_goods_gift_delivery_goods` | 随货资料发货商品表 | 10 | 1 | Id | GoodsId(商品id) |
| `ec` | `policy_order_with_goods_gift_dept` | 随货资料配置部门表 | 9 | 1 | Id | 未明显识别 |
| `ec` | `test_order` | VIEW | 42 | 0 | 未识别 | Code(订单编号), CustomerId(客户ID) |
| `ec` | `work_order_info_dic_mapping` |  | 8 | 0 | 未识别 | 未明显识别 |
| `oms` | `oms_data_carrier` | 物流承运商 | 41 | 1 | id | 未明显识别 |
| `oms` | `oms_delivery_batch` | 订单发货批次表 | 27 | 1 | Id | OrderId(订单ID), OuterOrderCode(外部系统订单号) |
| `oms` | `oms_delivery_batch_goods` | 订单批次商品详情 | 31 | 1 | Id | BatchId(批次ID), GoodsId(商品ID), OrderId(订单编号) |
| `oms` | `oms_delivery_batch_goods_revise` | 订单批次商品详情修订 | 29 | 2 | Id | OrderId(订单ID), BatchId(批次ID), GoodsId(商品ID) |
| `oms` | `oms_delivery_waybill_code` | 订单发运运单号表 | 14 | 1 | Id | OrderId(订单编号), BatchId(发货批次id) |
| `oms` | `oms_erp_flow` | 订单调用erp流水表 | 12 | 3 | Id | OrderCode(订单编号) |
| `oms` | `oms_erp_revise` |  | 9 | 2 | Id | OrderId(订单ID), BatchId(批次ID), OrderCode(批次号) |
| `oms` | `oms_erp_rule_1` | 订单推送ERP规则表 | 10 | 1 | Id | 未明显识别 |
| `oms` | `oms_erp_type_1` | 订单类型对应ERP销售类型 | 8 | 2 | Id | 未明显识别 |
| `oms` | `oms_extend` | 订单扩展表 | 26 | 1 | Id | OrderId(订单ID) |
| `oms` | `oms_flow` | 订单流水表 | 10 | 1 | Id | OrderId(订单ID), BatchId(批次ID) |
| `oms` | `oms_freight_warn` | 订单预估运费表 | 12 | 2 | Id | OrderId(订单ID) |
| `oms` | `oms_freight_warn_receiver` | 订单运费超标消息接收人配置表 | 8 | 1 | Id | 未明显识别 |
| `oms` | `oms_goods_detail` | 订单商品明细表 | 25 | 4 | Id | OrderId(订单ID), BatchId(批次ID), GoodsId(商品ID) |
| `oms` | `oms_hlj_push` | 活力佳推送信息表 | 14 | 3 | Id | 未明显识别 |
| `oms` | `oms_order` | 订单表 | 45 | 1 | Id | Code(订单编号), CustomerId(客户ID), OuterOrderCode(外部系统订单号) |
| `oms` | `oms_printer_limit_flow` |  | 9 | 3 | Id | OrderId(订单id), CustomerId(客户id) |
| `oms` | `oms_push_record` | 聚水潭推送信息表 | 26 | 2 | Id | BatchId(导入批次号) |
| `oms` | `oms_revise` | 订单修订工单表 | 43 | 2 | Id | OrderId(订单ID), OrderCode(订单编号), CustomerId(客户ID) |
| `oms` | `oms_revise_before` | 订单修订前工单表 | 24 | 1 | Id | OrderId(订单ID), OrderCode(订单编号), CustomerId(客户ID), OrderReviseId(修正订单ID) |
| `oms` | `oms_revise_picurls` | 订单修订图片urls | 8 | 2 | Id | 未明显识别 |
| `oms` | `oms_shop` | 店铺基础信息表 | 33 | 2 | Id | ThirdCustomerId(第三方运单号使用默认客户) |
| `oms` | `oms_shop_extend` | 店铺基础信息表 | 17 | 1 | Id | 未明显识别 |
| `oms` | `oms_shop_template` | 订单发送提示信息表 | 9 | 1 | Id | 未明显识别 |
| `oms` | `oms_third_party_mapping` |  | 8 | 1 | Id | OrderId(订单Id), JuShuiTanOrderId(聚水潭订单) |
| `oms` | `oms_work_flow` | 订单erp流水表 | 9 | 2 | Id | OrderCode(订单编号) |
| `oms` | `order_area_diff` | 第三方与丝路省市区映射表 | 17 | 2 | Id | 未明显识别 |

## 4. 订单相关接口检查

### 4.1 模块分布 Top 40

| 模块 | 接口数 |
|---|---:|
| 电商中台/订单-物流跟单 | 36 |
| 订单中心/促销-政策配置 | 29 |
| 电商中台/订单-查询 | 27 |
| 电商中台/订单-制单 | 22 |
| 订单中心/订单外部接口 | 20 |
| 订单中心/订单详情 | 18 |
| 订单中心/分销商订单 | 14 |
| 订单中心/订单审核 | 13 |
| 电商中台/订单-商品-物流 | 12 |
| 订单中心/订单 | 12 |
| 电商中台/订单-审核 | 11 |
| <订单客户查询> | 10 |
| 订单中心 | 10 |
| 订单中心/审单配置 必审规则 | 9 |
| 客户服务/<客户服务> | 8 |
| 电商中台/订单-财务审核 | 8 |
| 商品/商品-部门下单控制 | 7 |
| 订单中心/聚水潭系统 | 7 |
| 电商中台/订单包邮 | 7 |
| 订单中心/外部平台订单 | 7 |
| 订单中心/审单配置 自取审单/经理补贴 | 7 |
| 电商中台/订单-修订工单 | 7 |
| 促销政策/随货资料配置 | 7 |
| 促销政策/政策使用校验. | 7 |
| 电商中台/商品-产品下单控制 | 6 |
| 商品/下单商品控制管理 | 6 |
| 商品/商品-产品下单控制 | 6 |
| 订单中心/订单校验 | 6 |
| 订单中心/促销-返券规则 | 6 |
| 订单中心/测试接口 | 5 |
| 主数据/基础档案-禁止发货地区 | 5 |
| 资源相关操作 Controller | 5 |
| 订单中心/订单-物流撤单 | 5 |
| 订单中心/OrderPrinterFeeConfigController | 5 |
| 订单中心/订单商品统计配置 | 5 |
| 订单中心/订单配置/可消费额度配置 | 4 |
| 订单中心/促销-礼券流水 | 4 |
| (空) | 4 |
| 订单中心/物流-同步路由 | 4 |
| 订单中心/外部订单地址差异映射. | 4 |

### 4.2 缺失字段统计

| 缺失项 | 命中接口数 | 说明 |
|---|---:|---|
| `description` | 458 | 接口描述为空或未填写 |
| `request_body` | 190 | 请求体未声明，GET 接口可能正常，POST/PUT/PATCH 需重点确认 |
| `headers` | 175 | 请求头未声明 |

### 4.3 接口路径与鉴权检查

- 核心订单接口中，路径疑似包含本地地址或完整 URL 的接口：10 条。
- 核心订单接口中，存在 `Authorization` 或 `CurrentUser` 请求头但 `auth_type` 未结构化声明的接口：199 条。
- 报告中已对请求头示例值做脱敏，不展示 Authorization、CurrentUser 等可能敏感内容。

### 4.4 核心订单接口详细清单

> 说明：以下接口来自本地知识库 `apifox_project_776242.json`。请求头示例、Authorization、CurrentUser 等内容已脱敏；请求体和返回体以结构摘要方式展示，避免报告过大。

#### 1. 订单解密

- 所属模块：未声明
- 请求方式：`POST`
- 请求路径：`/datascraping/pdd/order/decrypt`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ClientId(string, 必填); Tid(string, 必填); Address(string, 必填); Name(string, 必填); Phone(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 2. test

- 所属模块：未声明
- 请求方式：`GET`
- 请求路径：`/order`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 3. 获取某个时间端的消费金额（获客大会员）

- 所属模块：未声明
- 请求方式：`POST`
- 请求路径：`/order/pay/money`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[StartOrderTime(string, 必填, 开始时间); EndOrderTime(string, 必填, 结束时间); CustomerId(integer, 必填, 客户Id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(integer, 必填, 金额单位（元）)]

#### 4. 根据主键id查询物流信息

- 所属模块：未声明
- 请求方式：`GET`
- 请求路径：`/touchpoint/photoletters//get/route`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=False，type=integer，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 5. 保存客户采集资料

- 所属模块：<订单客户查询>
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/data/collect/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/CusDataCollectionVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABBoolean%C2%BB

#### 6. 根据编号查询客户采集资料

- 所属模块：<订单客户查询>
- 请求方式：`GET`
- 请求路径：`/customerservice/customer/data/collect/select/{customerId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `customerId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABBoolean%C2%BB

#### 7. messageScreen

- 所属模块：<订单客户查询>
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/message/screen`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `isDeleted`：required=False，type=string，说明：无，示例：`0`
- `userId`：required=False，type=string，说明：无，示例：`0`
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无，示例：`0`
- `loginId`：required=False，type=string，说明：无，示例：`0`
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无，示例：`0`
- `businessType`：required=False，type=string，说明：无，示例：`0`
- `orgTypeId`：required=False，type=string，说明：无，示例：`0`
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无，示例：`0`
- `pageIndex`：required=False，type=string，说明：无，示例：`0`
- `pageSize`：required=False，type=string，说明：无，示例：`0`

**请求体**

- `application/json`：type=array; items=(type=string)

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 8. 判断可以拨打客户电话（判断是否购物部门下的孵化部门） true:省多多购物部门 false: 物部门下的孵化部门

- 所属模块：<订单客户查询>
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/shop/can/call`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/BaseVo

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 9. 导出提报信息

- 所属模块：<订单客户查询>
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/submission/import`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/CusGoodsSubmissionReqVO

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 10. 保存客户商品提报信息

- 所属模块：<订单客户查询>
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/submission/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/CusGoodsSubmissionSaveVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABBoolean%C2%BB

#### 11. 动态查询客户商品提报信息

- 所属模块：<订单客户查询>
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/submission/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/CusGoodsSubmissionReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABCusGoodsSubmissionRespVO%C2%BB

#### 12. test

- 所属模块：<订单客户查询>
- 请求方式：`GET`
- 请求路径：`/customerservice/customer/test/{count}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `count`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 13. 导出员工层级信息

- 所属模块：<订单客户查询>
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/userStaffLevel/export`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/UserQueryDTO

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 14. 导入

- 所属模块：<订单客户查询>
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/userStaffLevel/importExcel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[file(string, 必填)]

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 15. 客户在分配到池子之前的最近一笔订单记录-sop调用

- 所属模块：sop
- 请求方式：`POST`
- 请求路径：`/SOP/SOPExtend/CustomerOrderDistributeDefore`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Authorization`：required=True，type=string，说明：无
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填); OrderId(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 16. 2.2、订单系统--客户订单查询（媒体投放进线转人工时调用）

- 所属模块：丝路系统/IVR--进线接口管理
- 请求方式：`GET`
- 请求路径：`/CustomerAssets/InboundFlow/GetOrder`
- 接口说明：![image.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABkIAAAEjCAYAAABuPh3gAAAgAElEQVR4Ae3dX4ska14v+nwd3vab2Hgn7M2GjRfHwrrxXC6YfSHKPkfUxjNCWafskdGlDe1fxBlrjlWjC7QZNq2CrJmFF1UXYivYSwWPjJuevQvaNUfHGfDyOfwi44l8IjIyKzM6I...
- 鉴权方式：Authorization 请求头；OpenAPI security=bearer
- 缺失字段：request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `session.sce.CallId`：required=True，type=string，说明：进线唯一标识，示例：`session.sce.CallId=1575539293-664986`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 17. 2.2、获取客户未结案订单详情接口（媒体投放进线转人工时调用）(JAVA)

- 所属模块：丝路系统/IVR--进线接口管理
- 请求方式：`GET`
- 请求路径：`/callrecords/get/order`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `session.sce.CallId`：required=True，type=string，说明：进线唯一标识，示例：`session.sce.CallId=1575539293-664986`
- `session.sce.Dnis`：required=True，type=string，说明：落地号
- `session.sce.CustomerId`：required=True，type=string，说明：客户Id
- `session.sce.Ani`：required=False，type=string，说明：被叫号

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 18. 审单通过 通过phoneid添加客户微信

- 所属模块：丝路系统/rpa机器人加粉
- 请求方式：`POST`
- 请求路径：`/CustomerAssets/RpaCustomer/AddCustomerRpaWechat/{phoneId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- `phoneId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 19. 员工自取 - 3 - 员工自取客资数据（动作）

- 所属模块：丝路系统/客户数据分配和自取
- 请求方式：`GET`
- 请求路径：`/CustomerAssets/UserSelftake/SelfTake/{poolId}`
- 接口说明：1) 点击“自取数据”按钮时在选择“可用自取数据范围”内按如下顺序规则随机取一个客户，更新所属人为自取员工； a) 客户级别从高到低 b) 客资类型从高到低 c) 客户订单时间倒序 d) 客户接通通话时间<u>点</u>倒序 2) 并插入流转历史表一条流水记录，同时跳转到取得客户的客户详情页，执行拨打动作，拨打动作详见《客户详情页（会员、新训用）》描述；3) 如果自取失败弹屏给出消息告之自取人自取失败请重试；
- 鉴权方式：Authorization 请求头；OpenAPI security=bearer
- 缺失字段：request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CreateSource`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `poolId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 状态码，1000表示成功); Msg(string, 非必填); Data(boolean, 非必填, 结果，true or false)]

#### 20. transferOrder

- 所属模块：丝路系统/客户标记
- 请求方式：`POST`
- 请求路径：`/customerservice/customer/transfer/order/button/display`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/CustomerCallButtonDisplayVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 21. 合并客户(分销商）

- 所属模块：丝路系统/客户标记
- 请求方式：`POST`
- 请求路径：`/distribution/order/merge/customer`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OldCustomerId(integer, 必填, 老的客户Id); NewCustomerId(integer, 必填, 新的客户Id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 22. 下单创建客户

- 所属模块：丝路系统/客资系统-客户信息
- 请求方式：`POST`
- 请求路径：`/CustomerAssets/Customer/CreateCustomerByPhoneForOrder`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerName(string, 必填, 客户名称); PhoneNum(string, 必填, 电话号码); Gender(number, 非必填, 性别); AddressDetail(string, 必填, 地址); IsToNewPool(boolean, 非必填, 无所属人是否判断在XXX池 否然后抽离到新池  不传默认判断); PoolId(integer, 必填, 要进入的池子id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填, 编号); Msg(string, 非必填, 返回描述); Data(object, 非必填, 客户id)]

#### 23. 获取电话号码列表（for下单）

- 所属模块：丝路系统/客资系统-客户信息
- 请求方式：`GET`
- 请求路径：`/CustomerAssets/Customer/GetPhoneListForOrder`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无
- `CurrentUser`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户Id

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 24. 规则-根据订单信息匹配规则

- 所属模块：丝路系统/客资系统-客户消费限制
- 请求方式：`POST`
- 请求路径：`/CustomerAssets/CustomerSaleLimitRule/GetLimitRule`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填); OrgId(integer, 必填, 下单人部门); OrderType(integer, 必填, 订单类型); PayMethod(integer, 必填, 付款方式)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 25. 规则-根据订单信息判断是否可以下单

- 所属模块：丝路系统/客资系统-客户消费限制
- 请求方式：`POST`
- 请求路径：`/CustomerAssets/CustomerSaleLimitRule/IsCanOrder`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[RuleId(integer, 必填); CustomerId(integer, 必填); OrderAmount(number, 必填, 当前订单金额 现金金额+预付金额); OrderAmount1(number, 必填, 当前订单金额 现金金额+消费预付金额); IsFirstOrder(boolean, 非必填, 是否是首单); MonthOrderAmount(number, 非必填, 月度消费金额); HalfYearOrderAmount(number, 非必填, 半年消费金额); YearOrderAmount(number, 非必填, 年度消费金额); PrefundAmount(number, 非必填, 预付款余额)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 26. 当日订单审单情况--管理层

- 所属模块：丝路系统/客资系统-管理驾驶舱-客服看板
- 请求方式：`GET`
- 请求路径：`/CustomerAssets/CusMangeWork/OrderExamineStatistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `date`：required=True，type=string，说明：统计的日期，示例：`2019-01-01`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 27. 审单管理（获取当月）--员工用

- 所属模块：丝路系统/客资系统-管理驾驶舱-客服看板
- 请求方式：`GET`
- 请求路径：`/CustomerAssets/CusPersonalWork/GetMonthOrderAuditStatistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, request_body

**请求头**

- `CreateSource`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `date`：required=True，type=string，说明：日期  某个月

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 28. 审单管理（获取当天）--员工用

- 所属模块：丝路系统/客资系统-管理驾驶舱-客服看板
- 请求方式：`GET`
- 请求路径：`/CustomerAssets/CusPersonalWork/GetOrderAuditStatistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, request_body

**请求头**

- `CreateSource`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `date`：required=True，type=string，说明：日期

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 29. OA流程-企业微信客户下单

- 所属模块：丝路系统/泛微对接
- 请求方式：`POST`
- 请求路径：`/weaver/media/task/wechat`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[UserAccount(string, 必填, 坐席工号); CustomerCode(string, 必填, 客户编号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(boolean, 非必填)]

#### 30. 根据订单ID获取投放类型

- 所属模块：丝路系统/联络系统-Confluence需要接口补充
- 请求方式：`GET`
- 请求路径：`/Contact/InvolveContact/GetMediaPlacementTypeByOrderID`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderID`：required=True，type=string，说明：订单ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 状态码，1000表示成功); msg(string, 必填, 提示信息); Data(integer, 必填, 8.引流线 9.产品线 10.品销结合)]

#### 31. 新增禁止发货区域

- 所属模块：主数据/基础档案-禁止发货地区
- 请求方式：`POST`
- 请求路径：`/BaseInfo/BanExpressDistrict/Add`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ProvinceId(integer, 非必填, 省); CityId(integer, 非必填, 市); DistrictId(integer, 非必填, 区); StreetId(integer, 非必填, 街道); Reason(string, 非必填, 原因); OrgIds(string, 非必填, 部门 可多选 用|间隔 例如 |1|)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 32. 删除禁止发货区域

- 所属模块：主数据/基础档案-禁止发货地区
- 请求方式：`POST`
- 请求路径：`/BaseInfo/BanExpressDistrict/Delete/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- `id`：required=True，type=string，说明：主键

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 33. 分页列表

- 所属模块：主数据/基础档案-禁止发货地区
- 请求方式：`POST`
- 请求路径：`/BaseInfo/BanExpressDistrict/GetBanDistrictPageList`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ProvinceId(integer, 非必填, 省); CityId(integer, 非必填, 市); DistrictId(integer, 非必填, 区); StreetId(integer, 非必填, 街道); OrgId(integer, 非必填); PageIndex(number, 必填, 页码); PageSize(number, 必填, 每页大小); GetTotalCount(boolean, 必填, 是否获取总数)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 34. 判断区域是否是禁止发货区域

- 所属模块：主数据/基础档案-禁止发货地区
- 请求方式：`GET`
- 请求路径：`/BaseInfo/BanExpressDistrict/IsBanExpress`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `provinceId`：required=True，type=string，说明：省id  不传默认为0
- `cityId`：required=False，type=string，说明：市id
- `districtId`：required=False，type=string，说明：区id
- `streetId`：required=False，type=string，说明：街道id
- `orgId`：required=False，type=integer，说明：部门id  不传则不判断部门

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 35. 修改禁止发货区域

- 所属模块：主数据/基础档案-禁止发货地区
- 请求方式：`POST`
- 请求路径：`/BaseInfo/BanExpressDistrict/Update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ProvinceId(integer, 非必填, 省); Reason(string, 非必填, 原因); CityId(integer, 非必填, 市); DistrictId(integer, 非必填, 区); StreetId(integer, 非必填, 街道); Id(integer, 必填, 主键); OrgIds(string, 非必填, 部门  可多选 用|间隔 例如 |1|)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 36. 根据用户姓名/工号模糊查询(匹配订单权限

- 所属模块：主数据/权限 - 用户管理
- 请求方式：`GET`
- 请求路径：`/Privilege/User/FuzzyQueryForOrder`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `nameOrAccount`：required=True，type=string，说明：姓名或工号，示例：`张`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回状态码); Msg(string, 必填, 返回值); Data(array, 必填, 返回结果集)]

#### 37. 根据用户Id查询用户的订单权限

- 所属模块：主数据/权限 - 用户管理
- 请求方式：`GET`
- 请求路径：`/Privilege/User/GetOrderPrivilege`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：token

**Path 参数**

- 无/未声明

**Query 参数**

- `userId`：required=True，type=string，说明：用户Id，示例：`2`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 38. 获取某个订单最新使用的券的过期信息

- 所属模块：主数据/权限-用户资产
- 请求方式：`GET`
- 请求路径：`/Privilege/ProductCouponLogs/GetDeductLogsByOrderId`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=False，type=integer，说明：订单号
- `userId`：required=False，type=integer，说明：制单人id

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 状态码，1000表示成功); Msg(string, 必填, 提示信息); Data(array, 必填, 执行结果)]

#### 39. 空瓶回收下单最多比例

- 所属模块：促销政策/PolicyCouponApplyController
- 请求方式：`GET`
- 请求路径：`/policy/coupon/apply/goods/proportion`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABList%C2%ABGoodsProportionRespVO%C2%BB%C2%BB

#### 40. 查询订单可下预付赠品

- 所属模块：促销政策/其他政策配置 - 每满赠+多买多送
- 请求方式：`POST`
- 请求路径：`/policy/validate/gift/and/more`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PageIndex(integer, 必填, 分页); PageSize(integer, 必填, 分页); OrderPrefund(integer, 必填, 预付); CashMoneyChargeAmount(integer, 必填, 现金+预付); CashMoneyUseBalance(integer, 必填, 现金+消费); ConfigType(string, 必填, 类型 0：每满赠品 1：多买多少赠品); CustomerId(string, 必填, 客户Id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 41. 查询订单可下预付赠品

- 所属模块：促销政策/其他政策配置 - 预付赠品
- 请求方式：`POST`
- 请求路径：`/policy/validate/prefund`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderPrefund(integer, 必填); MinSharePrice(integer, 非必填); MaxSharePrice(integer, 非必填); CodeName(string, 非必填); PageIndex(integer, 必填); PageSize(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 42. 校验订单额外加送商品是否满足下单条件

- 所属模块：促销政策/其他政策配置- 预付额外送赠品
- 请求方式：`POST`
- 请求路径：`/validate/extra/order`
- 接口说明：接口返回 成功 ，允许提交订单或允许加入购物车
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Authorization`：required=True，type=string，说明：无
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填, 客户id); OrderPrefund(integer, 必填, 订单预付金额); OrderMoney(integer, 非必填, 订单实收); PayMoney(integer, 非必填, 客户实付); EnjoyUpgradeGift(integer, 非必填); EnjoyFullGift(integer, 非必填); ExpectBuyExtraGifts(array, 必填, 期望购买的额外加送商品)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 43. 查询符合订单预付额外送赠品

- 所属模块：促销政策/其他政策配置- 预付额外送赠品
- 请求方式：`POST`
- 请求路径：`/validate/extra/step`
- 接口说明：查询符合订单的额外加送
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderPrefund(integer, 非必填, 订单预付金额 单位分); OrderMoney(integer, 非必填, 订单实收金额单位分); CustomerPayMoney(integer, 非必填, 客户实付金额单位分); CodeName(string, 非必填, 商品名称 / 商品编码); EnjoyFullGift(integer, 非必填); EnjoyUpgradeGift(integer, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 44. 查询符合订单的免费领

- 所属模块：促销政策/政策使用校验.
- 请求方式：`POST`
- 请求路径：`/policy/validate/free`
- 接口说明：查询符合订单的免费领
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[customerLevelId(integer, 必填, 客户等级ID); codeName(string, 非必填, 商品名称 / 商品编码); workAges(integer, 非必填, 坐席入职工龄 单位;月份); inGroupWorkAges(integer, 非必填, 座席入组工龄 单位 月); customerGradeId(integer, 必填, 当前客户等级id); isDeleted(integer, 非必填); userId(integer, 非必填); userName(string, 非必填); orgId(integer, 非必填); loginId(integer, 非必填); loginUserName(string, 非必填); loginOrgId(integer, 非必填); userAccount(string, 非必填); createSource(string, 非必填); createTime(string, 非必填); updateSource(string, 非必填); ...其余 4 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 45. 查询符合订单的满额赠品

- 所属模块：促销政策/政策使用校验.
- 请求方式：`POST`
- 请求路径：`/policy/validate/full`
- 接口说明：查询符合订单的满额赠品
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[grade(integer, 非必填, 满额赠品档次额度); orderMoney(integer, 非必填, 订单实际可参与满额赠品的订单应收金额 单位：分); codeName(string, 非必填, 商品名称 / 商品编码); workAges(integer, 非必填, 坐席入职工龄 单位;月份); inGroupWorkAges(integer, 非必填, 座席入组工龄 单位 月); customerGradeId(integer, 必填, 当前客户等级id); isDeleted(integer, 非必填); userId(integer, 非必填); userName(string, 非必填); orgId(integer, 非必填); loginId(integer, 非必填); loginUserName(string, 非必填); loginOrgId(integer, 非必填); userAccount(string, 非必填); createSource(string, 非必填); createTime(string, 非必填); ...其余 5 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 46. 查询符合订单的升级赠品

- 所属模块：促销政策/政策使用校验.
- 请求方式：`POST`
- 请求路径：`/policy/validate/upgrade`
- 接口说明：查询符合订单的升级赠品
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[upgradeTypeId(integer, 必填, 下单后客户升级ID); codeName(string, 非必填, 商品名称 / 商品编码); workAges(integer, 非必填, 坐席入职工龄 单位;月份); inGroupWorkAges(integer, 非必填, 座席入组工龄 单位 月); customerGradeId(integer, 必填, 当前客户等级id); isDeleted(integer, 非必填); userId(integer, 非必填); userName(string, 非必填); orgId(integer, 非必填); loginId(integer, 非必填); loginUserName(string, 非必填); loginOrgId(integer, 非必填); userAccount(string, 非必填); createSource(string, 非必填); createTime(string, 非必填); updateSource(string, 非必填); ...其余 4 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 47. 查询符合订单的额外加送

- 所属模块：促销政策/政策使用校验.
- 请求方式：`POST`
- 请求路径：`/validate/extra`
- 接口说明：查询符合订单的额外加送
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderMoney(integer, 必填, 订单金额 单位分); OrderPrefund(integer, 必填, 订单预付金额 单位分); EnjoyUpgradeGift(integer, 非必填, 是否同时享受升级赠品 0:否 1:是); EnjoyStepGift(integer, 必填, 是否同时享受阶梯兑换0:否 1:是); EnjoyPrefundGift(integer, 必填, 是否同时享受多买多送：是/否); EnjoyFullGift(integer, 非必填, 是否同时享受满额赠品0:否 1:是); ReceiptMethod(integer, 非必填, 收款方式 字典id); CodeName(string, 非必填, 商品名称 / 商品编码); WorkAges(integer, 非必填, 坐席入职工龄 单位;月份); InGroupWorkAges(integer, 非必填, 座席入组工龄 单位 月); CustomerGradeId(integer, 必填, 当前客户等级id); PageIndex(integer, 非必填); PageSize(integer, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 48. 查询符合订单的积分换购

- 所属模块：促销政策/政策使用校验.
- 请求方式：`POST`
- 请求路径：`/validate/integral`
- 接口说明：查询符合订单的积分换购
- 鉴权方式：CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Integral(integer, 必填, 客户当前可用积分); IntegralStart(integer, 非必填, 积分左区间); IntegralEnd(integer, 非必填, 积分右区间或者积分档次); CodeName(string, 非必填, 商品名称 / 商品编码); WorkAges(integer, 非必填, 坐席入职工龄 单位;月份); InGroupWorkAges(integer, 非必填, 座席入组工龄 单位 月); CustomerGradeId(integer, 必填, 当前客户等级id); Type(string, 非必填, 积分赠品：1，默认为积分换购)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 49. 查询符合订单的积分档次

- 所属模块：促销政策/政策使用校验.
- 请求方式：`POST`
- 请求路径：`/validate/integral/grades`
- 接口说明：查询符合订单的积分换购
- 鉴权方式：CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Iintegral(integer, 必填, 客户当前可用积分); CodeName(string, 非必填, 商品名称 / 商品编码); WorkAges(integer, 非必填, 坐席入职工龄 单位;月份); InGroupWorkAges(integer, 非必填, 座席入组工龄 单位 月); CustomerGradeId(integer, 必填, 当前客户等级id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(array, 非必填, 可选档次列表)]

#### 50. 积分赠品下单前校验

- 所属模块：促销政策/政策使用校验.
- 请求方式：`POST`
- 请求路径：`/validate/integral/num`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填); Gifts(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(null, 必填)]

#### 51. 返券 - 计算当前订单可选的最大满额赠品档次以及可选的满额赠品档次列表以及未选赠品的剩余档次可折算的满额返券

- 所属模块：促销政策/政策计算.
- 请求方式：`POST`
- 请求路径：`/calculate/rebate/full`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PayAmountForFullGift(number, 必填); CancelRate(integer, 非必填); CalBigOrderReward(string, 非必填); CancelBigOrder(string, 非必填); EnjoyStatus(string, 非必填); ConsumeFullGradeLevel(string, 必填); WorkAges(string, 必填); DepartmentId(string, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 52. 返券 - 计算可兑换升级赠品信息以及未兑换升级赠品可折算的升级返券

- 所属模块：促销政策/政策计算.
- 请求方式：`POST`
- 请求路径：`/policy/calculate/rebate/upgrade`
- 接口说明：返券 - 计算可兑换升级赠品信息以及未兑换升级赠品可折算的升级返券  前提条件：  根据订单可享受升级赠品的应收金额 计算 可兑换升级赠品的升级信息  根据升级返券规则配置，根据 可兑换升级赠品的升级信息 在规则里计算对应的 未兑换升级赠品可折算的升级返券  <p>  计算规则：
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[payAmountForUpgradeGift(number, 必填, 可参与升级赠品计算的应收金额 单位分); beforeCustomerGradeId(integer, 必填, 下单前客户等级); customerId(integer, 必填, 客户id); isDeleted(integer, 非必填); userId(integer, 非必填); userName(string, 非必填); orgId(integer, 非必填); loginId(integer, 非必填); loginUserName(string, 非必填); loginOrgId(integer, 非必填); userAccount(string, 非必填); createSource(string, 非必填); createTime(string, 非必填); updateSource(string, 非必填); updateTime(string, 非必填); total(integer, 非必填); ...其余 2 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 53. 查询客户订单可以使用的礼券

- 所属模块：促销政策/礼券配置
- 请求方式：`POST`
- 请求路径：`/policy/coupon/customer/order`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 非必填, 订单ID); OrderMoney(integer, 非必填); DepartmentId(integer, 必填); CustomerId(integer, 必填); EmployeeId(integer, 必填, 坐席id); GoodsList(array, 非必填); AfterGradeId(integer, 必填, 下单后客户级别)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 54. 新增随货资料配置

- 所属模块：促销政策/随货资料配置
- 请求方式：`POST`
- 请求路径：`/orderwithgoods/create`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Authorization`：required=False，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DeliveryGoods(array, 必填, 随货资料商品集合); StartTime(string, 必填, 有效期开始时间); EndTime(string, 必填, 有效期结束时间); DepartmentIds(array, 必填, 下单部门id集合); BelongDepartmentIds(array, 必填, 下单客户所属人部门id集合); GradeIds(array, 非必填, 客户等级id集合); PlacementTypeLists(array, 非必填, 客户投放类型); OrderContainGoods(array, 非必填, 订单包含商品集合); OrderMutexGoods(array, 非必填); IsOnlyOneInValidTime(integer, 必填, 有效期内每个客户仅限1份（0：否，1：是）); Remark(string, 非必填, 备注); IsDeliveryWhenOrderContainsAgentGoods(string, 非必填, 订单包含代售商品是否发放随货资料)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 55. 批量延期

- 所属模块：促销政策/随货资料配置
- 请求方式：`POST`
- 请求路径：`/orderwithgoods/delay`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Ids(array, 必填); EndTime(string, 必填, 结束时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 56. 随货资料 - 分页查询

- 所属模块：促销政策/随货资料配置
- 请求方式：`GET`
- 请求路径：`/orderwithgoods/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description, request_body

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PageIndex`：required=True，type=integer，说明：无
- `PageSize`：required=True，type=integer，说明：无
- `Status`：required=False，type=integer，说明：状态
- `StartTime`：required=False，type=string，说明：有效期开始时间
- `EndTime`：required=False，type=string，说明：有效期结束时间
- `OrgIds`：required=False，type=array，说明：部门id数组

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 57. 获取订单可匹配到的随货资料配置

- 所属模块：促销政策/随货资料配置
- 请求方式：`POST`
- 请求路径：`/orderwithgoods/list/order`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderSource(integer, 必填); BeforeGradeId(integer, 必填); OrderSkuCodes(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 58. 批量状态变更

- 所属模块：促销政策/随货资料配置
- 请求方式：`POST`
- 请求路径：`/orderwithgoods/status`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Ids(array, 必填); Status(integer, 必填, 变更状态)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 59. 状态变更

- 所属模块：促销政策/随货资料配置
- 请求方式：`POST`
- 请求路径：`/orderwithgoods/status/{id}/{status}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description, request_body

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `id`：required=True，type=integer，说明：随货资料配置id，示例：`0`
- `status`：required=True，type=integer，说明：状态（0：停用，1：启用）

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 60. 修改随货资料配置

- 所属模块：促销政策/随货资料配置
- 请求方式：`POST`
- 请求路径：`/orderwithgoods/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Authorization`：required=False，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DeliveryGoods(array, 必填, 随货资料商品集合); StartTime(string, 必填, 有效期开始时间); EndTime(string, 必填, 有效期结束时间); DepartmentIds(array, 必填, 下单部门id集合); BelongDepartmentIds(array, 必填, 下单客户所属人部门id集合); GradeIds(array, 非必填, 客户等级id集合); PlacementTypeLists(array, 非必填, 客户投放类型); OrderContainGoods(array, 非必填, 订单包含商品集合); IsOnlyOneInValidTime(integer, 必填, 有效期内每个客户仅限1份（0：否，1：是）); Remark(string, 非必填, 备注); Id(integer, 必填, 主键); OrderMutexGoods(array, 非必填); IsDeliveryWhenOrderContainsAgentGoods(string, 非必填); CustomerTagIds(array, 非必填, 客户标签数组)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 61. 审核人员查询短信列表（分页）

- 所属模块：公共服务/短信服务
- 请求方式：`POST`
- 请求路径：`/SmsService/Sms/GetAuditSmsSendList`
- 接口说明：由于短信和用户不在一个库，审单人员名字、发送坐席名字需要另外调用接口获取
- 鉴权方式：Authorization 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=False，type=string，说明：Authorization (Only:7E723BC8DF774C388475CCD999BB421C)

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerCode(string, 非必填, 客户编号); UserId(number, 非必填, 用户Id); AuditTimeBegin(number, 非必填, 开始时间); AuditTimeEnd(number, 非必填, 结束时间); AuditStatus(number, 非必填, 审核状态（0-待审核，1-审核通过，2-审核不通过）); PageIndex(number, 非必填, 页码); PageSize(number, 非必填, 每页条数)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 62. 订单查询接口

- 所属模块：分账系统
- 请求方式：`POST`
- 请求路径：`/split/separate/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填, 订单编码); CustomerCode(string, 必填, 客户编码); OrderStatus(integer, 必填, 订单状态1,2,3,4,5,6); MediaIds(array, 必填, 媒体id默认5061); FoursIds(array, 必填, 四百id默认532,1698,1704,588,536); OrderStartTime(string, 必填, 下单开始时间); OrderEndTime(string, 必填, 下单结束时间); PageIndex(integer, 必填); PageSize(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 63. 订单查询导出接口

- 所属模块：分账系统
- 请求方式：`GET`
- 请求路径：`/split/separate/list/export`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=array; items=(type=object; fields=[])

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 64. 撤单

- 所属模块：售后
- 请求方式：`POST`
- 请求路径：`/aftersale/cancelOrder`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[AfterSaleId(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(null, 必填)]

#### 65. 退款确认

- 所属模块：售后
- 请求方式：`POST`
- 请求路径：`/confirm`
- 接口说明：1. 客服闭环需求中的 下单人24h内确认以及超过24h以上自动确认功能
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 必填); Type(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 66. 修改在途数、供应周期、是否不在补货

- 所属模块：商品/GoodsController
- 请求方式：`POST`
- 请求路径：`/cx/goods/order/goods/status`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/GoodsOrderStatusVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsgVo

#### 67. 查询订货预警数据

- 所属模块：商品/GoodsController
- 请求方式：`POST`
- 请求路径：`/cx/goods/order/warn`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/GoodsOrderWarnReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsgVo%C2%ABCommonListRespVO%C2%BB

#### 68. 下载商品预警数据

- 所属模块：商品/GoodsController
- 请求方式：`GET`
- 请求路径：`/cx/goods/order/warn/download`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `isDeleted`：required=False，type=integer，说明：无
- `loginId`：required=False，type=integer，说明：无
- `loginName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=integer，说明：无
- `TenantId`：required=False，type=integer，说明：无
- `loginAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=integer，说明：无
- `pageIndex`：required=False，type=integer，说明：无
- `pageSize`：required=False，type=integer，说明：无
- `chargePeopleId`：required=False，type=integer，说明：产品负责人id
- `chargePeopleAccount`：required=False，type=string，说明：产品负责人工号
- `goodsId`：required=False，type=integer，说明：商品id

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 69. 订单校验返回符合条件的skuCode

- 所属模块：商品/GoodsCustomerGuidanceController
- 请求方式：`POST`
- 请求路径：`/cx/goods/customer/guidance/check/match/remind`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/CheckGoodsReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsgVo%C2%ABList%C2%ABSpuCodeRespVO%C2%BB%C2%BB

#### 70. 批量添加

- 所属模块：商品/下单商品控制管理
- 请求方式：`POST`
- 请求路径：`/commodity/goods/label/batch/add`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[labelId(integer, 必填, 客户标签id); typeStatus(integer, 必填, 配置类型：0：允许1：禁止); goodsLabelVOList(array, 必填, 商品)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填); msg(string, 必填); data(string, 必填)]

#### 71. 删除商品

- 所属模块：商品/下单商品控制管理
- 请求方式：`GET`
- 请求路径：`/commodity/goods/label/deleted`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=False，type=integer，说明：商品主键id

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填); msg(string, 必填); data(string, 必填)]

#### 72. 查询详情

- 所属模块：商品/下单商品控制管理
- 请求方式：`GET`
- 请求路径：`/commodity/goods/label/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=False，type=integer，说明：Id

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 73. 分页查询

- 所属模块：商品/下单商品控制管理
- 请求方式：`POST`
- 请求路径：`/commodity/goods/label/page`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[labelId(integer, 必填, 客户标签id); goodsName(string, 必填, 商品名称)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填); msg(string, 必填); data(object, 必填)]

#### 74. 读取Excel数据

- 所属模块：商品/下单商品控制管理
- 请求方式：`POST`
- 请求路径：`/commodity/goods/label/read/excel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `file`：required=False，type=string，说明：表地址

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 75. 添加修改标签

- 所属模块：商品/下单商品控制管理
- 请求方式：`POST`
- 请求路径：`/commodity/goods/label/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[id(integer, 必填, 要修改商品id); labelIds(array, 必填, 客户标签id); typeStatus(integer, 必填, 配置类型：0：允许1：禁止); goodsLabelVO(object, 必填, 商品)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填); msg(string, 必填); data(string, 必填)]

#### 76. 删除下单区域控制

- 所属模块：商品/商品-产品下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/order/area/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 下单区域控制ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息)]

#### 77. 下单区域控制详情

- 所属模块：商品/商品-产品下单控制
- 请求方式：`GET`
- 请求路径：`/commodity/order/area/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=True，type=string，说明：下单区域控制ID，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息); Data(object, 必填, 返回结果)]

#### 78. 保存下单区域控制

- 所属模块：商品/商品-产品下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/order/area/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[GoodsList(array, 必填, 商品列表); OrgList(array, 必填, 区域组织列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息)]

#### 79. 查询下单区域控制

- 所属模块：商品/商品-产品下单控制
- 请求方式：`GET`
- 请求路径：`/commodity/order/area/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=False，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PageIndex`：required=False，type=string，说明：页数 默认1，示例：`1`
- `PageSize`：required=False，type=string，说明：每页显示条数 默认10，示例：`10`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 80. 修改下单区域控制

- 所属模块：商品/商品-产品下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/order/area/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[GoodsList(array, 必填, 商品列表); OrgList(array, 必填, 区域组织列表); Id(number, 必填, 下单区域控制ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息)]

#### 81. 检查商品是否在下单区域内

- 所属模块：商品/商品-产品下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/select/checkGoodsIsArea`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[GoodsIds(array, 必填, 商品ID集合); ProvinceId(number, 非必填, 客户接收地址省ID); CityId(number, 非必填, 客户接收地址市ID); DistrictId(number, 非必填, 区id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 82. 删除部门下单控制

- 所属模块：商品/商品-部门下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/dept/order/control/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DeptOrderControlId(number, 必填, 部门下单控制ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 83. 查询部门下单控制部门

- 所属模块：商品/商品-部门下单控制
- 请求方式：`GET`
- 请求路径：`/commodity/dept/order/control/dept/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `DeptOrderControlId`：required=True，type=string，说明：部门下单控制ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示信息); Data(object, 非必填, 返回值)]

#### 84. 查询部门下单控制商品

- 所属模块：商品/商品-部门下单控制
- 请求方式：`GET`
- 请求路径：`/commodity/dept/order/control/goods/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `DeptOrderControlId`：required=True，type=string，说明：部门下单控制ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 85. 保存部门下单控制

- 所属模块：商品/商品-部门下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/dept/order/control/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[GoodsList(array, 必填, 商品列表); DepartmentList(array, 必填, 部门列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 86. 查询部门下单控制列表

- 所属模块：商品/商品-部门下单控制
- 请求方式：`GET`
- 请求路径：`/commodity/dept/order/control/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `GoodsId`：required=True，type=string，说明：商品ID
- `DepartmentId`：required=True，type=string，说明：部门ID
- `UserId`：required=True，type=string，说明：用户ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 87. 修改部门下单控制

- 所属模块：商品/商品-部门下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/dept/order/control/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[GoodsList(array, 必填, 商品列表); DepartmentList(array, 必填, 部门列表); Id(number, 必填, 部门下单控制ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 88. 查询部门下单控制用户

- 所属模块：商品/商品-部门下单控制
- 请求方式：`GET`
- 请求路径：`/commodity/dept/order/control/user/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `DeptOrderControlId`：required=True，type=string，说明：部门下单控制ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息); Data(object, 非必填, 返回值)]

#### 89. 下单中获取商品可展示的属性

- 所属模块：商品/新版商品管理
- 请求方式：`POST`
- 请求路径：`/commodity/order/getGoodsPrperty`
- 接口说明：<获取商品Sku信息> <功能详细描述>
- 鉴权方式：Authorization 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[GoodsId(integer, 必填, 商品ID); Type(number, 必填, 类型 1：spu商品；2：商品组；3:政策); PolicyId(number, 非必填, 政策ID（type=3时必传）); PolicyGroupId(number, 非必填, 政策配置ID（type=3时必传）); GroupID(number, 非必填, 商品组ID（type=2时必传）); PropertyValueIds(array, 非必填); IsOrder(string, 非必填, 查询来源  0：下单查询；1：其他；2： 下单页的返回换购 3：其他政策中配置范围内查询；4：员工自...)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 90. 保存客户待下单数据

- 所属模块：客户服务
- 请求方式：`POST`
- 请求路径：`/customerservice/pend/order/add`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(string, 必填, 客户id); UserId(string, 必填, 坐席Id); Type(integer, 必填, 1:机器人待下单)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 91. 获取专家连线次数

- 所属模块：客户服务
- 请求方式：`GET`
- 请求路径：`/orders/expert/count`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `CustomerId`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(integer, 必填)]

#### 92. 更新客户未完结工单来电次数

- 所属模块：客户服务
- 请求方式：`POST`
- 请求路径：`/orders/inbound`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Authorization`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(string, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 93. 初始redis预分配数据池

- 所属模块：客户服务/<客户服务>
- 请求方式：`POST`
- 请求路径：`/customerservice/orders/allocate/init`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=array; items=(type=string)

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 94. <自取下一条>

- 所属模块：客户服务/<客户服务>
- 请求方式：`POST`
- 请求路径：`/customerservice/orders/autoAddOrder`
- 接口说明：<坐席优先处理自己名下 处理中和 协办中 状态的工单+时间asc;没有则获取未领取状态的+时间asc>
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[id(integer, 非必填, 工单id); taskClassifyId(integer, 非必填, 工单分类id); taskTypeId(integer, 非必填, 工单类型id); taskClassifyIds(array, 非必填, 多个工单分类id); taskTypeIds(array, 非必填, 多个工单类型id); cusPhoneId(integer, 非必填, 回电号码id); status(integer, 非必填, 工单状态：1：未领取；2：处理中；3：协办中；4：协办完成待完结；5：已完结；6：作废); statuss(array, 非必填, 多个工单状态); gradeId(string, 非必填, 客户级别id); customerNo(string, 非必填, 客户编号); handlePerson(string, 非必填, 处理人); handlePersonId(integer, 非必填, 当前处理人id); createUser(string, 非必填, 创建人); isYuqi(integer, 非必填, 是否逾期（0：未逾期；1：已逾期）); isMe(integer, 非必填, 是否与我相关（0：否；1：是）); isOver2Hour(integer, 非必填, 是否超2小时未领取（0：否；1：是）); ...其余 64 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 95. 创建高端消费客户工单

- 所属模块：客户服务/<客户服务>
- 请求方式：`POST`
- 请求路径：`/customerservice/orders/highend`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(string, 必填, 客户id); Content(string, 必填, 工单内容)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 非必填)]

#### 96. 重新分配延期分配的工单数据

- 所属模块：客户服务/<客户服务>
- 请求方式：`POST`
- 请求路径：`/customerservice/orders/job/realllocate`
- 接口说明：todo 定时执行 每天9点执行一次
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 97. 初始redis消息提醒人数据池

- 所属模块：客户服务/<客户服务>
- 请求方式：`POST`
- 请求路径：`/customerservice/orders/notify/init`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=array; items=(type=string)

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 98. 获取售后服务评分详情 -> 根据退换货工单id

- 所属模块：客户服务/<客户服务>
- 请求方式：`GET`
- 请求路径：`/customerservice/orders/satisfaction`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `AfterSaleId`：required=True，type=string，说明：无，示例：`0`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 99. 创建售后回访服务工单

- 所属模块：客户服务/<客户服务>
- 请求方式：`POST`
- 请求路径：`/customerservice/orders/satisfaction`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[customerId(integer, 非必填, 客户id); customerCode(string, 非必填, 客户编号 （如果存在customerId,即可不填）); toUserId(integer, 非必填, 被评分处理人id); toUserAccount(string, 非必填, 被评分处理人丝路工号（如果存在被评分处理人id，即可不填丝路工号）); relationId(integer, 非必填, 关联id（退换货类为退换货工单id，投诉类为投诉档案id）); WorkOrderStatus(integer, 非必填, 投诉档案工单状态（0:完结 1:未完结）); relationType(integer, 必填, 关联类型(退换货类：0，投诉类：1))]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 100. 更新售后服务评分

- 所属模块：客户服务/<客户服务>
- 请求方式：`POST`
- 请求路径：`/customerservice/orders/satisfaction/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[id(integer, 必填, 评分id); serviceAttitudeScore(integer, 必填, 服务态度评分); serviceEfficiencyScore(integer, 必填, 服务效率评分); logisticsServiceScore(integer, 必填, 物流服务评分); remark(string, 非必填, 备注); updateSource(string, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 101. 微盟-订单详情

- 所属模块：微盟
- 请求方式：`POST`
- 请求路径：`/api/1_0/ec/order/queryOrderDetail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `accesstoken`：required=True，type=string，说明：无，示例：`e91cc081-7f24-4c2d-b58b-edd27f5b7161`

**请求体**

- `application/json`：type=object; fields=[orderNo(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[globalTicket(string, 必填); code(object, 必填); data(object, 必填)]

#### 102. 微盟-消息推送

- 所属模块：微盟
- 请求方式：`POST`
- 请求路径：`/order/weimob/receive`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 103. 媒体进线订单明细

- 所属模块：报表系统/媒体
- 请求方式：`GET`
- 请求路径：`/ReportSystem/ManageCockpit/GetMediaInboundOrderDetails`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `sDate`：required=True，type=string，说明：开始时间
- `eDate`：required=True，type=string，说明：结束时间
- `n400`：required=False，type=string，说明：400号

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 104. 坐席通话和出勤及下单汇总

- 所属模块：报表系统/首页看板
- 请求方式：`GET`
- 请求路径：`/ReportSystem/ManageCockpit/GetSeatsCallAndWorkInfo`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `sDate`：required=True，type=string，说明：开始时间
- `eDate`：required=True，type=string，说明：结束时间
- `orgId`：required=True，type=string，说明：部门id

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 105. 订单详情

- 所属模块：拼多多
- 请求方式：`POST`
- 请求路径：`/datascraping/pdd/order/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ClientId(string, 必填); Tid(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 106. 物流对接-查询杂志邮寄物流状态

- 所属模块：接触点/DM
- 请求方式：`GET`
- 请求路径：`/touchpoint/job/list/get/magazineMail/status`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `ExpressNoList`：required=True，type=string，说明：物流单号，示例：`9973282482394,9973282482393`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 107. 物流对接-修改杂志邮寄物流状态

- 所属模块：接触点/DM
- 请求方式：`POST`
- 请求路径：`/touchpoint/job/list/update/magazineMail/status`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[MagazineMailStatusList(array, 非必填, 杂志邮寄状态集合)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(null, 非必填, 响应数据)]

#### 108. 根据杂志物流单号返显 联系备注

- 所属模块：接触点/DM
- 请求方式：`GET`
- 请求路径：`/touchpoint/magazine/qryContactRemark/{expressNo}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `expressNo`：required=True，type=string，说明：运单号，示例：`9973282956596`

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 接口返回码值); Msg(string, 必填, 接口返回信息); Data(string, 必填, 联系备注信息)]

#### 109. 根据主键id和用户id获取物流单号信息

- 所属模块：接触点/照片信件
- 请求方式：`GET`
- 请求路径：`/touchpoint/photoletters/get/logisticsCode`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=False，type=string，说明：主键id
- `UserId`：required=False，type=string，说明：用户id

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 110. 根据物流号获取跟单备注

- 所属模块：接触点/照片信件
- 请求方式：`GET`
- 请求路径：`/touchpoint/photoletters/get/remark`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `ExpressNo`：required=False，type=string，说明：物流单号

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[data(string, 必填, 数据)]

#### 111. 根据主键获取物流信息

- 所属模块：接触点/照片信件
- 请求方式：`GET`
- 请求路径：`/touchpoint/photoletters/get/route`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=False，type=string，说明：主键

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 112. 根据订单号发送短信

- 所属模块：接触点/短信
- 请求方式：`POST`
- 请求路径：`/touchpoint/send/message/by/orderId`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(string, 必填, 订单Id); UserId(string, 必填, 坐席Id); TargetPhone(string, 必填, PhoneId); TemplateId(string, 必填, 短信模板Id); CustomerId(string, 必填, 客户Id); PhoneType(string, 必填, 手机类型，1、明文手机号，2、一次加密手机号；3、二次加密手机号 4、phoneId)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 113. 有赞订单 批量解密

- 所属模块：有赞 Controller
- 请求方式：`POST`
- 请求路径：`/datascraping/youzan/batch/decrypt`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/YouzanBatchDecryptReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 114. 有赞订单 佣金

- 所属模块：有赞 Controller
- 请求方式：`POST`
- 请求路径：`/datascraping/youzan/commission`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/YouzanCommissionReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 115. 有赞订单 发货

- 所属模块：有赞 Controller
- 请求方式：`POST`
- 请求路径：`/datascraping/youzan/delivery`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/YouzanDeliveryReqVo

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 116. 上门取件

- 所属模块：物流系统
- 请求方式：`POST`
- 请求路径：`/logistics/order/carrier/create/pick`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CarrierId(integer, 必填); OrderCode(string, 必填); ProvinceName(string, 必填); CityName(string, 必填); DistrictName(string, 必填); StreetName(null, 必填); DetailAddress(string, 必填); SenderProvinceName(string, 必填); SenderCityName(string, 必填); SenderDistrictName(string, 必填); SenderStreetName(null, 必填); SenderDetailAddress(string, 必填); Contact(string, 必填); ReceiverPhone(string, 必填); Phone(string, 必填); CargoDetails(array, 必填); ...其余 2 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(string, 必填)]

#### 117. 上门取件订单取消

- 所属模块：物流系统/上门取件
- 请求方式：`POST`
- 请求路径：`/logistics/pickup/cancel/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description, request_body

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 118. 新建上门取件

- 所属模块：物流系统/上门取件
- 请求方式：`POST`
- 请求路径：`/logistics/pickup/create`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填); CarrierId(integer, 必填); PayMethodId(integer, 必填); Sender(object, 必填); Receiver(object, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 119. 分页查询

- 所属模块：物流系统/上门取件
- 请求方式：`POST`
- 请求路径：`/logistics/pickup/page`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 非必填); StartTime(string, 非必填); EndTime(string, 非必填); PageIndex(string, 必填); PageSize(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 120. 导出物流商运费账单核算数据

- 所属模块：物流系统/物流商运费账单核对
- 请求方式：`POST`
- 请求路径：`/logistics/check/fee/exportExcel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ReceiveSendDateStart(string, 必填); ReceiveSendDateEnd(string, 必填); logisticsCode(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 121. 导入物流商运费账单

- 所属模块：物流系统/物流商运费账单核对
- 请求方式：`POST`
- 请求路径：`/logistics/check/fee/import`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[file(string, 非必填, 导入文件)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(string, 必填)]

#### 122. 物流商运费账单分页

- 所属模块：物流系统/物流商运费账单核对
- 请求方式：`POST`
- 请求路径：`/logistics/check/fee/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PageIndex(integer, 必填); PageSize(integer, 必填); ReceiveSendDateStart(string, 必填); ReceiveSendDateEnd(string, 必填); logisticsCode(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 123. 审单通过

- 所属模块：电商中台
- 请求方式：`POST`
- 请求路径：`/order/review/rule/pass/XJ0120260204007089`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填); IsCanModifyAddress(boolean, 必填); AgentDesc(null, 必填); ReviewDesc(null, 必填); NotPassReason(null, 必填); ActualFreeReview(null, 必填); PayFreight(integer, 必填); Type(string, 必填); IsHasSurvey(boolean, 必填); TenantId(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 124. 9.11 退换货订单签收（作废）

- 所属模块：电商中台/9_售后服务
- 请求方式：`POST`
- 请求路径：`/aftersale/orderSignReceived`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[AfterSaleId(string, 必填, 退换货工单ID); OrderId(string, 必填, 订单id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 状态码); Msg(string, 非必填, 返回消息); Data(boolean, 非必填)]

#### 125. 9.5选中订单

- 所属模块：电商中台/9_售后服务
- 请求方式：`POST`
- 请求路径：`/aftersale/unpack/chooseOrder`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `AfterSaleId`：required=True，type=string，说明：退换货工单ID

**请求体**

- `application/json`：type=object; fields=[AfterSaleId(number, 必填, 售后工单Id); OrderId(number, 必填, 选中的工单id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 126. 取消订单回收礼券

- 所属模块：电商中台/促销-礼券发放
- 请求方式：`POST`
- 请求路径：`/coupon/grant/order/cancel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); OrderId(number, 必填, 订单ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语)]

#### 127. 根据订单发放礼券

- 所属模块：电商中台/促销-礼券发放
- 请求方式：`POST`
- 请求路径：`/policy/coupon/grant/order`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); OrderStatus(number, 必填, 订单状态); CustomerLevelId(number, 必填, 客户等级ID); CustomerTypeId(number, 必填, 客户类型ID); EmployeeId(number, 必填, 下单人ID); DepartmentId(number, 必填, 下单部门ID); GoodsList(array, 必填, 商品列表); OrderId(number, 必填, 订单ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(array, 必填)]

#### 128. 查询公司收获地址

- 所属模块：电商中台/公共接口
- 请求方式：`GET`
- 请求路径：`/order/extend/company/address`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 129. 根据customerCode和skuList获取最近一次签收的订单、订单时间

- 所属模块：电商中台/公共接口
- 请求方式：`POST`
- 请求路径：`/order/get/order/by/sku/list`
- 接口说明：根据customerCode和skuList获取最近一次签收的订单、订单时间
- 鉴权方式：未声明/未识别
- 缺失字段：headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerCode(string, 必填, 客户编码); SkuList(array, 必填, Sku集合)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 130. 订单发送wms仓库

- 所属模块：电商中台/公共接口
- 请求方式：`POST`
- 请求路径：`/order/review/send/wms`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=array; items=(type=string)

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 131. 删除下单部门控制

- 所属模块：电商中台/商品-产品下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/dept/order/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 下单部门控制ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息)]

#### 132. 下单部门控制详情

- 所属模块：电商中台/商品-产品下单控制
- 请求方式：`GET`
- 请求路径：`/commodity/dept/order/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=True，type=string，说明：下单部门控制ID，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语); Data(object, 必填)]

#### 133. 保存下单部门控制

- 所属模块：电商中台/商品-产品下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/dept/order/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[BatchTime(string, 必填, 批次时间); DepartmentList(array, 必填, 下单部门); InitTaskUpNumber(number, 必填, 任务上限数); GoodsId(number, 必填, 商品ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填)]

#### 134. 查询下单部门控制

- 所属模块：电商中台/商品-产品下单控制
- 请求方式：`GET`
- 请求路径：`/commodity/dept/order/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PageIndex`：required=False，type=string，说明：页数  默认1，示例：`1`
- `PageSize`：required=False，type=string，说明：每页显示条数  默认10，示例：`10`
- `DepartmentId`：required=False，type=string，说明：部门ID，示例：`1`
- `GoodsName`：required=False，type=string，说明：商品名称
- `BatchTime`：required=False，type=string，说明：批次时间，示例：`2019-01`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语); Data(object, 必填, 返回值)]

#### 135. 给部门经理发送通知

- 所属模块：电商中台/商品-产品下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/dept/order/send/notice`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[List(array, 必填, 部门下单控制ID集合)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语)]

#### 136. 修改下单部门控制

- 所属模块：电商中台/商品-产品下单控制
- 请求方式：`POST`
- 请求路径：`/commodity/dept/order/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[BatchTime(string, 必填, 批次时间); Id(number, 必填, 部门下单ID); DepartmentId(number, 必填, 下单部门ID); InitTaskUpNumber(number, 必填, 任务上限数); GoodsId(number, 必填, 商品ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填)]

#### 137. 批量自动确认预存

- 所属模块：电商中台/定时任务
- 请求方式：`GET`
- 请求路径：`/order/review/batchEnsurePreTask`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 138. 顺丰下单

- 所属模块：电商中台/物流
- 请求方式：`POST`
- 请求路径：`/logistics/sf/create/order`
- 接口说明：顺丰下单
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填, 客户订单号，); Address(string, 必填, 详细地址（带省市区）); Contact(string, 必填, 联系人); PostCode(string, 非必填, 邮编); TotalWeight(number, 必填, 总重量); CargoDetails(array, 必填, 托寄物信息  必须)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Dsg(string, 非必填); Data(string, 非必填, 顺丰运单号)]

#### 139. 德邦

- 所属模块：电商中台/物流-通过物流推送码改订单状态
- 请求方式：`POST`
- 请求路径：`/logistics/route/receiveRouteForDEPPON`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[time(string, 必填, 时间); status(string, 必填, 路由吗); description(string, 必填, 描述); trackingNumber(string, 必填, 运单号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 140. ems

- 所属模块：电商中台/物流-通过物流推送码改订单状态
- 请求方式：`POST`
- 请求路径：`/logistics/route/receiveRouteForEMS`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[mailnum(string, 必填, 运单号); procdate(string, 必填, 日期); proctime(string, 必填, 时间); description(string, 必填, 描述); action(string, 必填, 动作); properdelivery(string, 必填, 路由码); notproperdelivery(string, 必填, 路由码)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 141. 顺丰

- 所属模块：电商中台/物流-通过物流推送码改订单状态
- 请求方式：`POST`
- 请求路径：`/logistics/route/receiveRouteForSF`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[mailNo(string, 必填, 运单号); opCode(string, 必填, 操作码); remark(string, 必填, 备注); acceptTime(string, 必填, 操作时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 142. 杂志面单

- 所属模块：电商中台/订单-wms对接
- 请求方式：`POST`
- 请求路径：`/`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无
- `CreateSource`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Type(integer, 必填, 查询来源2：杂志); CustId(string, 必填, type=2 运单号（即2.0的tp_final_post_magazines表ExpressNo字...)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 143. 撤销修正订单

- 所属模块：电商中台/订单-修订工单
- 请求方式：`POST`
- 请求路径：`/order/revise/cancel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderReviseId(number, 必填, 修正订单ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 144. 查询修订订单详情

- 所属模块：电商中台/订单-修订工单
- 请求方式：`GET`
- 请求路径：`/order/revise/detail/{orderReviseId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderReviseId`：required=True，type=string，说明：修订订单ID，示例：`1`

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(object, 非必填, 返回值)]

#### 145. 处理修正订单

- 所属模块：电商中台/订单-修订工单
- 请求方式：`POST`
- 请求路径：`/order/revise/handle`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderReviseId(number, 必填, 修正订单ID); PassResult(number, 必填, 审核是否通过0:不通过 1:通过); Reason(string, 必填, 审单备注); ReviewType(number, 必填, 0:合规审核  1:财务审核)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 146. 订单修订工单列表查询

- 所属模块：电商中台/订单-修订工单
- 请求方式：`POST`
- 请求路径：`/order/revise/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 非必填, 订单编号); CustomerId(number, 非必填, 客户Id); CreatorId(number, 非必填, 制单人ID); ReviseStatus(number, 非必填, 工地状态); PageIndex(number, 非必填, 页数 默认1); PageSize(integer, 非必填, 每页显示条数  默认10); UserType(number, 非必填, 用户类型 0:用户 1:审单审核 2:财务审核)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(object, 非必填, 返回值)]

#### 147. 修改订单修订工单

- 所属模块：电商中台/订单-修订工单
- 请求方式：`POST`
- 请求路径：`/order/revise/modify`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单ID); Id(integer, 必填, 修正订单ID); CashAmount(integer, 非必填, 现金消费修改为，单位：分); UseBalanceAmount(integer, 非必填, 预存消费修改为，单位：分); ChargeBalanceAmount(integer, 非必填, 预存存入，单位：分); PayAmount(integer, 非必填, 应收合计，单位：分); UseRebateAmount(integer, 非必填, 返券消费合计，单位：分); GainRebateAmount(integer, 非必填, 获得返券，单位：分); GainPoint(integer, 非必填, 获得积分); PaymentMethod(integer, 非必填, 收款方式，0-快递代收，1-款到发货，2-运费到付); BigOrderAward(integer, 非必填, 大单奖励，单位：元); UpdateGradeAward(integer, 非必填, 升级奖励，单位：元); ProductFullAward(integer, 非必填, 商品满额奖励，单位：元); Reasons(integer, 必填, 修订原因); UseCoupon(integer, 非必填, 礼券消费，单位：分); GapAmount(integer, 非必填, 客户补齐，单位：分); ...其余 1 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 消息)]

#### 148. 新增订单修订工单

- 所属模块：电商中台/订单-修订工单
- 请求方式：`POST`
- 请求路径：`/order/revise/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单ID); CashAmount(integer, 非必填, 现金消费修改为，单位：分); UseBalanceAmount(integer, 非必填, 预存消费修改为，单位：分); ChargeBalanceAmount(integer, 非必填, 预存存入，单位：分); PayAmount(integer, 非必填, 应收合计，单位：分); UseRebateAmount(integer, 非必填, 返券消费合计，单位：分); GainRebateAmount(integer, 非必填, 获得返券，单位：分); GainPoint(integer, 非必填, 获得积分); PaymentMethod(integer, 非必填, 收款方式，0-快递代收，1-款到发货，2-运费到付); BigOrderAward(integer, 非必填, 大单奖励，单位：元); UpdateGradeAward(integer, 非必填, 升级奖励，单位：元); ProductFullAward(integer, 非必填, 商品满额奖励，单位：元); Reasons(integer, 必填, 修订原因); UseCoupon(integer, 非必填, 礼券消费，单位：分); GapAmount(integer, 非必填, 客户补齐，单位：分); Freight(integer, 非必填, 运费，单位：分)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 消息)]

#### 149. 查询修正订单状态

- 所属模块：电商中台/订单-修订工单
- 请求方式：`GET`
- 请求路径：`/order/revise/status`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(array, 非必填, 返回值)]

#### 150. 新增地址

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/addAddress`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Address(object, 必填, 地址)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(object, 必填)]

#### 151. 新增电话

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/addPhone`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Phone(string, 必填, 电话); Mobile(string, 必填, 手机); CustomerId(integer, 必填, 客户ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(boolean, 必填)]

#### 152. 创建退换货订单

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/afterSale/exchange/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Products(array, 必填, 商品列表); UserId(number, 必填, 下单人ID); UserName(string, 必填, 下单人名称); UserOrgId(number, 必填, 下单人部门ID); OldOrderId(number, 必填, 销售订单ID); TotalAmount(number, 必填, 订单总金额); PayAmount(number, 必填, 订单应收金额); GainPoint(number, 必填, 获得积分); ChargeAmount(number, 必填, 充值预存 单位:分); GainRebate(number, 必填, 获得返券 单位:分); UseIntegral(number, 必填, 使用积分); UseBalance(number, 必填, 使用预存 单位:分); UseRebate(number, 必填, 使用返券 单位：分); PaymentMethod(number, 必填, 支付方式)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息); Data(number, 非必填, 退换货订单ID)]

#### 153. 销售订单-撤销

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/cancel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单ID); CancelType(number, 非必填, 撤单类型： 1:坐席撤单 2:自动撤单 3:物流撤单); Remarks(string, 非必填, 撤单备注)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(boolean, 必填)]

#### 154. 订单发货

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/delivery`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[List(array, 非必填, 发货内容)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语); Data(boolean, 必填)]

#### 155. 查询商品最大可销售量

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/goods/max/sale`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderSource(integer, 必填); OrderType(integer, 必填); OrderGoods(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填); Data(object, 必填)]

#### 156. 根据物流单号更新订单状态 Copy

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/logistics/status/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Operation(string, 必填, create  制单   review  合规审单   manager_review  经理审单  ...); LogisticsCode(string, 必填, 物流单号); Status(number, 必填, 状态，10:待修改,20:经理待审,30:合规待审,40:财务待审,50:待发货,60:撤单,70:...)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(string, 必填)]

#### 157. 修改销售制单

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/modify`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); AfterCustomerGradeId(number, 必填, 下单后客户等级ID); ReceiveAddress(object, 必填, 收货地址ID); DeliveryDemand(object, 必填, 送货方式和发票对象); ReceiptMethod(number, 必填, 收款方式); IsChargeOrder(number, 必填, 是否充值订单0:否 1:是); ApplyPersonReview(number, 必填, 是否人工审单，0-否，1-是); DelayReviewTime(string, 必填, 审核时间); FreightRule(number, 非必填, 运费规则); ReviewRemark(string, 必填, 坐席备注); Coupons(array, 非必填, 下单使用礼券); OrderMoney(object, 必填, 订单金额对象); OrderType(number, 必填, 订单类型 29:销售订单，30:员工自购，31:经销订单，32:快递理赔，33:内部领用，34:退换...); OrderSource(number, 必填, 订单来源 10:CRM 20:有赞 30:管易); IsNewPhone(number, 必填, 下单页面是否新增收货电话   0:否  1:是); IsUpgrade(number, 必填, 是否升级 0:未升级  1:大单升级 2:累计升级); ...其余 5 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(number, 必填, 订单ID)]

#### 158. 订单合并

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/orders/mergeOrder`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填, 源用户id); TargetId(integer, 必填, 目标客户id); TargetCustomerName(string, 必填, 目标客户名称)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 159. 销售制单-修订

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/orders/revise`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单ID); PaymentMethod(integer, 非必填, 收款方式); UseBalance(integer, 非必填, 使用余额，单位：分); ChargeAmount(integer, 非必填, 充值金额，单位：分); Reason(string, 必填, 修订原因); CashAmount(integer, 非必填, 现金金额，单位：分); PayAmount(integer, 非必填, 实付金额，单位：分); UseRebate(integer, 非必填, 使用返券，单位：分); GainPoint(integer, 非必填, 获得积分); GainRebate(integer, 非必填, 获得返券); BigOrderAward(number, 非必填, 大单奖励 ，单位：分); GradeAward(number, 非必填, 升级奖励，单位：分); ProductAward(number, 非必填, 产品奖励，单位：分)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息)]

#### 160. 出库制单

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/outbound`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[customer(object, 必填, 客户信息); receiver(object, 必填, 收货人信息); address(object, 必填, 地址); deliveryRequirement(string, 必填, 送货要求); payWay(string, 必填, 收款方式：0-款到发货 1-货到付款); products(array, 必填); couponAmount(number, 必填, 实际使用券，单位：元); cashAmount(number, 必填, 实际支付，单位：元); type(integer, 必填, 订单类型)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(object, 必填)]

#### 161. 出库订单-撤单

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/outbound/cancel/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[reason(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 162. 出库订单-提交修改

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/outbound/modify/submit/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[customer(object, 必填, 客户信息); receiver(object, 必填, 收货人信息); deliveryRequirement(string, 必填, 送货要求); payWay(string, 必填, 收款方式：0-款到发货 1-货到付款); products(array, 必填); couponAmount(number, 必填, 实际使用券，单位：元); cashAmount(number, 必填, 实际支付，单位：元); type(integer, 必填, 订单类型)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(object, 必填)]

#### 163. 出库订单-退回修改

- 所属模块：电商中台/订单-制单
- 请求方式：`GET`
- 请求路径：`/order/outbound/modify/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 164. 出库订单-单个查询

- 所属模块：电商中台/订单-制单
- 请求方式：`GET`
- 请求路径：`/order/outbound/query/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[orderInnerItems(array, 必填); logistics(object, 必填); orderInnerBill(object, 必填); reviewInfo(object, 必填)]

#### 165. 销售订单-拒收

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/reject`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCodeList(array, 必填, 订单编号列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(boolean, 必填)]

#### 166. 销售订单-取回

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/retrieve`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(boolean, 必填)]

#### 167. 取回管控限发订单

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/retrieve/limitDelivery`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Ids(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 168. 销售制单

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderSource(integer, 必填, 订单来源 10:CRM 20:有赞 30:管易); OrderType(integer, 必填, 订单类型 29:销售订单，30:员工自购，31:经销订单，32:快递理赔，33:内部领用，34:退换...); CustomerId(integer, 必填, 客户ID); CustomerName(string, 必填); GradeName(string, 必填); ReceiptMethod(integer, 必填, 收款方式); IsChargeOrder(integer, 必填, 是否充值订单0:否 1:是); ApplyPersonReview(integer, 必填, 是否人工审单，0-否，1-是); DelayReviewTime(string, 必填, 审核时间); IsNewPhone(integer, 必填, 下单页面是否新增收货电话   0:否  1:是); AfterCustomerGradeId(integer, 必填, 下单后客户等级ID); ReceiveAddress(object, 必填, 收货地址ID); DeliveryDemand(object, 必填, 送货方式和发票对象); IsUpgrade(integer, 必填, 是否升级 0:未升级  1:大单升级 2:累计升级); IsCancelBigAward(integer, 必填, 是否取消大单奖励 0:否 1:是); LaunchId(integer, 必填); ...其余 8 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(number, 必填, 订单ID)]

#### 169. 修改订单状态

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/status/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Operation(string, 必填, create  制单   review  合规审单   manager_review  经理审单  ...); BatchNo(string, 必填, 批次号); Status(number, 必填, 状态，10:待修改,20:经理待审,30:合规待审,40:财务待审,50:待发货,60:撤单,70:...)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(string, 必填)]

#### 170. 销售制单暂存

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/temporary/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); Data(string, 必填, 订单数据)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(number, 必填, 订单ID)]

#### 171. 查询暂存订单

- 所属模块：电商中台/订单-制单
- 请求方式：`POST`
- 请求路径：`/order/temporary/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(number, 必填, 订单数据)]

#### 172. 查询商品可用库存

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`GET`
- 请求路径：`/commodity/inventory/getAvailableInventory/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/octet-stream` type=object; fields=[]

#### 173. 批量查询库存信息

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`POST`
- 请求路径：`/commodity/inventory/getInventories`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=array; items=(type=string)

**返回体**

- `200`：无描述；`application/json` type=array; items=(type=object; fields=[SkuCode(string, 必填, 商品编号); AvailableStock(integer, 必填, 可用库存); LockStock(integer, 必填, 锁定库存)])

#### 174. 查询商品占用库存

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`GET`
- 请求路径：`/commodity/inventory/getLockInventory/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(integer, 必填, 商品占用库存)]

#### 175. 释放库存

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`POST`
- 请求路径：`/commodity/inventory/releaseInventory`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无
- `CreateSource`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 必填); Inventory(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 176. 同步库存

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`POST`
- 请求路径：`/commodity/inventory/syncInventory`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=array; items=(type=object; fields=[Code(string, 必填, 产品编号); Inventory(integer, 必填, 库存)])

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 177. 批量锁定预售库存

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`POST`
- 请求路径：`/cx/stock/batch/presalestock/lock`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填, 订单号); ShopId(integer, 必填, 店铺Id); List(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 178. 批量锁定库存

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`POST`
- 请求路径：`/cx/stock/batchLock`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填, 订单号); ShopId(integer, 必填, 店铺Id); ClaimFlag(integer, 非必填, 0:正常订单 1:理赔订单 2:预售订单); List(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 179. 批量释放库存

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`POST`
- 请求路径：`/cx/stock/batchRelease`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填); ShopId(integer, 必填); ClaimFlag(integer, 必填, 0:正常订单 1:理赔订单 2:预售订单); List(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 180. 订单发货释放库存

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`POST`
- 请求路径：`/cx/stock/delivery`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填); ShopId(integer, 必填); ClaimFlag(integer, 必填, 0:正常订单 1:理赔订单 2:预售订单); List(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 181. 查询所有承运商

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`GET`
- 请求路径：`/logistics/documentary/carrier`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `CarrierTypeId`：required=True，type=string，说明：承运商类型ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(array, 非必填, 返回值)]

#### 182. 查询路由状态码

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`GET`
- 请求路径：`/logistics/documentary/route/code`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `CarrierTypeId`：required=True，type=string，说明：承运商类型ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息); Data(array, 非必填, 返回值)]

#### 183. 查询二级路由描述

- 所属模块：电商中台/订单-商品-物流
- 请求方式：`GET`
- 请求路径：`/logistics/documentary/route/spec`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 184. 重新计算订单奖励数据并更新入库

- 所属模块：电商中台/订单-奖励
- 请求方式：`POST`
- 请求路径：`/order/reward//customer/rebate/recalculate`
- 接口说明：更新范围：2020年07-28 00:00:00 之前 所有2.0的订单
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 185. 计算某个订单的返券奖励

- 所属模块：电商中台/订单-奖励
- 请求方式：`GET`
- 请求路径：`/order/reward/customer/rebate/calculate/{orderId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderId`：required=True，type=string，说明：订单id，示例：`23620804`

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(object, 必填)]

#### 186. 重新计算某个订单的奖励并更新入库

- 所属模块：电商中台/订单-奖励
- 请求方式：`POST`
- 请求路径：`/order/reward/customer/rebate/{orderId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- `orderId`：required=True，type=string，说明：无，示例：`23620804`

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 187. 重新计算部分订单的返券奖励并更新入库

- 所属模块：电商中台/订单-奖励
- 请求方式：`POST`
- 请求路径：`/reward/customer/rebate/recalculate/part`
- 接口说明：更新范围：2020年07-28 00:00:00 之前 所有2.0的订单
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PageIndex(number, 必填); PageSize(number, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 188. 查询审单配置必审规则列表

- 所属模块：电商中台/订单-审单配置
- 请求方式：`GET`
- 请求路径：`/order/examine/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `PageIndex`：required=True，type=string，说明：页数，示例：`1`
- `PageSize`：required=True，type=string，说明：每页显示条数，示例：`10`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语); Data(object, 必填, 返回值)]

#### 189. 查询符合订单的必审规则

- 所属模块：电商中台/订单-审单配置
- 请求方式：`GET`
- 请求路径：`/order/examine/rule`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=True，type=string，说明：订单ID
- `ConfigId`：required=True，type=string，说明：审单必审规则ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 190. 配置列表

- 所属模块：电商中台/订单-审单配置
- 请求方式：`POST`
- 请求路径：`/order/review/config/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Type(integer, 必填); PageIndex(integer, 必填); PageSize(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 191. 移交

- 所属模块：电商中台/订单-审核
- 请求方式：`POST`
- 请求路径：`/order/review/batch`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[reviewIds(array, 必填, 审单数据id); UserIds(array, 必填, 移交用户ID); Num(integer, 必填, 分配条数)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 信息); Data(object, 必填)]

#### 192. 审单

- 所属模块：电商中台/订单-审核
- 请求方式：`GET`
- 请求路径：`/order/review/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：无
- `type`：required=True，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 信息); Data(object, 必填)]

#### 193. 判断是否审单员

- 所属模块：电商中台/订单-审核
- 请求方式：`POST`
- 请求路径：`/order/review/judge`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 194. 判断订单是否可审

- 所属模块：电商中台/订单-审核
- 请求方式：`POST`
- 请求路径：`/order/review/judge/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 195. 审单不通过

- 所属模块：电商中台/订单-审核
- 请求方式：`POST`
- 请求路径：`/order/review/notPass/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[reviewDesc(string, 必填, 审单备注); notPassReason(integer, 必填, 不通过原因); actualFreeReview(integer, 必填, 实际免审 勾选传1 不勾选不传); payFreight(integer, 必填, 运费规则); type(integer, 必填, 订单类型)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 196. 开始审单

- 所属模块：电商中台/订单-审核
- 请求方式：`GET`
- 请求路径：`/order/review/open/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[AgentDesc(string, 必填, 坐席备注); ReviewDesc(string, 必填, 审单备注); NotPassReason(integer, 必填, 不通过原因); ActualFreeReview(integer, 必填, 实际免审，勾选了传1，不勾选不传); PayFreight(integer, 必填, 运费规则); Type(integer, 必填, 订单类型)]

#### 197. 审单通过

- 所属模块：电商中台/订单-审核
- 请求方式：`POST`
- 请求路径：`/order/review/pass/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ReviewDesc(string, 非必填, 审单备注); ActualFreeReview(integer, 非必填, 实际免审？ 勾选传1 不勾选不传); PayFreight(integer, 必填, 运费规则); Type(integer, 必填, 订单类型)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 198. 复杂查询

- 所属模块：电商中台/订单-审核
- 请求方式：`POST`
- 请求路径：`/order/review/query`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[code(string, 必填, 订单编码); status(integer, 必填, 订单状态); customerId(integer, 必填, 客户id); customerLevel(array, 必填, 客户等级); makerId(string, 必填, 制单人id); reviewerId(integer, 必填, 审单人id); requiredOrgId(integer, 必填, 组织架构); distribute(integer, 必填, 是否已分配 0：没有 1：已分配); minDistributionTime(string, 必填, 开始分配时间); maxDistributionTime(string, 必填, 结束分配时间); minMakeTime(string, 必填, 开始制单时间); maxMakeTime(string, 必填, 结束制单时间); minAmount(number, 必填, 开始订单金额 元); maxAmount(number, 必填, 结束订单金额 元); isSystemReview(string, 必填, 传1 表示免审 不选不传); must(string, 必填, 传1 表示必审 不选不传); ...其余 2 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息); Data(object, 必填)]

#### 199. 审核订单统计

- 所属模块：电商中台/订单-审核
- 请求方式：`GET`
- 请求路径：`/order/review/statistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息); Data(object, 必填)]

#### 200. 审单暂存

- 所属模块：电商中台/订单-审核
- 请求方式：`POST`
- 请求路径：`/order/review/storage/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[reviewDesc(string, 必填, 审单备注); notPassReason(string, 必填, 不通过原因); actualFreeReview(integer, 必填, 实际免审 勾选就传1); payFreight(integer, 必填, 运费规则); type(integer, 必填, 订单类型)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 201. 自取审单

- 所属模块：电商中台/订单-审核
- 请求方式：`POST`
- 请求路径：`/order/review/take`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(integer, 必填, id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 202. 校验是否有未处理完的任务

- 所属模块：电商中台/订单-批量任务
- 请求方式：`GET`
- 请求路径：`/order/batch/task/checkTaskIsFinished`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `type`：required=True，type=string，说明：任务类型，1:批量财务审单，2:批量财务收款，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[data(boolean, 必填, true:有未处理完的任务，false：没有)]

#### 203. 查询物流跟单员接口

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/logistics/track/order/{orderCode}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderCode`：required=True，type=string，说明：订单编号

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 204. 退换货查询销售订单列表

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/afterSale/queryList`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(number, 非必填, 商品编号); StatusList(array, 非必填, 订单状态列表); DeliveryCode(string, 非必填, 运单号); CustomerId(number, 非必填, 客户ID); GoodsId(number, 非必填, 商品ID); AmountMin(number, 非必填, 订单开始金额 单位:分); AmountMax(number, 非必填, 订单结束金额 单位:分); CreateTimeBegin(string, 非必填, 制单开始金额); CreateTimeEnd(string, 非必填, 制单结束金额); DeliveryTimeBegin(string, 非必填, 发货开始时间); DeliveryTimeEnd(string, 非必填, 发货结束时间); IsNormalOrder(number, 非必填, 是否正常订单 0:否 1；是); IsSelf(number, 非必填, 与我相关 0-否 1-是); UserId(number, 非必填, 下单人ID); ReviewerId(number, 非必填, 审单人ID); ReviewStartTime(string, 非必填, 审单开始时间); ...其余 8 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(object, 非必填)]

#### 205. 查询客户明细订单

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/customer`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 非必填, 客户ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 206. 查询订单完结个数

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/customer/finish/number`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `CustomerId`：required=True，type=string，说明：客户ID
- `OrgType`：required=True，type=string，说明：组织类型 1:媒体 2:会员中心 3:客服 4:启航 5:新训 6:其他
- `OrderType`：required=True，type=string，说明：订单类型
- `IsFinished`：required=True，type=string，说明：0:未完结 1:完结 2:所有

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 207. 查询订单详情

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrdeId`：required=True，type=string，说明：订单ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 208. 获取订单Code和CustomerId

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/detail/id`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=True，type=string，说明：订单Id

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 209. 查询销售订单列表

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无
- `CurrentUser`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(number, 非必填, 商品编号); StatusList(array, 非必填, 订单状态列表); DeliveryCode(string, 非必填, 运单号); CustomerId(number, 非必填, 客户ID); GoodsId(number, 非必填, 商品ID); AmountMin(number, 非必填, 订单开始金额 单位:分); AmountMax(number, 非必填, 订单结束金额 单位:分); CreateTimeBegin(string, 非必填, 制单开始金额); CreateTimeEnd(string, 非必填, 制单结束金额); DeliveryTimeBegin(string, 非必填, 发货开始时间); DeliveryTimeEnd(string, 非必填, 发货结束时间); IsNormalOrder(number, 非必填, 是否正常订单 0:否 1；是); IsSelf(number, 非必填, 与我相关 0-否 1-是); UserId(number, 非必填, 下单人ID); ReviewerId(number, 非必填, 审单人ID); ReviewStartTime(string, 非必填, 审单开始时间); ...其余 8 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 210. 查询客户未结案订单个数

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/notFinish/number`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `CustomerId`：required=True，type=string，说明：客户ID
- `OrderId`：required=True，type=string，说明：订单ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语); Data(number, 必填, 累计拒收个数)]

#### 211. 查询订单收货地址

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/address/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：订单ID

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回信息); Data(string, 必填, 返回值)]

#### 212. 查询客户购买策略商品个数接口

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/customer/buy/limit`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `CustomerId`：required=True，type=string，说明：客户ID
- `StrategyId`：required=True，type=string，说明：策略ID
- `OrderId`：required=False，type=string，说明：订单ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(number, 必填, 已经购买个数)]

#### 213. 查询订单详情页物流信息

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/detail/logistics/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 214. 过滤查询用户列表

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/orders/filterUsers`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrgIds(array, 必填, 部门ID集合); AccountOrName(string, 必填, 工号或者用户名); OrderCountMin(integer, 必填, 成交单数最小值); OrderCountMax(integer, 必填, 成交单数最大值); OrderAmountMin(integer, 必填, 每单价格最小值，单位：分); OrderAmountMax(integer, 必填, 每单价格最大值，单位：分); OrderTimeStart(string, 必填, 制单开始时间); OrderTimeEnd(string, 必填, 制单结束时间); OrderStatus(integer, 必填, 订单状态)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 215. 查询订单商品

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/goods/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：订单ID

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 216. 根据订单号获取订单信息，客户信息（物流跟单处理页使用）

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/logistics/orderCustomerInfo/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 217. 查询订单物流信息

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/logistics/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 218. 根据订单编号查询订单详情

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/orders/queryByCode`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 必填, 订单编号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 219. 根据客户ID和坐席ID查询最近签收非0订单的时间

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/orders/queryNonZeroByCustomerIdAndUserId`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填); UserId(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(string, 必填)]

#### 220. 查询客户的最新下单时间和订单号

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/orders/queryOrderTimeAndCode`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerIds(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 221. 查询订单收货人信息

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/receiver/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：订单ID

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 222. 根据客户ID查询拒收次数

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/orders/rejectOrderTimes`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(integer, 必填)]

#### 223. 查询订单审单信息

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/reviewInfo/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：订单ID

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 224. 查询订单奖励信息

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/rewardInfo/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 坐席的大单奖励，单位：分); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 225. 查询客户的订单统计信息

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/orders/statistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填, 客户ID); Name(string, 必填, 客户姓名); Level(integer, 必填, 客户等级)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息); Data(object, 必填)]

#### 226. 查询订单状态值映射列表

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/status`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 返回码); msg(string, 必填, 信息); data(array, 必填)]

#### 227. 导出订单模板

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/orders/{id}/template`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- `id`：required=True，type=string，说明：订单ID

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 编号); msg(string, 必填, 信息); data(object, 必填)]

#### 228. 查询出库订单列表

- 所属模块：电商中台/订单-查询
- 请求方式：`GET`
- 请求路径：`/order/outOrders`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息); Data(object, 必填)]

#### 229. 出库订单复杂查询

- 所属模块：电商中台/订单-查询
- 请求方式：`POST`
- 请求路径：`/order/outbound/query`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 必填, 订单号); Type(integer, 必填, 类型); Status(array, 必填, 状态); PayWay(integer, 必填, 收款方式); CustomerId(integer, 必填, 客户id); ProductId(integer, 必填, 产品id); MinAmount(number, 必填, 大于订单金额); MaxAmount(number, 必填, 小于订单金额); BeginOrderTime(string, 必填, 大于制单时间); EndOrderTime(string, 必填, 小于制单时间); BeginReviewTime(string, 必填, 大于审单时间); EndReviewTime(string, 必填, 小于审单时间); BeginDeliveryTime(string, 必填, 大于发货时间); EndDeliveryTime(string, 必填, 小于发货时间); RequiredOrgId(integer, 必填, 所属组别); MakerId(string, 必填, 审单人名)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[msg(string, 必填); data(object, 必填); code(string, 必填)]

#### 230. 查询在途异常配置详情

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/documentary/config/detail/{configId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `configId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 231. 更改滞留配置状态

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/documentary/changeStatus`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[List(array, 必填, 在途异常配置ID列表); Status(number, 必填, 0:停用  1:启用)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 232. 删除滞留配置

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/documentary/config/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 在途异常配置ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 233. 查询滞留配置

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/documentary/config/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[carrierType(integer, 必填, 承运商类型 字典); routeCode(integer, 必填, 路由码); status(integer, 必填, 状态 0：停用 1：启用); PageIndex(number, 必填, 页数); PageSize(number, 必填, 每页条数)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 234. 配置滞留时长

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/documentary/saveTransitConfig`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CarrierType(integer, 必填, 承运商类型); RouteCode(integer, 必填, 路由码); Hours(integer, 必填, 时长); StartTime(string, 必填, 开始时间); EndTime(string, 必填, 结束时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 235. 查询所有技能组

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/documentary/skillSet/all`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(array, 非必填, 返回值)]

#### 236. 删除技能组

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/documentary/skillSet/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 技能组ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 237. 技能组详情

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/documentary/skillSet/detail/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `id`：required=True，type=string，说明：技能组ID，示例：`id`

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 238. 查询技能组

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/documentary/skillSet/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PageIndex`：required=True，type=string，说明：页数，示例：`1`
- `PageSize`：required=True，type=string，说明：每页显示条数，示例：`100`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 239. 查询技能组成员

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/documentary/skillSet/member`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `SkillSetId`：required=True，type=string，说明：技能组ID
- `UserId`：required=True，type=string，说明：用户ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回值); Msg(string, 非必填, 返回信息); Data(array, 非必填, 返回值)]

#### 240. 保存技能组

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/documentary/skillSet/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Name(string, 非必填, 技能组名称); Quantity(number, 非必填, 自取条数); DepartmentList(array, 非必填, 部门列表); CarrierList(array, 非必填, 承运商列表); UserList(array, 非必填, 用户列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回提示语)]

#### 241. 修改技能组

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/documentary/skillSet/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Name(string, 非必填, 技能组名称); Quantity(number, 非必填, 自取条数); DepartmentList(array, 非必填, 部门列表); CarrierList(array, 非必填, 承运商列表); UserList(array, 非必填, 用户列表); Id(number, 非必填, 技能组ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 返回提示语)]

#### 242. 获取单个路由

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/route/getRoutes/{logisticsCode}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `logisticsCode`：required=True，type=string，说明：物流单号，示例：`LK434266003CN`

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(array, 必填)]

#### 243. 拒收扣款跟单明细

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/track/chargebackDetail/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 244. 批量复制运单号

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/copy/logistics/code`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Ids(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(array, 必填)]

#### 245. 跟单数据详情(拒收处理)

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/detail/{trackType}/{mailNum}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `trackType`：required=True，type=string，说明：无，示例：`跟单类型 404 405 407`
- `mailNum`：required=True，type=string，说明：无，示例：`物流单号`

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 必填); Data(object, 必填)]

#### 246. 跟单数据详情（跟单处理）(废弃停用)

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/detail/{trackType}/{mailNum}_1586501234792`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `trackType`：required=True，type=string，说明：无，示例：`跟单类型 404 405 407`
- `mailNum`：required=True，type=string，说明：无，示例：`物流单号`

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 必填); Data(object, 必填)]

#### 247. 跟单分配

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/distribution`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Ids(array, 必填, 跟单id); UserIds(array, 必填, 分配人员id); Num(number, 必填, 平均分配数量)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); MSg(string, 必填); Data(object, 必填)]

#### 248. 根据运单号获取加密手机号（掩码+加密)

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/track/get/courier/encrypt/phone/{logisticsCode}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `logisticsCode`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填, 电话号码)]

#### 249. 根据运单号查询快递员信息

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/track/getCourierInfoByLogisticsCode/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填, 电话号码)]

#### 250. 根据运单号查询快递员号码

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/track/getCourierPhoneByLogisticsCode/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(string, 非必填, 电话号码)]

#### 251. 根据运单号查询快递员明文号码

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/track/getCourierPlainPhoneByLogisticsCode/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(string, 非必填, 电话号码)]

#### 252. 根据订单号获取跟单记录

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/track/getDocumentaryRecords/{OrderCode}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `OrderCode`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(array, 必填)]

#### 253. 查询技能组下所有成员

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/logistics/track/getSkillsetMembers/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(array, 必填)]

#### 254. 根据多个订单号获取跟单员姓名

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/getTrackersByOrderCodes`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCodes(array, 必填, 订单号数组)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 255. 新增跟单任务

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/newTask/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 256. 查询跟单信息

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/queryLogisticsTrack`
- 接口说明：和跟单再分配查询一样
- 鉴权方式：Authorization 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[beginRefuseRate(number, 必填, 开始拒收率); endRefuseRate(number, 必填, 结束拒收率); todayAppointment(integer, 必填, 今日预约); todayStar(integer, 必填, 今日五角星); mime(integer, 必填, 与我相关); trackInfo(object, 必填, 跟单信息); orderInfo(object, 必填, 订单信息); assign(integer, 必填, 是否已分配 0：否 1：是)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[备注(string, 必填, 返回值和跟单再分配查询一样)]

#### 257. 保存跟单(拒收处理)（弃用停用）

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/save_`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Feedback(string, 必填, 跟单反馈); ContactResult(integer, 必填, 联络结果); Id(integer, 必填, 当前跟单数据id); FirstReason(integer, 必填, 第一拒收原因); SecondReason(integer, 必填, 第二拒收原因); ThirdReason(integer, 必填, 第三拒收原因)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 258. 更新跟单记录结果

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/updateLogisticsTrackResult`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[UserId(number, 必填, 坐席id); CustomerId(number, 必填, 客户id); CallStartTime(string, 必填, 拨打电话开始时间); CallEndTime(string, 必填, 拨打电话结束时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 259. 更改拒收原因

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/track/updateRejectReason`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填, 当前跟单数据id); FirstReason(integer, 必填, 第一拒收原因); SecondReason(integer, 必填, 第二拒收原因); ThirdReason(integer, 必填, 第三拒收原因)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 260. 自取下一条

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/logistics/trackNext`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填, 订单号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); MSg(string, 必填); Data(object, 必填)]

#### 261. 根据订单id查询运单号（存在子母单的情况）

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/order/logistics/get/logisticsCode/{orderId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderId`：required=True，type=string，说明：无

**Query 参数**

- `OrderWaybillCodeId`：required=False，type=string，说明：无，示例：`运单批次Id`
- `UserId`：required=True，type=string，说明：无，示例：`坐席Id`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填, 物流单号)]

#### 262. 根据订单id查询快递员号码

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/order/logistics/getCourierPhone/{orderId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填, 快递员号码)]

#### 263. 获取运单号查询订单全部运单路由

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/order/logistics/route/{logisticsCode}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `logisticsCode`：required=True，type=string，说明：物流单号，示例：`LK434266003CN`

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(array, 必填)]

#### 264. 根据订单id或者运单批次号查询订单全部运单路由

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`GET`
- 请求路径：`/order/logistics/routeByOrderId/{orderId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderId`：required=True，type=string，说明：无

**Query 参数**

- `OrderWaybillCodeId`：required=False，type=string，说明：运单批次号，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(array, 必填)]

#### 265. 拒收扣款查询

- 所属模块：电商中台/订单-物流跟单
- 请求方式：`POST`
- 请求路径：`/order/orders/rejectionStatistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[RejectionTime(string, 必填, 拒收月); RequiredOrgId(integer, 必填, 组织架构id); Code(string, 必填, 订单号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 266. 审核补贴

- 所属模块：电商中台/订单-经理审核
- 请求方式：`POST`
- 请求路径：`/order/orders/auditSubsidy`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[IsPass(boolean, 必填, 是否通过); Remark(string, 必填, 备注); OrderId(integer, 必填, 订单ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 267. 经理审核

- 所属模块：电商中台/订单-经理审核
- 请求方式：`POST`
- 请求路径：`/order/orders/review/manager`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[orderId(string, 必填, 订单id); result(string, 必填, 0：不通过 1：通过); remark(string, 必填, 备注)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 268. 经理审核

- 所属模块：电商中台/订单-经理审核
- 请求方式：`POST`
- 请求路径：`/order/saleOrders/review`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单ID); IsPass(boolean, 必填, 是否通过)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 信息); Data(object, 必填)]

#### 269. 确认收款

- 所属模块：电商中台/订单-财务审核
- 请求方式：`POST`
- 请求路径：`/order/batchConfirmMoney`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[orderIds(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 270. 确认预存

- 所属模块：电商中台/订单-财务审核
- 请求方式：`POST`
- 请求路径：`/order/confirmPreStorage/{orderId}/{userId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- `orderId`：required=True，type=string，说明：无
- `userId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 271. 财务确认收款页面查询订单列表

- 所属模块：电商中台/订单-财务审核
- 请求方式：`POST`
- 请求路径：`/order/financeOrders`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `code`：required=True，type=string，说明：无

**请求体**

- `application/json`：type=object; fields=[Code(string, 必填, 订单号); status(integer, 必填, 订单状态); customerNo(string, 必填, 客户编号); logisticsCodes(array, 必填, 物流单号,多个)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[page(object, 必填)]

#### 272. 财务审核

- 所属模块：电商中台/订单-财务审核
- 请求方式：`POST`
- 请求路径：`/order/orders/financial`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[mark(string, 必填, 财务审核备注); payWay(integer, 必填, 支付方式，0：现金，1：pos，2：银行转账，3：微信，4：支付宝，5：其他); pass(integer, 必填, 0：不通过，1：通过); orderId(integer, 必填, 订单ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息)]

#### 273. 校验转账码是否被使用过

- 所属模块：电商中台/订单-财务审核
- 请求方式：`POST`
- 请求路径：`/order/orders/financial/batch/checkTransferCode`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 非必填, 订单编号); Status(number, 非必填, 订单状态); CustomerId(number, 非必填, 客户ID); ReviewerId(number, 非必填, 合规审单人ID); MakerId(number, 非必填, 制单人ID); MakerOrgId(number, 非必填, 制单人部门ID); MinOrderMoney(number, 非必填, 订单金额 单位:元); MaxOrderMoney(number, 非必填, 订单金额 单位:元); OrderType(number, 非必填, 订单类型ID); StartTime(number, 非必填, 制单开始时间); EndTime(number, 非必填, 制单结束时间); Ids(array, 非必填, 订单id数组); PayWay(number, 必填); Mark(string, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(string, 非必填)]

#### 274. 批量财务审单

- 所属模块：电商中台/订单-财务审核
- 请求方式：`POST`
- 请求路径：`/order/orders/financial/batch/review`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 非必填, 订单编号); Status(number, 非必填, 订单状态); CustomerId(number, 非必填, 客户ID); ReviewerId(number, 非必填, 合规审单人ID); MakerId(number, 非必填, 制单人ID); MakerOrgId(number, 非必填, 制单人部门ID); MinOrderMoney(number, 非必填, 订单金额 单位:元); MaxOrderMoney(number, 非必填, 订单金额 单位:元); OrderType(number, 非必填, 订单类型ID); StartTime(number, 非必填, 制单开始时间); EndTime(number, 非必填, 制单结束时间); Ids(array, 非必填, 订单id数组); PayWay(number, 必填); Mark(string, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(string, 非必填)]

#### 275. 查询审核订单列表

- 所属模块：电商中台/订单-财务审核
- 请求方式：`POST`
- 请求路径：`/order/orders/financial/query`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 非必填, 订单编号); Status(number, 非必填, 订单状态); CustomerId(number, 非必填, 客户ID); ReviewerId(number, 非必填, 合规审单人ID); MakerId(number, 非必填, 制单人ID); MakerOrgId(number, 非必填, 制单人部门ID); MinOrderMoney(number, 非必填, 订单金额 单位:元); MaxOrderMoney(number, 必填, 订单金额 单位:元); OrderType(number, 非必填, 订单类型ID); StartTime(number, 非必填, 制单开始时间); EndTime(number, 非必填, 制单结束时间); PageIndex(number, 非必填, 页数 默认1); PageSize(number, 非必填, 每页显示条数)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回提示语); Data(object, 非必填)]

#### 276. 财务详情

- 所属模块：电商中台/订单-财务审核
- 请求方式：`POST`
- 请求路径：`/order/orders/financialReview/detail/{code}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- `code`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 277. 查询

- 所属模块：电商中台/订单-财务确认收款
- 请求方式：`POST`
- 请求路径：`/order/review/ensureFinancial/query`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[LogisticsCodes(array, 必填, 运单号); Code(string, 必填, 订单号); CustomerCode(string, 必填, 客户编号); HandleStatus(integer, 必填, 1未处理 2已经处理); Status(integer, 必填, 订单状态); OrderType(integer, 必填, 订单类型); payWay(integer, 必填, 支付方式); makerId(integer, 必填, 制单人); CreateBeginTime(string, 必填, 制单时间 左 yyyy-MM-dd); CreateEndTime(string, 必填, 制单时间 右 yyyy-MM-dd HH:mm:ss)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(array, 必填)]

#### 278. 确认财务

- 所属模块：电商中台/订单-财务确认收款
- 请求方式：`POST`
- 请求路径：`/order/review/ensureFund`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Type(integer, 必填); Ids(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(integer, 必填, 成功的个数)]

#### 279. 确认预存

- 所属模块：电商中台/订单-财务确认收款
- 请求方式：`POST`
- 请求路径：`/order/review/ensurePre`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填); Type(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 280. 查询订单包邮金额

- 所属模块：电商中台/订单包邮
- 请求方式：`POST`
- 请求路径：`/order/orders/config/department/money`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(number, 必填, 订单包邮金额)]

#### 281. 查询订单包邮配置详情

- 所属模块：电商中台/订单包邮
- 请求方式：`GET`
- 请求路径：`/order/orders/config/detail/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：订单包邮配置ID

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 282. 查询商品是否可以免邮

- 所属模块：电商中台/订单包邮
- 请求方式：`POST`
- 请求路径：`/order/orders/config/goods/freight`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[GoodsList(array, 必填, 商品列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 283. 保存订单配置

- 所属模块：电商中台/订单包邮
- 请求方式：`POST`
- 请求路径：`/order/orders/config/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DepartmentId(number, 必填, 部门ID); PackageMailMoney(number, 必填, 包邮金额); NoAuditTime(number, 必填, 免审时长(分钟)); ReturnTimes(number, 必填, 退回次数); GoodsList(array, 必填, 商品列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息)]

#### 284. 查询订单配置

- 所属模块：电商中台/订单包邮
- 请求方式：`GET`
- 请求路径：`/order/orders/config/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `DepartmentId`：required=False，type=string，说明：部门ID
- `GoodsId`：required=False，type=string，说明：商品ID
- `PageIndex`：required=True，type=string，说明：页数
- `PageSize`：required=True，type=string，说明：每页显示条数

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 285. 根据部门组织ID查询包邮配置

- 所属模块：电商中台/订单包邮
- 请求方式：`GET`
- 请求路径：`/order/orders/config/selectOrderConfigByOrgId`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `UserOrgId`：required=True，type=string，说明：用户组织ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 286. 修改订单配置

- 所属模块：电商中台/订单包邮
- 请求方式：`POST`
- 请求路径：`/order/orders/config/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 订单配置ID); DepartmentId(number, 必填, 部门ID); PackageMailMoney(number, 必填, 包邮金额); NoAuditTime(number, 必填, 免审时长(分钟)); ReturnTimes(number, 必填, 退回次数); GoodsList(array, 必填, 商品列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息)]

#### 287. 订单

- 所属模块：百弘wms/公共分类
- 请求方式：`POST`
- 请求路径：`/http://192.168.100.214:8082/BH_EDI/order/order.action`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[order(object, 必填); orderDetails(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填); msg(string, 必填); data(string, 必填)]

#### 288. 撤单

- 所属模块：百弘wms/公共分类
- 请求方式：`POST`
- 请求路径：`/http://192.168.100.214:8082/order/cancelOrder.action`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[orderId(string, 必填, 订单id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填); msg(string, 必填); data(string, 必填)]

#### 289. 合作伙伴对应媒体投放形成的订单列表

- 所属模块：聚合查询/联络系统聚合查询
- 请求方式：`POST`
- 请求路径：`/AggrQuery/MediaSeach/MediaPlacementOrderQuery`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无
- `CurrentUser`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderStartTime(string, 非必填, 订单开始时间); OrderEndTime(string, 非必填, 订单结束时间); PageSize(number, 必填, 页大小); PageIndex(number, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 状态码，1000表示成功); msg(string, 必填, 提示信息); Data(object, 必填, 结果)]

#### 290. 当月业绩查询

- 所属模块：聚合查询/首页看板
- 请求方式：`GET`
- 请求路径：`/AggrQuery/Order/MTDSalesPerformance`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(array, 必填)]

#### 291. 当天业绩查询

- 所属模块：聚合查询/首页看板
- 请求方式：`GET`
- 请求路径：`/AggrQuery/Order/TodaySalesPerformance`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(array, 必填)]

#### 292. 获取某个客户在某个时间段的所有（签收、已收）订单累计获得积分

- 所属模块：订单中心
- 请求方式：`GET`
- 请求路径：`/localhost/order/money/points`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：无，示例：`8767572`
- `st`：required=True，type=string，说明：无，示例：`2023-01-01`
- `et`：required=True，type=string，说明：无，示例：`2023-12-01`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(integer, 必填)]

#### 293. 制单人最近一笔未结案订单的跟单员

- 所属模块：订单中心
- 请求方式：`GET`
- 请求路径：`/notFinish/{userId}/trackers`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `userId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 294. 异业合作订单运单导入更新订单状态（签收、拒收）

- 所属模块：订单中心
- 请求方式：`POST`
- 请求路径：`/order/agent/sale/import/logisticCode`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[file(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(null, 必填)]

#### 295. 订单客户信息

- 所属模块：订单中心
- 请求方式：`GET`
- 请求路径：`/order/code/info`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderCode`：required=False，type=string，说明：无，示例：`XJTS0120250430000016`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 296. 查询客户在当前登陆人所在部门的近12个月消费

- 所属模块：订单中心
- 请求方式：`GET`
- 请求路径：`/order/money/consumption/last-12-month/{customerId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `customerId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(integer, 必填)]

#### 297. 查询客户（年度、月度）消费金额和限额

- 所属模块：订单中心
- 请求方式：`GET`
- 请求路径：`/order/money/consumption/sale-limit/{customerId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `customerId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 298. scrm一键下单

- 所属模块：订单中心
- 请求方式：`POST`
- 请求路径：`/order/one/key/scrm`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填); CorpId(string, 必填); LoginId(integer, 必填); LoginUserName(string, 必填); LoginOrgId(integer, 必填); Receiver(string, 必填, 收货人姓名); ReceiverPhoneId(string, 非必填, 收货人手机号（丝路phoneid）); ReceiverPhone(string, 非必填, 收货人手机号（真实手机号明文）); ReceiveAddress(object, 必填); Policies(array, 必填, 下单的政策商品集合); ReceiptMethod(integer, 非必填, 付款方式)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(null, 必填)]

#### 299. 订单下送WMS

- 所属模块：订单中心
- 请求方式：`POST`
- 请求路径：`/order/orders/wms/sendOrderToWmsByOrderId`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(null, 必填)]

#### 300. 当前制单人的待审订单的审单人

- 所属模块：订单中心
- 请求方式：`GET`
- 请求路径：`/reviewing/{userId}/reviewers`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `userId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 301. ERP签收

- 所属模块：订单中心
- 请求方式：`POST`
- 请求路径：`/service/xjservice`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[vbillcode(string, 必填); dbilldate(string, 必填); interfacetype(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 302. 退货通知ERP

- 所属模块：订单中心/ERP对接
- 请求方式：`POST`
- 请求路径：`/order/erp/return`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[AfterSaleDate(string, 必填, 退货日期 YYYY-MM-DD); AfterSaleCode(string, 必填, 退货工单单号); AfterSaleNote(string, 非必填, 退货工单备注); BatchNo(string, 必填, 订单批次号); ChargeMoney(number, 非必填, 充值金额); GoodList(array, 必填, 商品列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(boolean, 非必填, 响应数据)]

#### 303. 订单签收通知ERP

- 所属模块：订单中心/ERP对接
- 请求方式：`POST`
- 请求路径：`/order/sign/erp`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[BatchNo(string, 必填, 批次号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语); Data(object, 必填)]

#### 304. deleted

- 所属模块：订单中心/OrderPrinterFeeConfigController
- 请求方式：`POST`
- 请求路径：`/order/printer/config/deleted`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/OrderPrinterFeeConfigReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 305. detail

- 所属模块：订单中心/OrderPrinterFeeConfigController
- 请求方式：`GET`
- 请求路径：`/order/printer/config/detail/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABOrderPrinterFeeConfigRespVO%C2%BB

#### 306. page

- 所属模块：订单中心/OrderPrinterFeeConfigController
- 请求方式：`POST`
- 请求路径：`/order/printer/config/page`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/OrderPrinterFeeConfigReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABPageVO%C2%ABOrderPrinterFeeConfigRespVO%C2%BB%C2%BB

#### 307. save

- 所属模块：订单中心/OrderPrinterFeeConfigController
- 请求方式：`POST`
- 请求路径：`/order/printer/config/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/OrderPrinterFeeConfigReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 308. update

- 所属模块：订单中心/OrderPrinterFeeConfigController
- 请求方式：`POST`
- 请求路径：`/order/printer/config/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/OrderPrinterFeeConfigReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 309. 保存大单奖励折算赠品倍数(已废弃)

- 所属模块：订单中心/促销-奖励规则
- 请求方式：`POST`
- 请求路径：`/policy/reward`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ConversionTimes(number, 必填, 订单取消折算赠品倍数); RewardType(integer, 必填, 奖励类型 0:大单奖励;1:升级奖励)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息)]

#### 310. 查询小于大单奖励明细（已弃用）

- 所属模块：订单中心/促销-奖励规则
- 请求方式：`GET`
- 请求路径：`/policy/reward/all`
- 接口说明：调用方弃用：前端
- 鉴权方式：Authorization 请求头
- 缺失字段：request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `RewardType`：required=True，type=string，说明：奖励类型 0:大单奖励  1:升级奖励，示例：`Long`
- `Grade`：required=True，type=string，说明：档次，示例：`Long`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(array, 必填)]

#### 311. 查询政策配置列表

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `Name`：required=False，type=string，说明：政策名称，示例：`String`
- `DepartmentId`：required=False，type=string，说明：归属部门Id，示例：`String`
- `Status`：required=False，type=string，说明：启用状态  0:停用 1:启用，示例：`Long`
- `PageIndex`：required=True，type=string，说明：当前页数 从1开始，示例：`Long`
- `PageSize`：required=True，type=string，说明：每页显示条数 默认10条，示例：`Long`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 312. 批量停用/启用政策

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/batchStartOrStop`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[List(array, 必填); Status(number, 必填, 启用编码：0：停用，1：启用)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 313. 查询商品策略分类

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/category`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PolicyId`：required=True，type=string，说明：政策ID，示例：`1`
- `FirstCategoryId`：required=True，type=string，说明：政策一级分类ID，示例：`1`
- `PageIndex`：required=True，type=string，说明：页数，示例：`1`
- `PageSize`：required=True，type=string，说明：每页显示条数，示例：`1`
- `CategoryName`：required=False，type=string，说明：策略分类名称，示例：`asf`
- `StartTime`：required=False，type=string，说明：创建开始时间，示例：`2020-02-22 11:46:35`
- `EndTime`：required=False，type=string，说明：创建结束时间，示例：`2020-02-22 11:46:35`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 314. 保存商品策略分类

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/category`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PolicyId(number, 必填, 政策ID); FirstCategoryId(number, 必填, 政策一级分类ID); Name(string, 必填, 政策分类名称)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码  0:成功); Msg(string, 必填, 返回信息)]

#### 315. 删除商品策略分类

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/category/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 商品策略分类ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 316. 修改商品策略分类

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/category/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 商品策略分类ID); Name(string, 必填, 策略名称)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息)]

#### 317. 商品策略添加至某个策略分类

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/copyStrategy`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[StrategyCategoryId(number, 必填, 策略分类ID); StrategyList(array, 必填, 策略ID列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语)]

#### 318. 查询策略(es查询)

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/es/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `FictitiousGoodsId`：required=False，type=string，说明：虚拟商品ID，示例：`1`
- `PolicyId`：required=False，type=string，说明：政策ID，示例：`1`
- `Name`：required=False，type=string，说明：政策名称，示例：`www`
- `DepartmentId`：required=False，type=string，说明：部门ID，示例：`1`
- `Status`：required=False，type=string，说明：启用状态 0:停用 1:启用，示例：`1`
- `PageIndex`：required=False，type=string，说明：页数，示例：`1`
- `PageSize`：required=False，type=string，说明：每页显示条数，示例：`10`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回语); Data(object, 必填)]

#### 319. 查询政策额外加送

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/extra`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PolicyId`：required=True，type=string，说明：政策ID，示例：`Long`
- `PageIndex`：required=True，type=string，说明：页数 从1开始，示例：`Long`
- `PageSize`：required=True，type=string，说明：每页显示条数  默认10条，示例：`Long`
- `PolicyFirstCategoryId`：required=True，type=string，说明：政策一级分类ID，示例：`Long`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 320. 保存政策额外加送

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/extra`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PolicyId(number, 必填, 政策ID); PolicyFirstCategoryId(number, 必填, 政策一级分类ID); StartMoney(number, 必填, 订单应收开始金额); EndMoney(number, 必填, 订单应收结束金额); EnjoyUpgradeGift(number, 必填, 是否同时享受升级赠品 0:否 1:是); EnjoyFullGift(number, 必填, 是否同时享受满额赠品0:否 1:是); OptionalNumber(number, 必填, 任选数量)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 321. 查询额外加送产品

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/extra/goods`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PolicyExtraId`：required=True，type=string，说明：额外加送ID，示例：`Long`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语); Data(array, 必填, 返回值)]

#### 322. 保存额外加送产品

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/extra/goods`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PolicyExtraId(number, 必填, 额外加送ID); GoodsNumber(number, 必填, 商品数量); GoodsIds(array, 必填, 商品ID集合)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 323. 删除额外加送产品

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/extra/goods/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 额外加送商品ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 324. 复制上月升级赠品/满额赠品

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/other/copy`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DepartmentId(number, 必填, 部门ID); PolicyId(number, 必填, 本月政策ID); PolicyFirstCategoryId(number, 必填, 政策一级分类ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 325. 删除满额赠品/升级赠品/积分换购/免费领

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/other/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 其他政策配置ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 326. 保存满额赠品/升级赠品/积分换购/免费领

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/other/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PolicyId(number, 必填, 政策ID); PolicyFirstCategoryId(number, 必填, 政策一级分类ID); Number(number, 必填, 商品数量); GoodsIds(array, 必填, 商品ID集合); Grade(string, 非必填, 档次); UpgradeTypeId(number, 非必填, 升级类型ID); ConsumeIntegral(number, 非必填, 消耗积分); CustomerLevel(string, 非必填, 客户等级(Json){"id":1,"code":2,"name":"铜卡"})]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 327. 查询满额赠品/升级赠品/积分换购/免费领

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/other/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PolicyId`：required=True，type=string，说明：政策ID，示例：`Long`
- `PolicyFirstCategoryId`：required=True，type=string，说明：政策一级分类ID，示例：`Long`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语); Data(array, 必填, 返回值)]

#### 328. 新增政策

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Name(string, 必填, 政策名称); DepartmentId(integer, 必填, 归属部门ID); StartMonth(integer, 必填, 可用坐席开始工龄); EndMonth(integer, 必填, 可用坐席结束工龄); StartTime(string, 必填, 有效期结束时间); EndTime(string, 必填, 有效期结束时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 提示语); Data(number, 必填, 政策ID)]

#### 329. 停用/启用政策

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/startOrStop`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Status(number, 必填, 启用编码：0：停用，1：启用); Id(number, 必填, 政策ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 330. 查询商品策略名称列表

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/strategy`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PolicyId`：required=False，type=string，说明：政策ID，示例：`Long`
- `PolicyCategoryId`：required=False，type=string，说明：政策一级分类ID，示例：`Long`
- `PageIndex`：required=True，type=string，说明：页码，示例：`Long`
- `PageSize`：required=True，type=string，说明：每页最大记录数，示例：`Long`
- `StrategyName`：required=False，type=string，说明：策略名称，示例：`String`
- `DepartmentId`：required=False，type=string，说明：部门ID，示例：`Long`
- `StartTime`：required=False，type=string，说明：创建开始时间，示例：`String`
- `EndTime`：required=False，type=string，说明：创建结束时间，示例：`String`
- `StrategyCategoryId`：required=False，type=string，说明：策略分类ID，示例：`Long`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填, 返回码); Msg(string, 必填, 提示语); Data(object, 必填)]

#### 331. 删除商品策略

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/strategy/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 策略ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息)]

#### 332. 删除商品策略商品

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/strategy/goods/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[strategyGoodsId(number, 必填, 策略商品ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 333. 保存商品策略商品

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/strategy/goods/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[StrategyId(number, 必填, 策略iD); StrategyCategoryId(number, 必填, 政策分类ID); GoodsList(array, 必填, 商品列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 334. 查询商品策略商品

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/strategy/goods/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `StrategyId`：required=True，type=string，说明：商品策略ID，示例：`1`
- `StrategyCategoryId`：required=True，type=string，说明：政策分类ID，示例：`1`
- `SetMealGoodsType`：required=False，type=string，说明：套餐内商品类型 X,Y,Z，示例：`X`
- `Type`：required=False，type=string，说明：商品类型 1:主品  2:辅品，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(array, 必填)]

#### 335. 保存商品策略

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/strategy/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CreateSource`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Name(string, 必填, 商品策略名称); PolicyCategoryId(number, 必填, 政策一级分类ID); StrategyCategoryId(number, 必填, 策略分类ID); StrategyTypeId(number, 必填, 策略类型ID); CustomerLevel(string, 必填, 客户等级); LimitNumber(number, 必填, 客户限购个数); SingleLimit(number, 必填, 每单限购); StartTime(string, 必填, 客户限购开始时间); EndTime(string, 必填, 客户限购结束时间); IsControlReward(number, 必填, 是否控制员工奖励：0：否，1是); RewardLevel(string, 必填, 员工共奖励级别(Json)[{"id":1,"code":"1","name":"金卡"}]); RewardMoney(number, 必填, 员工奖励金额，单位：分); IsEnjoyMemberDiscount(number, 必填, 是否享受会员折扣0否1是); IsEnjoyExtraGifts(number, 必填, 是否享受额外赠品  0:否 1:是); IsEnjoyFullGift(number, 必填, 是否享受满额赠品  0:否 1:是); IsEnjoyUpGradeGifts(number, 必填, 是否享受升级赠品  0:否 1:是); ...其余 11 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(number, 必填, 策略ID)]

#### 336. 修改商品策略

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/strategy/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CreateSource`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PolicyId(integer, 必填, 所属政策Id); PolicyCategoryId(integer, 必填, 政策一级分类Id); Name(string, 必填, 商品策略名称); StrategyCategroyId(number, 必填, 策略分类Id); StrategyTypeId(number, 必填, 策略类型ID); CustomerBuyLimitNumber(number, 必填, 客户限购个数); CustomerBuyLimitStartTime(string, 必填, 客户限购开始时间); CustomerBuyLimitEndTime(string, 必填, 客户限购结束时间); EmployeeRewardLevel(string, 必填, 员工奖励级别); EmployeeRewardMoney(number, 必填, 员工奖励金额); IsEnjoyMemberDiscount(number, 必填, 是否享受会员折扣  0:否 1:是); IsEnjoyExtraGifts(number, 必填, 是否享受额外赠品  0:否 1:是); IsEnjoyFullGift(number, 必填, 是否享受满额赠品  0:否 1:是); IsEnjoyUpGradeGifts(number, 必填, 是否享受升级赠品  0:否 1:是); IsIncludedCompleteRate(number, 必填, 是否计入完成率  0:否 1:是); RoyaltyRate(number, 必填, 提成比例); ...其余 10 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息)]

#### 337. 查询商品策略详情

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/strategy/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `id`：required=True，type=string，说明：商品策略id，示例：`12`

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 338. 修改政策

- 所属模块：订单中心/促销-政策配置
- 请求方式：`POST`
- 请求路径：`/policy/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 非必填, 政策ID,修改时必填); Name(string, 必填, 政策名称); DepartmentId(integer, 必填, 归属部门ID); StartMonth(integer, 必填, 可用坐席开始工龄); EndMonth(integer, 必填, 可用坐席结束工龄); StartTime(string, 必填, 有效期结束时间); EndTime(string, 必填, 有效期结束时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 提示语)]

#### 339. 根据政策ID查询政策

- 所属模块：订单中心/促销-政策配置
- 请求方式：`GET`
- 请求路径：`/policy/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `id`：required=True，type=string，说明：政策Id，示例：`151`

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 340. 客户合并,礼券合并接口(MergeCustomerId客户礼券向CustomerId合并)

- 所属模块：订单中心/促销-礼券-客户合并
- 请求方式：`POST`
- 请求路径：`/policy/coupon/customer/merge`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填); MergeCustomerId(number, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回语); Data(array, 必填, 礼券ID集合)]

#### 341. 撤销订单使用礼券

- 所属模块：订单中心/促销-礼券流水
- 请求方式：`POST`
- 请求路径：`/coupon/flow/cancel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); CouponId(number, 必填, 礼券ID); OrderId(number, 必填, 订单ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语)]

#### 342. 查询礼券使用流水

- 所属模块：订单中心/促销-礼券流水
- 请求方式：`GET`
- 请求路径：`/policy/coupon/flow`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Type`：required=True，type=string，说明：0:根据客户ID查询 1:根据礼券ID查询  2:根据客户ID和礼券ID查询，示例：`0`
- `CouponId`：required=False，type=string，说明：礼券ID，示例：`1`
- `CustomerId`：required=False，type=string，说明：客户ID，示例：`1`
- `PageIndex`：required=True，type=string，说明：页数，示例：`1`
- `PageSize`：required=True，type=string，说明：每页显示条数，示例：`10`
- `StartTime`：required=False，type=string，说明：礼券失效开始时间
- `EndTime`：required=False，type=string，说明：礼券失效结束时间
- `Status`：required=False，type=string，说明：0:未使用 1:已使用  2:已过期 3已回收

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 343. 查询礼券使用流水历史记录

- 所属模块：订单中心/促销-礼券流水
- 请求方式：`GET`
- 请求路径：`/policy/coupon/flow/history`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Type`：required=True，type=string，说明：0:根据客户ID查询 1:根据礼券ID查询  2:根据客户ID和礼券ID查询，示例：`0`
- `CouponId`：required=False，type=string，说明：礼券ID，示例：`1`
- `CustomerId`：required=False，type=string，说明：客户ID，示例：`1`
- `PageIndex`：required=True，type=string，说明：页数，示例：`1`
- `PageSize`：required=True，type=string，说明：每页显示条数，示例：`10`
- `StartTime`：required=False，type=string，说明：礼券失效开始时间
- `EndTime`：required=False，type=string，说明：礼券失效结束时间
- `Status`：required=False，type=string，说明：0:未使用 1:已使用  2:已过期 3已回收

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 344. 保存礼券使用流水

- 所属模块：订单中心/促销-礼券流水
- 请求方式：`POST`
- 请求路径：`/policy/coupon/flow/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CouponId(number, 必填, 礼券ID); CouponRuleId(number, 必填, 礼券规则ID); CustomerId(number, 必填, 客户ID); UseNumber(number, 必填, 使用数量); OrderId(number, 必填, 下单ID); OrderCode(string, 必填, 下单编号); OrderTime(string, 必填, 下单时间); Remarks(string, 必填, 使用备注)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 345. 保存积分默认比值

- 所属模块：订单中心/促销-积分配置
- 请求方式：`POST`
- 请求路径：`/policy/integral/default`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/SaveIntegralDefaultRateReqVo

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 346. 删除积分配置

- 所属模块：订单中心/促销-积分配置
- 请求方式：`POST`
- 请求路径：`/policy/integral/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/DeletePolicyIntegralReqVo

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 347. 查询适合订单的积分配置

- 所属模块：订单中心/促销-积分配置
- 请求方式：`GET`
- 请求路径：`/policy/integral/order`
- 接口说明：「已废弃」2022-02-24 不再使用
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderMoney`：required=True，type=string，说明：订单金额，示例：`0`
- `upgradeType`：required=True，type=string，说明：升级类型 ( 0 未升级，1：满额升级 2：累计升级)，示例：`0`
- `levelId`：required=True，type=string，说明：下单后客户等级，示例：`0`
- `beforeOrderLevelId`：required=True，type=string，说明：下单前客户等级，示例：`0`
- `beforeCustomerAssetsId`：required=True，type=string，说明：无，示例：`0`
- `customerId`：required=True，type=string，说明：无，示例：`0`
- `isDeleted`：required=False，type=string，说明：无，示例：`0`
- `userId`：required=False，type=string，说明：无，示例：`0`
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无，示例：`0`
- `loginId`：required=False，type=string，说明：无，示例：`0`
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无，示例：`0`
- `businessType`：required=False，type=string，说明：无，示例：`0`
- `orgTypeId`：required=False，type=string，说明：无，示例：`0`
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无，示例：`0`
- `pageIndex`：required=False，type=string，说明：无，示例：`0`
- `pageSize`：required=False，type=string，说明：无，示例：`0`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(#/components/schemas/PolicyIntegralRespVo, 非必填)]

#### 348. 查询级别折扣

- 所属模块：订单中心/促销-级别折扣
- 请求方式：`GET`
- 请求路径：`/policy/leveldiscount`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `LevelId`：required=False，type=string，说明：级别折扣ID，示例：`Long`
- `Discount`：required=True，type=string，说明：折扣比例

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语); Data(array, 必填, 返回值)]

#### 349. 保存级别折扣

- 所属模块：订单中心/促销-级别折扣
- 请求方式：`POST`
- 请求路径：`/policy/leveldiscount`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[LevelId(number, 必填, 等级ID); Discount(number, 必填, 折扣)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 350. 删除级别折扣

- 所属模块：订单中心/促销-级别折扣
- 请求方式：`POST`
- 请求路径：`/policy/leveldiscount/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 级别折扣ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码 0:成功); Msg(string, 必填, 返回提示语)]

#### 351. 查询返券列表

- 所属模块：订单中心/促销-返券规则
- 请求方式：`GET`
- 请求路径：`/policy/rebate`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- `Type`：required=True，type=string，说明：返券类型 0:满额返券;1:升级返券，示例：`1`
- `Grade`：required=False，type=string，说明：档次  单位:分，示例：`1`
- `LevelId`：required=False，type=string，说明：等级级别ID
- `PageIndex`：required=True，type=string，说明：页数，示例：`1`
- `PageSize`：required=True，type=string，说明：每页显示条数，示例：`1`
- `ReturnMoney`：required=False，type=string，说明：返券金额，示例：`1`
- `DepartmentId`：required=False，type=string，说明：部门ID，示例：`1`
- `EffectDays`：required=False，type=string，说明：有效期（天）

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 352. 删除返券

- 所属模块：订单中心/促销-返券规则
- 请求方式：`POST`
- 请求路径：`/policy/rebate/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 必填, 返券ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息)]

#### 353. 新增满额返券

- 所属模块：订单中心/促销-返券规则
- 请求方式：`POST`
- 请求路径：`/policy/rebate/full`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Grade(integer, 必填, 档次 单位:分); ReturnMoney(integer, 必填, 返券金额 单位:分); EffectDays(number, 必填, 有效期(天)); DepartmentList(array, 必填, 部门ID集合)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息)]

#### 354. 查询适用订单返券列表

- 所属模块：订单中心/促销-返券规则
- 请求方式：`GET`
- 请求路径：`/policy/rebate/order`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- `Type`：required=True，type=string，说明：返券类型 0:满额返券;1:升级返券，示例：`1`
- `Grade`：required=False，type=string，说明：档次  单位:分  Type为0时传入，示例：`1`
- `LevelId`：required=False，type=string，说明：等级级别ID
- `ReturnMoney`：required=False，type=string，说明：返券金额  Type为1时可以传入，示例：`1`
- `DepartmentId`：required=True，type=string，说明：下单部门ID，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(array, 必填, 返回值)]

#### 355. 计算订单返券金额

- 所属模块：订单中心/促销-返券规则
- 请求方式：`POST`
- 请求路径：`/policy/rebate/order/count`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DepartmentId(number, 必填, 下单部门ID); OrderMoney(number, 必填, 订单应收金额 单位:分)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(number, 必填, 返券金额)]

#### 356. 新增升级返券

- 所属模块：订单中心/促销-返券规则
- 请求方式：`POST`
- 请求路径：`/policy/rebate/upgrade`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[LevelId(number, 必填, 客户升级级别ID); ReturnMoney(number, 必填, 返券金额 单位:分); EffectDays(number, 必填, 有效期 单位:天); DepartmentList(array, 必填, 部门ID列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息)]

#### 357. 出库订单查询 - 分页

- 所属模块：订单中心/出库订单
- 请求方式：`POST`
- 请求路径：`/order/otherout/select`
- 接口说明：出库订单查询 - 分页  入参与出参，各个字段首字母大写
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[isGlobal(integer, 非必填, 用户权限是否是全局); orderType(integer, 必填, 订单类型 30:员工自购，31:经销订单，32:快递理赔，33:内部领用，34:退换货订单); orderTypes(array, 必填, 订单类型 30:员工自购，31:经销订单，32:快递理赔，33:内部领用，34:退换货订单); orderSource(integer, 必填, 订单来源); code(string, 非必填, 订单号); statusList(array, 非必填, 订单状态); receiptMethodId(integer, 非必填, 收款方式); customerId(integer, 非必填, 客户Id); goodsId(integer, 非必填, 商品Id); amountMin(integer, 非必填, 订单金额 -开始 单位分); amountMax(integer, 非必填, 订单金额-结束 单位分); createTimeBegin(string, 非必填, 制单开始时间); createTimeEnd(string, 非必填, 制单结束时间); deliveryTimeBegin(string, 非必填, 发货开始时间); deliveryTimeEnd(string, 非必填, 发货结束时间); reviewStartTime(string, 非必填, 审单开始时间); ...其余 17 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 358. 分销商信息保存修改

- 所属模块：订单中心/分销商管理
- 请求方式：`POST`
- 请求路径：`/distribution/info/addOrEdit`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 非必填, 主键); ContactName(string, 必填, 联系人); DistributionName(string, 必填, 名称); Telephone(string, 必填, 电话); ProvinceId(integer, 必填, 省ID); CityId(integer, 必填, 市ID); DistrictId(integer, 必填, 区ID); StreetId(integer, 必填, 街道ID); AddressDetail(string, 必填, 地址详情); ProvinceName(string, 必填, 省名称); CityName(string, 必填, 市名称); DistrictName(string, 必填, 区名称); StreetName(string, 必填, 街道名称); FullAddress(string, 必填, 地址全称)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(null, 非必填)]

#### 359. 分销商信息查询

- 所属模块：订单中心/分销商管理
- 请求方式：`POST`
- 请求路径：`/distribution/info/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PageIndex(number, 必填); PageSize(number, 必填); DistributionName(string, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 360. 分销商库存查询

- 所属模块：订单中心/分销商管理
- 请求方式：`POST`
- 请求路径：`/distribution/info/select/stock`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PageIndex(number, 必填); PageSize(number, 必填); PlatformId(number, 非必填, 平台ID); ShopId(number, 非必填, 店铺ID); SkuCode(string, 非必填, 商品编码); Name(string, 非必填, 商品名称)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 361. 失败订单数据导出

- 所属模块：订单中心/分销商订单
- 请求方式：`POST`
- 请求路径：`/127.0.0.1/distribution/order/export`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[BatchId(integer, 必填)]

**返回体**

- `200`：无描述；`application/octet-stream` type=object; fields=[]

#### 362. 导入订单V2

- 所属模块：订单中心/分销商订单
- 请求方式：`POST`
- 请求路径：`/127.0.0.1/distribution/order/importOrders`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`multipart/form-data`
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[file(string, 必填); CreateSource(string, 必填, 操作人)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 363. 处理分销商订单

- 所属模块：订单中心/分销商订单
- 请求方式：`GET`
- 请求路径：`/127.0.0.1/distribution/order/push/handle`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description, request_body

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 364. 查询导入信息

- 所属模块：订单中心/分销商订单
- 请求方式：`POST`
- 请求路径：`/127.0.0.1/distribution/order/select/import`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[StartDate(string/null, 必填, 开始日期); EndDate(string/null, 必填, 结束日期)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 365. 获取订单总额(分销商制单)

- 所属模块：订单中心/分销商订单
- 请求方式：`POST`
- 请求路径：`/distribution/order/calculate/order/amount`
- 接口说明：分销商制单仅计算政策金额
- 鉴权方式：未声明/未识别
- 缺失字段：headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PolicyGoods(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(integer, 必填, 订单总额(单位:分))]

#### 366. 查询订单详情

- 所属模块：订单中心/分销商订单
- 请求方式：`GET`
- 请求路径：`/distribution/order/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=True，type=string，说明：订单ID，示例：`0`
- `EncryptionLogistics`：required=False，type=string，说明：物流单号加密，示例：`true`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 367. 结账单下载

- 所属模块：订单中心/分销商订单
- 请求方式：`GET`
- 请求路径：`/distribution/order/financial/download`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Code`：required=False，type=string，说明：订单编号
- `Receiver`：required=False，type=string，说明：收货人名称
- `GoodsId`：required=False，type=string，说明：商品Id，示例：`0`
- `PlatformId`：required=False，type=string，说明：平台id，示例：`0`
- `ShopId`：required=False，type=string，说明：店铺ID，示例：`0`
- `DeliveryCode`：required=False，type=string，说明：运单号
- `StatusList`：required=False，type=string，说明：订单状态
- `CreateTimeBegin`：required=False，type=string，说明：制单开始时间
- `CreateTimeEnd`：required=False，type=string，说明：制单结束时间
- `DeliveryTimeBegin`：required=False，type=string，说明：发货开始时间
- `DeliveryTimeEnd`：required=False，type=string，说明：发货结束时间
- `IsFinished`：required=False，type=string，说明：结账状态 : 0-未结账 ，1-已结账，示例：`0`
- `Ids`：required=False，type=string，说明：无，示例：`0`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 368. 财务结账

- 所属模块：订单中心/分销商订单
- 请求方式：`POST`
- 请求路径：`/distribution/order/financial/settle`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 非必填, 订单编号); Receiver(string, 非必填, 收货人名称); GoodsId(integer, 非必填, 商品Id); PlatformId(integer, 非必填, 平台id); ShopId(integer, 非必填, 店铺ID); DeliveryCode(string, 非必填, 运单号); StatusList(array, 非必填, 订单状态); CreateTimeBegin(string, 非必填, 制单开始时间); CreateTimeEnd(string, 非必填, 制单结束时间); DeliveryTimeBegin(string, 非必填, 发货开始时间); DeliveryTimeEnd(string, 非必填, 发货结束时间); IsFinished(integer, 非必填, 结账状态 : 0-未结账 ，1-已结账); Ids(array, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 369. 查询订单商品

- 所属模块：订单中心/分销商订单
- 请求方式：`GET`
- 请求路径：`/distribution/order/goods`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=True，type=string，说明：订单ID，示例：`0`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 370. 查询订单列表(对账单查询共用)

- 所属模块：订单中心/分销商订单
- 请求方式：`POST`
- 请求路径：`/distribution/order/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 非必填, 订单编号); Receiver(string, 非必填, 收货人名称); GoodsId(integer, 非必填, 商品Id); PlatformId(integer, 非必填, 平台id); ShopId(integer, 非必填, 店铺ID); DeliveryCode(string, 非必填, 运单号); StatusList(array, 非必填, 订单状态); CreateTimeBegin(string, 非必填, 制单开始时间); CreateTimeEnd(string, 非必填, 制单结束时间); DeliveryTimeBegin(string, 非必填, 发货开始时间); DeliveryTimeEnd(string, 非必填, 发货结束时间); SignStartTime(string, 非必填, 签收开始时间); SignEndTime(string, 非必填, 签收结束时间); IsFinished(integer, 非必填, 结账状态 : 0-未结账 ，1-已结账); UserOrgId(number, 非必填, 用户部门id，用于控制权限); QueryUserId(number, 非必填, 分销商订单查询用); ...其余 2 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 371. 查询的订单列表的物流信息导出

- 所属模块：订单中心/分销商订单
- 请求方式：`POST`
- 请求路径：`/distribution/order/list/logistic/export`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[code(string, 非必填, 订单编号); receiver(string, 非必填, 收货人名称); goodsId(integer, 非必填, 商品Id); platformId(integer, 非必填, 平台id); shopId(integer, 非必填, 店铺ID); deliveryCode(string, 非必填, 运单号); statusList(array, 非必填, 订单状态); createTimeBegin(string, 非必填, 制单开始时间); createTimeEnd(string, 非必填, 制单结束时间); deliveryTimeBegin(string, 非必填, 发货开始时间); deliveryTimeEnd(string, 非必填, 发货结束时间); isFinished(integer, 非必填, 结账状态 : 0-未结账 ，1-已结账); ids(array, 非必填); userOrgId(integer, 非必填); shopIds(array, 非必填, 店铺ids，用于控制数据权限); queryUserId(integer, 非必填); ...其余 17 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 372. 查询订单物流信息

- 所属模块：订单中心/分销商订单
- 请求方式：`GET`
- 请求路径：`/distribution/order/logistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=True，type=string，说明：订单ID，示例：`0`
- `EncryptionLogistics`：required=False，type=string，说明：物流单号加密，示例：`true`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 373. 订单状态数量统计

- 所属模块：订单中心/分销商订单
- 请求方式：`GET`
- 请求路径：`/distribution/order/status/statistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 374. 撤单

- 所属模块：订单中心/分销商订单
- 请求方式：`POST`
- 请求路径：`/distribution/order/user/cancel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填, 订单编号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 375. 新增

- 所属模块：订单中心/员工资源配置 Controller
- 请求方式：`POST`
- 请求路径：`/customerservice/media/config/add`
- 接口说明：新增
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[StaffLevel(integer, 必填, 员工层级); InGroupPeriod(integer, 非必填, 入组周期); CustomerCategory(integer, 必填, 资源类型); Threshold(integer, 必填, 分线数量)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 376. 列表查询

- 所属模块：订单中心/员工资源配置 Controller
- 请求方式：`GET`
- 请求路径：`/customerservice/media/config/all`
- 接口说明：列表查询
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 377. 删除

- 所属模块：订单中心/员工资源配置 Controller
- 请求方式：`POST`
- 请求路径：`/customerservice/media/config/delete`
- 接口说明：删除
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填, 配置id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 378. 根据批次号 导出失败订单数据

- 所属模块：订单中心/外部平台订单
- 请求方式：`POST`
- 请求路径：`/order/outplatform/exportExcel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Platform(string, 必填, 订单平台 0：京东 ，1：淘宝，2：天猫); BatchId(integer, 必填, excel处理批次号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 379. 外部平台导入订单excel（0：京东 ，1：淘宝，2：天猫）

- 所属模块：订单中心/外部平台订单
- 请求方式：`POST`
- 请求路径：`/order/outplatform/importExcel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`multipart/form-data`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[Excel(string, 必填, 导入的excel文件); Platform(string, 必填, 平台 0：京东 ，1：淘宝，2：天猫); ShopCode(string, 必填, 店铺code); CreateSource(string, 必填, 导入操作人)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 380. 第三方订单制单失败-可处理订单平台

- 所属模块：订单中心/外部平台订单
- 请求方式：`GET`
- 请求路径：`/order/outplatform/qryAllPlatform`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 381. 查询所有导入数据结果集

- 所属模块：订单中心/外部平台订单
- 请求方式：`POST`
- 请求路径：`/order/outplatform/qryImportResult`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Platform(string, 必填, 订单平台 0：京东 ，1：淘宝，2：天猫); PageIndex(integer, 必填); PageSize(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 382. 查询外部平台店铺信息

- 所属模块：订单中心/外部平台订单
- 请求方式：`GET`
- 请求路径：`/order/outplatform/qryShopInfo`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 383. 查询第三方订单查询失败的订单

- 所属模块：订单中心/外部平台订单
- 请求方式：`POST`
- 请求路径：`/order/outplatform/queryFailList`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Platform(number, 非必填, 订单平台 0：京东 ，1：淘宝，2：天猫 3：抖音 4：有赞); OrderId(string, 非必填, 第三方外部订单编号); HandleResult(string, 非必填, 失败原因); StartTime(string, 非必填, 起始时间); EndTime(string, 非必填, 结束时间); PageIndex(number, 非必填, 起始页); PageSize(number, 非必填, 一页多少条)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 384. 外部订单重新制单

- 所属模块：订单中心/外部平台订单
- 请求方式：`POST`
- 请求路径：`/order/outplatform/queue/add`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Platform(string, 必填, 订单平台 0：京东 ，1：淘宝，2：天猫 3：抖音 4：有赞); PushIdList(array, 必填, 订单主键 集合)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 385. 分页查询 - 区域地址信息映射

- 所属模块：订单中心/外部订单地址差异映射.
- 请求方式：`GET`
- 请求路径：`/order/area/diff`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Source`：required=True，type=string，说明：地址所属外部平台id，示例：`0`
- `OuterProvince`：required=True，type=string，说明：外部平台区域 - 省，示例：`""`
- `OuterCity`：required=True，type=string，说明：外部平台区域 - 市，示例：`""`
- `OuterDistrict`：required=True，type=string，说明：外部平台区域 - 区，示例：`""`
- `InnerProvince`：required=True，type=string，说明：内部平台区域 - 省，示例：`""`
- `InnerCity`：required=True，type=string，说明：内部平台区域 - 市，示例：`""`
- `InnerDistrict`：required=True，type=string，说明：内部平台区域 - 区，示例：`""`
- `PageIndex`：required=True，type=string，说明：无，示例：`1`
- `PageSize`：required=True，type=string，说明：无，示例：`10`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 386. 创建一个地址区域映射

- 所属模块：订单中心/外部订单地址差异映射.
- 请求方式：`POST`
- 请求路径：`/order/area/diff`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Source(integer, 必填, 地址所属外部平台id); OuterProvince(string, 必填, 外部平台区域 - 省); OuterCity(string, 必填, 外部平台区域 - 市); OuterDistrict(string, 必填, 外部平台区域 - 区); OuterStreet(string, 必填, 外部平台区域 - 街道); InnerProvince(string, 必填, 内部平台区域 - 省); InnerCity(string, 必填, 内部平台区域 - 市); InnerDistrict(string, 必填, 内部平台区域 - 区); CreateSource(string, 非必填); InnerProvinceId(integer, 必填, 内部平台区域 - 省Id); InnerCityId(integer, 必填, 内部平台区域 - 市Id); InnerDistrictId(integer, 必填, 内部平台区域 - 区Id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 387. 删除一个已存在的地址区域映射

- 所属模块：订单中心/外部订单地址差异映射.
- 请求方式：`POST`
- 请求路径：`/order/area/diff/delete/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 388. 修改一个已存在的地址区域映射

- 所属模块：订单中心/外部订单地址差异映射.
- 请求方式：`POST`
- 请求路径：`/order/area/diff/modify/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Source(integer, 必填, 地址所属外部平台id); OuterProvince(string, 必填, 外部平台区域 - 省); OuterCity(string, 必填, 外部平台区域 - 市); OuterDistrict(string, 必填, 外部平台区域 - 区); OuterStreet(string, 必填, 外部平台区域 - 街道); InnerProvince(string, 必填, 内部平台区域 - 省); InnerCity(string, 必填, 内部平台区域 - 市); InnerDistrict(string, 必填, 内部平台区域 - 区); UpdateSource(string, 非必填); InnerProvinceId(string, 必填, 内部平台区域-省Id); InnerCityId(string, 必填, 内部平台区域 - 市Id); InnerDistrictId(string, 必填, 内部平台区域 - 区Id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 389. 审单配置 必审规则 详情

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`GET`
- 请求路径：`/order/examine/detail`
- 接口说明：审单配置 必审规则 详情
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=True，type=string，说明：必审规则id

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(object, 非必填, 响应数据)]

#### 390. 审单配置 必审规则 商品列表

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`GET`
- 请求路径：`/order/examine/goods`
- 接口说明：审单配置 必审规则 商品列表
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Code`：required=False，type=string，说明：商品编码
- `Name`：required=False，type=string，说明：商品名称
- `Id`：required=True，type=string，说明：审核配置规则ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 非必填)]

#### 391. 审单配置 必审规则 列表

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`GET`
- 请求路径：`/order/examine/page`
- 接口说明：审单配置 必审规则 列表
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `PageIndex`：required=True，type=string，说明：页码，示例：`1`
- `PageSize`：required=True，type=string，说明：页尺寸，示例：`10`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 非必填)]

#### 392. 审单配置 必审规则 新增

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`POST`
- 请求路径：`/order/examine/save`
- 接口说明：审单配置 必审规则 新增
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[RejectionTimes(integer, 必填, 客户连续拒收次数); CustomerGradeList(array, 非必填, 下单前客户级别); StartDays(integer, 非必填, 坐席工龄（起）); EndDays(integer, 非必填, 坐席工龄（止）); GoodsList(array, 非必填, 必审商品); StartTime(string, 必填, 启用时间（起）); EndTime(string, 必填, 启用时间（止）); DepartmentList(array, 非必填, 下单部门集合); CustomerAssetsType(integer, 非必填, 客户类型ID); StartOrderMoney(integer, 非必填, 订单应收金额（起）); EndOrderMoney(integer, 非必填, 订单应收金额（止）); UserList(array, 非必填, 必审坐席); SegmentationId(number, 非必填, 必审标签ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填, 响应码); Msg(string, 非必填, 响应消息)]

#### 393. 审单配置 必审规则 启用

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`POST`
- 请求路径：`/order/examine/start`
- 接口说明：审单配置 必审规则 启用
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 响应码); Msg(string, 必填, 响应消息)]

#### 394. 审单配置 必审规则 停用

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`POST`
- 请求路径：`/order/examine/stop`
- 接口说明：审单配置 必审规则 停用
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填, 审单配置ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 响应码); Msg(string, 必填, 响应消息)]

#### 395. 审单配置 必审规则 修改

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`POST`
- 请求路径：`/order/examine/update`
- 接口说明：审单配置 必审规则 修改
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填); DepartmentList(array, 非必填, 下单部门集合); CustomerGradeList(array, 非必填, 下单前客户级别); GoodsList(array, 非必填, 必审商品); UserList(array, 非必填, 必审坐席); StartDays(integer, 非必填, 坐席工龄（起）); EndDays(integer, 非必填, 坐席工龄（止）); StartOrderMoney(integer, 非必填, 订单应收开始金额); EndOrderMoney(integer, 非必填, 订单应收结束金额); StartTime(string, 必填, 启用时间（起）); EndTime(string, 必填, 启用时间（止）); CustomerAssetsType(integer, 非必填, 客户类型ID); RejectionTimes(integer, 非必填, 客户连续拒收次数); SegmentationId(number, 非必填, 必审标签ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填)]

#### 396. 审单配置 必审标签 列表

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`GET`
- 请求路径：`/order/segmentation/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(array, 非必填, 响应数据)]

#### 397. 审单配置 必审标签 添加

- 所属模块：订单中心/审单配置 必审规则
- 请求方式：`POST`
- 请求路径：`/order/segmentation/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[SegmentationIdList(array, 非必填, 标签id集合)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应信息); Data(boolean, 非必填, 处理结果)]

#### 398. 审单配置 删除

- 所属模块：订单中心/审单配置 自取审单/经理补贴
- 请求方式：`POST`
- 请求路径：`/order/review/config/delete/{id}`
- 接口说明：审单配置 删除
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `id`：required=True，type=string，说明：删除数据id，示例：`1`

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填, 响应码); Msg(string, 非必填, 响应消息)]

#### 399. 审单配置 经理补贴 查额度

- 所属模块：订单中心/审单配置 自取审单/经理补贴
- 请求方式：`POST`
- 请求路径：`/order/review/config/querySubsidy`
- 接口说明：审单配置 经理补贴 查询额度
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 响应码); Msg(string, 必填, 响应消息); Data(number, 必填, 经理补贴额度（元）)]

#### 400. 审单配置 经理补贴 根据部门查额度

- 所属模块：订单中心/审单配置 自取审单/经理补贴
- 请求方式：`GET`
- 请求路径：`/order/review/config/quota/{departmentId}`
- 接口说明：审单配置 经理补贴 查询额度
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `departmentId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 响应码); Msg(string, 必填, 响应消息); Data(number, 必填, 经理补贴额度（分）)]

#### 401. 审单配置 经理补贴 查修改记录

- 所属模块：订单中心/审单配置 自取审单/经理补贴
- 请求方式：`GET`
- 请求路径：`/order/review/config/records`
- 接口说明：审单配置 经理补贴 修改记录列表
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `reviewConfigId`：required=True，type=string，说明：经理补贴配置id，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 非必填)]

#### 402. 审单配置 经理补贴 新增/修改

- 所属模块：订单中心/审单配置 自取审单/经理补贴
- 请求方式：`POST`
- 请求路径：`/order/review/config/subsidy/save`
- 接口说明：审单配置 经理补贴 新增/修改
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 非必填, id); UserIds(string, 必填, 用户id); FromDeptId(string, 必填, 组织架构id); SubsidyAmount(integer, 必填, 补贴金额（分）); Type(integer, 必填, 配置类型（1经理补贴）); Remark(string/null, 非必填, 备注)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 响应码); Msg(string, 必填, 响应消息)]

#### 403. 审单配置 列表

- 所属模块：订单中心/审单配置 自取审单/经理补贴
- 请求方式：`POST`
- 请求路径：`/review/config/page`
- 接口说明：审单配置 列表查询
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Type(integer, 必填, 配置类型 0自取审单 1经理补贴); PageIndex(integer, 必填, 页码); PageSize(integer, 必填, 页尺寸)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 404. 审单配置 自取审单 新增/修改

- 所属模块：订单中心/审单配置 自取审单/经理补贴
- 请求方式：`POST`
- 请求路径：`/review/config/taking/save`
- 接口说明：审单配置 自取配置 新增/修改
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 非必填, id); UserIds(string, 必填, 用户ids（逗号拼接）); FromDeptId(string, 必填, 组织架构id（逗号拼接）); Num(integer, 必填, 每次自取条数); OrderTypes(integer, 必填, 订单类型); Type(integer, 必填, 配置类型（0自取审单）)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填, 响应码); Msg(string, 非必填, 响应消息)]

#### 405. 查询符合当前订单的礼券

- 所属模块：订单中心/政策-订单验证
- 请求方式：`POST`
- 请求路径：`/policy/validate/coupon`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); DepartmentId(number, 必填, 下单人最底层部门ID); GoodsList(array, 必填, 下单商品); OrderMoney(number, 必填, 订单金额 单位:分); EmployeeId(number, 必填, 下单人ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(array, 必填, 返回值)]

#### 406. 查询符合订单商品的策略

- 所属模块：订单中心/政策-订单验证
- 请求方式：`POST`
- 请求路径：`/policy/validate/strategy`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CreateSource`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DepartmentId(number, 必填, 坐席最底层部门ID); WorkMonth(number, 必填, 坐席工龄 单位:月份); GoodsList(array, 必填, 商品列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(array, 必填)]

#### 407. 服务费配置-新增

- 所属模块：订单中心/服务费配置
- 请求方式：`POST`
- 请求路径：`/order/config/service/add`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PolicyId(number, 必填, 政策ID); GoodsId(number, 必填, 商品ID); SkuCode(string, 必填, Sku编码); Quantity(number, 必填, 数量); SharePrice(number, 必填, 享佳价 单位:分); PayPrice(number, 必填, 支付价格 单位:分); IsJoinFinancialGoal(number, 必填, 是否参与财务目的计算  0:否 1:是); IsJoinRealGoal(number, 必填, 是否参与实际目的计算  0:否 1:是); Proportion(number, 必填, 比例 1-100); Level(number, 必填, 级别)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(null, 非必填, 响应数据)]

#### 408. 服务费配置-删除

- 所属模块：订单中心/服务费配置
- 请求方式：`POST`
- 请求路径：`/order/config/service/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 非必填, Id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(null, 非必填, 响应数据)]

#### 409. 服务费配置-分页查询

- 所属模块：订单中心/服务费配置
- 请求方式：`POST`
- 请求路径：`/order/config/service/page`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PolicyId(number, 非必填, 政策Id); SkuCode(string, 非必填, Sku编码)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(object, 非必填, 响应数据)]

#### 410. 服务费配置-修改

- 所属模块：订单中心/服务费配置
- 请求方式：`POST`
- 请求路径：`/order/config/service/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 非必填, Id); PolicyId(number, 非必填, 政策ID); GoodsId(number, 非必填, 商品ID); SkuCode(string, 非必填, Sku编码); Quantity(number, 非必填, 数量); SharePrice(number, 非必填, 享佳价 单位:分); PayPrice(number, 非必填, 支付价格 单位:分); IsJoinFinancialGoal(number, 非必填, 是否参与财务目的计算  0:否 1:是); IsJoinRealGoal(number, 非必填, 是否参与实际目的计算  0:否 1:是); Proportion(number, 非必填, 比例); Level(number, 非必填, 级别)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(null, 非必填, 响应数据)]

#### 411. 首页

- 所属模块：订单中心/测试接口
- 请求方式：`GET`
- 请求路径：`/`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, request_body

**请求头**

- `Proxy-Connection`：required=True，type=string，说明：无，示例：`keep-alive`
- `Upgrade-Insecure-Requests`：required=True，type=string，说明：无，示例：`1`
- `User-Agent`：required=True，type=string，说明：无，示例：***已脱敏***
- `Accept`：required=True，type=string，说明：无，示例：***已脱敏***
- `Accept-Encoding`：required=True，type=string，说明：无，示例：`gzip, deflate`
- `Accept-Language`：required=True，type=string，说明：无，示例：`zh-CN,zh;q=0.9`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 412. 登录

- 所属模块：订单中心/测试接口
- 请求方式：`POST`
- 请求路径：`/Account/Login`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Proxy-Connection`：required=True，type=string，说明：无，示例：`keep-alive`
- `Content-Length`：required=True，type=string，说明：无，示例：`92`
- `Accept`：required=True，type=string，说明：无，示例：`application/json, text/javascript, */*; q=0.01`
- `Origin`：required=True，type=string，说明：无，示例：`http://192.168.70.142:10090`
- `X-Requested-With`：required=True，type=string，说明：无，示例：`XMLHttpRequest`
- `User-Agent`：required=True，type=string，说明：无，示例：***已脱敏***
- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Accept-Encoding`：required=True，type=string，说明：无，示例：`gzip, deflate`
- `Accept-Language`：required=True，type=string，说明：无，示例：`zh-CN,zh;q=0.9`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[usernameOrEmailAddress(string, 必填); password(string, 必填); rememberMe(boolean, 必填); returnUrlHash(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 413. 顺丰

- 所属模块：订单中心/测试接口
- 请求方式：`POST`
- 请求路径：`/http://192.168.70.81:40001/mock/46/logistics/receive/sf`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[content(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 414. 同步德邦路由信息

- 所属模块：订单中心/测试接口
- 请求方式：`POST`
- 请求路径：`/logistics/receive/deppon_1576817912202`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/x-www-form-urlencoded`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[params(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 415. 同步EMS信息_测试场景1描述

- 所属模块：订单中心/测试接口
- 请求方式：`POST`
- 请求路径：`/logistics/receive/ems_1576725632133`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[listexpressmail(array, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[response(object, 非必填)]

#### 416. 详情

- 所属模块：订单中心/消费限额
- 请求方式：`GET`
- 请求路径：`/order/config/consumable/monthly/detail/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 417. 修改

- 所属模块：订单中心/消费限额
- 请求方式：`POST`
- 请求路径：`/order/config/consumable/monthly/edit`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填); SegmentationId(integer, 必填); SegmentationName(string, 必填); Remark(string, 必填); DetailList(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(null, 必填)]

#### 418. 新增

- 所属模块：订单中心/消费限额
- 请求方式：`POST`
- 请求路径：`/order/config/consumable/monthly/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[SegmentationId(integer, 必填); SegmentationName(string, 必填); Remark(string, 必填); DetailList(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(null, 必填)]

#### 419. 同步德邦路由信息(参照logistics_dp表)

- 所属模块：订单中心/物流-同步路由
- 请求方式：`POST`
- 请求路径：`/logistics/receive/deppon`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[TrackList(object, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 420. 同步EMS路由信息(参照logistics_ems表)

- 所属模块：订单中心/物流-同步路由
- 请求方式：`POST`
- 请求路径：`/logistics/receive/ems`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[listexpressmail(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[response(object, 非必填)]

#### 421. 同步顺丰路由信息(参照logistics_sf表)

- 所属模块：订单中心/物流-同步路由
- 请求方式：`POST`
- 请求路径：`/logistics/receive/sf`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=array; items=(type=object; fields=[mailId(string, 必填, 路由编号，每一个id代表一条不同的路由); mailNo(string, 必填, 运单号); orderId(string, 必填, 订单号); acceptTime(string, 必填, 路由产生时间); acceptAddress(string, 必填, 路由发生时间); opCode(string, 必填, 操作码); remark(string, 必填, 详细描述)])

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 422. 根据运单号查询杂志路由信息

- 所属模块：订单中心/物流-同步路由
- 请求方式：`GET`
- 请求路径：`/logistics/track/mail/{mailNo}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `mailNo`：required=True，type=string，说明：运单号

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回提示语); Data(object, 必填, 返回值)]

#### 423. 批量确认收款

- 所属模块：订单中心/确认收款 Controller
- 请求方式：`POST`
- 请求路径：`/order/confirm/batch/fund`
- 接口说明：批量确认收款
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[logisticsCodes(array, 非必填, 运单号); codes(array, 非必填, 订单编号); customerCode(string, 非必填, 客户编号); customerId(integer, 非必填, 客户id); handleStatus(integer, 非必填, 是否处理 1未处理 2已处理); status(integer, 非必填, 订单状态); orderType(integer, 非必填, 订单类型); payWay(integer, 非必填, 支付方式); makerId(integer, 非必填, 制单人id); createTimeBegin(string, 非必填, 制单时间（起）); createTimeEnd(string, 非必填, 制单时间（止）); ids(array, 非必填, 订单id); type(integer, 非必填, 订单类型); orderIdList(array, 非必填, 订单类型); isDeleted(integer, 非必填); userId(integer, 非必填); ...其余 13 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 424. 列表查询

- 所属模块：订单中心/确认收款 Controller
- 请求方式：`POST`
- 请求路径：`/order/confirm/page`
- 接口说明：列表查询  ```   1　支付邮寄运费是指财务支付给快递公司的运费   2　确认预存：针对单笔订单，已结案的确认预存按钮置灰不可操作   3　记录确认预存的人   4  按钮说明：        批量确认收款：如果有已收的订单不再重复已收。已收的订单，仍可跟单，变为拒收。记录处理确认收款的人 ```
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[logisticsCodes(array, 非必填, 运单号); codes(array, 非必填, 订单编号); customerCode(string, 非必填, 客户编号); customerId(integer, 非必填, 客户id); handleStatus(integer, 非必填, 是否处理 1未处理 2已处理); status(integer, 非必填, 订单状态); orderType(integer, 非必填, 订单类型); payWay(integer, 非必填, 支付方式); makerId(integer, 非必填, 制单人id); createTimeBegin(string, 非必填, 制单时间（起）); createTimeEnd(string, 非必填, 制单时间（止）); ids(array, 非必填, 订单id); type(integer, 非必填, 订单类型); orderIdList(array, 非必填, 订单类型); isDeleted(integer, 非必填); userId(integer, 非必填); ...其余 13 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 425. 确认预存

- 所属模块：订单中心/确认收款 Controller
- 请求方式：`POST`
- 请求路径：`/order/confirm/pre`
- 接口说明：确认预存
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[id(integer, 必填); isDeleted(integer, 非必填); userId(integer, 非必填); userName(string, 非必填); orgId(integer, 非必填); loginId(integer, 非必填); loginUserName(string, 非必填); loginOrgId(integer, 非必填); userAccount(string, 非必填); createSource(string, 非必填); createTime(string, 非必填); updateSource(string, 非必填); updateTime(string, 非必填); total(integer, 非必填); pageIndex(integer, 非必填); pageSize(integer, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 426. 确认返券

- 所属模块：订单中心/确认收款 Controller
- 请求方式：`POST`
- 请求路径：`/order/confirm/rebate`
- 接口说明：确认返券
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[id(integer, 必填); isDeleted(integer, 非必填); userId(integer, 非必填); userName(string, 非必填); orgId(integer, 非必填); loginId(integer, 非必填); loginUserName(string, 非必填); loginOrgId(integer, 非必填); userAccount(string, 非必填); createSource(string, 非必填); createTime(string, 非必填); updateSource(string, 非必填); updateTime(string, 非必填); total(integer, 非必填); pageIndex(integer, 非必填); pageSize(integer, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 427. token创建

- 所属模块：订单中心/聚水潭系统
- 请求方式：`GET`
- 请求路径：`/datascraping/jushuitan/createToken`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `code`：required=False，type=string，说明：无，示例：`12345`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 428. 取消订单--测试

- 所属模块：订单中心/聚水潭系统
- 请求方式：`GET`
- 请求路径：`/datascraping/jushuitan/order/cancel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 429. 推送聚水潭订单发货

- 所属模块：订单中心/聚水潭系统
- 请求方式：`POST`
- 请求路径：`/datascraping/jushuitan/order/delivery`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 430. 获取销售出库订单--测试

- 所属模块：订单中心/聚水潭系统
- 请求方式：`POST`
- 请求路径：`/datascraping/jushuitan/order/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 431. 发货查询--测试

- 所属模块：订单中心/聚水潭系统
- 请求方式：`POST`
- 请求路径：`/datascraping/jushuitan/order/logistic/query`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 432. 订单推送-已付款

- 所属模块：订单中心/聚水潭系统
- 请求方式：`POST`
- 请求路径：`/datascraping/jushuitan/order/upload`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 433. 订阅聚水潭发货通知

- 所属模块：订单中心/聚水潭系统
- 请求方式：`POST`
- 请求路径：`/order/jushuitan/oldCallback`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `ts`：required=False，type=string，说明：无，示例：`1743504568`
- `partnerid`：required=False，type=string，说明：无，示例：`erp`
- `method`：required=False，type=string，说明：无，示例：`logistics.upload`
- `sign`：required=False，type=string，说明：无，示例：`34225252`

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 434. 筛选已下单的客户id

- 所属模块：订单中心/订单
- 请求方式：`POST`
- 请求路径：`/order/check/customer`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=array; items=(type=number)

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 响应码); Msg(string, 必填, 响应消息); Data(array, 必填, 响应数据)]

#### 435. 获取运费配置

- 所属模块：订单中心/订单
- 请求方式：`GET`
- 请求路径：`/order/getFreight`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderSource`：required=True，type=string，说明：订单来源

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(number, 非必填, 运费（分）)]

#### 436. 获取订单来源

- 所属模块：订单中心/订单
- 请求方式：`GET`
- 请求路径：`/order/getOrderSource`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(number, 必填)]

#### 437. 订单运单号导入EXCEL

- 所属模块：订单中心/订单
- 请求方式：`POST`
- 请求路径：`/order/importDeliveryExcel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`multipart/form-data`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `multipart/form-data`：type=object; fields=[file(string, 必填, 导入的excel文件); CreateSource(string, 必填, 导入操作人)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 438. 查询离职员工订单列表

- 所属模块：订单中心/订单
- 请求方式：`POST`
- 请求路径：`/order/list/employee/lz`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(number, 非必填, 商品编号); StatusList(array, 非必填, 订单状态列表); StatusNames(array, 非必填, 订单状态名称列表); DeliveryCode(string, 非必填, 运单号); CustomerId(number, 非必填, 客户ID); GoodsId(number, 非必填, 商品ID); AmountMin(number, 非必填, 订单开始金额 单位:分); AmountMax(number, 非必填, 订单结束金额 单位:分); CreateTimeBegin(string, 非必填, 制单开始金额); CreateTimeEnd(string, 非必填, 制单结束金额); DeliveryTimeBegin(string, 非必填, 发货开始时间); DeliveryTimeEnd(string, 非必填, 发货结束时间); IsNormalOrder(number, 非必填, 是否正常订单 0:否 1；是); IsSelf(number, 非必填, 与我相关 0-否 1-是); UserId(number, 非必填, 下单人ID); ReviewerId(number, 非必填, 审单人ID); ...其余 8 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 439. 第三方订单查询

- 所属模块：订单中心/订单
- 请求方式：`POST`
- 请求路径：`/order/list/outer`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[PlatFormId(integer, 非必填, 平台id); ShopName(string, 非必填, 店铺名称); ShopOrderCode(string, 非必填, 店铺单号); OrderCode(string, 非必填, 丝路订单号); LogisticCode(string, 非必填, 运单号); StatusList(array, 非必填, 订单状态); DeliveryTimeStart(string, 非必填, 发货时间开始); DeliveryTimeEnd(string, 非必填, 发货时间结束); OrderTimeStart(string, 必填, 制单时间开始); OrderTimeEnd(string, 必填, 制单时间结束); RepealTimeStart(string, 非必填, 撤单时间开始); RepealTimeEnd(string, 非必填, 撤单时间结束); PageIndex(integer, 必填); PageSize(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 440. 打印出库单

- 所属模块：订单中心/订单
- 请求方式：`POST`
- 请求路径：`/order/orders/wms/printOutOrder`
- 接口说明：接口，返回值首字母大写
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 441. 获取第三方平台

- 所属模块：订单中心/订单
- 请求方式：`GET`
- 请求路径：`/order/outer/platforms`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(array, 非必填)]

#### 442. 预售订单坐席确认

- 所属模块：订单中心/订单
- 请求方式：`POST`
- 请求路径：`/order/pre-sale-order/{orderCode}/confirm`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderCode`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 443. 撤销订单失败

- 所属模块：订单中心/订单
- 请求方式：`POST`
- 请求路径：`/order/revoke/fail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[oderCode(string, 必填); errorMessage(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 444. 统计查询订单列表的现金、充值、消费、大单奖励、产品奖励

- 所属模块：订单中心/订单
- 请求方式：`POST`
- 请求路径：`/order/statistic`
- 接口说明：统计查询订单列表的现金、充值、消费、大单奖励、产品奖励
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[code(string, 非必填, 订单编号); statusList(array, 非必填, 订单状态); deliveryCode(string, 非必填, 运单号); customerId(integer, 非必填, 客户Id); goodsId(integer, 非必填, 商品Id); amountMin(integer, 非必填, 订单金额 -开始); amountMax(integer, 非必填, 订单金额-结束); createTimeBegin(string, 非必填, 制单开始时间); createTimeEnd(string, 非必填, 制单结束时间); deliveryTimeBegin(string, 非必填, 发货开始时间); deliveryTimeEnd(string, 非必填, 发货结束时间); isNormalOrder(integer, 非必填, 是否正常订单 0:否 1；是); normalStatus(array, 非必填, 正常订单状态列表); isSelf(integer, 非必填, 与我相关 0-否 1-是); reviewerId(string, 非必填, 审单人ID); reviewStartTime(string, 非必填, 审单开始时间); ...其余 28 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 445. 查询客户最近一年丝路销售订单记录

- 所属模块：订单中心/订单
- 请求方式：`GET`
- 请求路径：`/order/{customerId}/recentYear`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `customerId`：required=True，type=string，说明：无，示例：`10053`

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填, true 最近一年客户有丝路销售订单记录 反之 false)]

#### 446. 订单部门转移

- 所属模块：订单中心/订单-OA
- 请求方式：`POST`
- 请求路径：`/order/user/transfer/department`
- 接口说明：新增
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[FromDepartmentId(number, 非必填, 原部门); ToDepartmentId(number, 非必填, 新部门); OperatorName(string, 非必填, 操作人); BeginTime(string, 非必填, 调整周期范围开始时间); EndTime(string, 非必填, 调整周期范围结束时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 447. 获取坐席名下已发货未结案订单

- 所属模块：订单中心/订单-微信
- 请求方式：`POST`
- 请求路径：`/order/get/user/finish/orders`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[UserId(number, 必填, 客户ID); PageIndex(number, 非必填, 页数 默认1); StatusList(array, 必填); PageSize(number, 非必填, 每页显示条数 默认10)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息); Data(array, 非必填, 返回值)]

#### 448. 微信订单详情

- 所属模块：订单中心/订单-微信
- 请求方式：`GET`
- 请求路径：`/order/wx/order/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=True，type=string，说明：订单ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填, 返回值)]

#### 449. 微信查询订单列表

- 所属模块：订单中心/订单-微信
- 请求方式：`POST`
- 请求路径：`/order/wx/order/list`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); StatusList(array, 非必填, 订单状态列表); StartTime(string, 非必填, 制单开始时间(默认查三个月内)); EndTime(string, 非必填, 制单结束时间); PageIndex(number, 非必填, 页数 默认1); PageSize(number, 非必填, 每页显示条数 默认10)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息); Data(array, 非必填, 返回值)]

#### 450. 物流撤单

- 所属模块：订单中心/订单-物流撤单
- 请求方式：`POST`
- 请求路径：`/order/logistics/cancel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCodeList(array, 非必填, 订单编号列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息)]

#### 451. 更换承运商

- 所属模块：订单中心/订单-物流撤单
- 请求方式：`POST`
- 请求路径：`/order/logistics/changeLogistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(number, 必填, 订单id); CarrierId(number, 必填, 承运商id); LogisticsCode(string, 必填, 运单号)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息)]

#### 452. 批量撤单

- 所属模块：订单中心/订单-物流撤单
- 请求方式：`POST`
- 请求路径：`/order/orders/cancel/logistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderIds(number, 必填, 需要撤单的订单id集合); Remarks(string, 必填, 撤单备注)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 错误码); Msg(string, 必填, 错误信息); List(object, 必填, 撤单成功的订单id)]

#### 453. 物流撤单查询

- 所属模块：订单中心/订单-物流撤单
- 请求方式：`POST`
- 请求路径：`/order/orders/logistics/cancel`
- 接口说明：该接口查询的是销售订单中订单状态为待发货的订单，查询条件对这些进行过滤。订单状态 29 为销售订单
- 鉴权方式：Authorization 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 非必填, 订单号); CustomerCode(string, 非必填, 客户编号); CustomerName(string, 非必填, 客户姓名); BelongUserId(number, 非必填, 所属坐席id); CreateTimeBegin(string, 非必填, 制单时间左区间); CreateTimeEnd(string, 非必填, 制单时间右区间); AmountMin(number, 非必填, 订单金额左区间 单位分); AmountMax(number, 非必填, 订单金额右区间 单位分); Status(number, 非必填, 订单状态); NeedReturnTotal(boolean, 非必填, 是否需要返回total数); PageIndex(integer, 必填, 当前页数); PageSize(integer, 必填, 每页记录数)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Msg(string, 必填, 消息); Code(integer, 必填, 返回码); Data(array, 必填, 数据)]

#### 454. 坐席物流撤单

- 所属模块：订单中心/订单-物流撤单
- 请求方式：`POST`
- 请求路径：`/order/user/logistics/cancel`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderCode(string, 必填, 订单号); CancelReason(string, 非必填, 撤单原因（预留字段）)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 消息)]

#### 455. 定时任务 批量财务审核/确认收款

- 所属模块：订单中心/订单任务
- 请求方式：`GET`
- 请求路径：`/order/task/batch`
- 接口说明：定时任务 批量财务审核/确认收款
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 456. 定时任务 批量确认预存

- 所属模块：订单中心/订单任务
- 请求方式：`GET`
- 请求路径：`/order/task/batch/pre`
- 接口说明：定时任务 批量确认预存
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 457. 是否有未完结的任务（1财务审单 2确认收款）

- 所属模块：订单中心/订单任务
- 请求方式：`GET`
- 请求路径：`/order/task/existNotFinished`
- 接口说明：是否有未完结的任务（1财务审单 2确认收款）
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `type`：required=True，type=string，说明：1批量财务审单 2批量确认收款，示例：`0`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 458. 订单商品统计配置-增

- 所属模块：订单中心/订单商品统计配置
- 请求方式：`POST`
- 请求路径：`/order/sku/statistic/add`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Name(string, 非必填, 商品名称); OrgIdList(array, 非必填, 部门id集合); SkuCodeList(array, 非必填, sku集合); StartTime(string, 非必填, 生效时间); EndTime(string, 非必填, 失效时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(boolean, 非必填, 响应数据)]

#### 459. 订单商品统计配置-删

- 所属模块：订单中心/订单商品统计配置
- 请求方式：`POST`
- 请求路径：`/order/sku/statistic/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(number, 非必填, 配置id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(boolean, 非必填, 响应数据)]

#### 460. 订单商品统计配置-详情

- 所属模块：订单中心/订单商品统计配置
- 请求方式：`POST`
- 请求路径：`/order/sku/statistic/detail`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[UserId(number, 非必填, 坐席id); CustomerId(number, 非必填, 客户id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(array, 非必填, 响应数据)]

#### 461. 订单商品统计配置-查

- 所属模块：订单中心/订单商品统计配置
- 请求方式：`POST`
- 请求路径：`/order/sku/statistic/page`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Name(string, 非必填, 商品名称)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(object, 非必填, 响应数据)]

#### 462. 订单商品统计配置-改

- 所属模块：订单中心/订单商品统计配置
- 请求方式：`POST`
- 请求路径：`/order/sku/statistic/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Name(string, 必填, 商品名称); OrgIdList(array, 必填, 部门id集合); SkuCodeList(array, 必填, sku集合); StartTime(string, 必填, 生效时间); EndTime(string, 必填, 失效时间); Id(string, 必填, 配置id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 响应码); Msg(string, 非必填, 响应消息); Data(boolean, 非必填, 响应数据)]

#### 463. 获取赠品购买数量

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/gift/count`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=integer，说明：无
- `giftIds`：required=True，type=array，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 464. 某天所有销量的商品列表

- 所属模块：订单中心/订单外部接口
- 请求方式：`POST`
- 请求路径：`/order/job/productsSaleCount`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- `day`：required=True，type=string，说明：哪天，示例：`2019-09-23`

**请求体**

- `application/json`：type=object; fields=[GoodsList(array, 必填, 商品ID列表); Day(string, 必填, 日期(精确到天))]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 编码); Msg(string, 必填, 消息); Data(array, 必填, 数据)]

#### 465. 客户或坐席的最早订单

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/order/earliest`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户或坐席id，示例：`23`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(number, 非必填); msg(string, 非必填); data(string, 非必填, 订单创建时间)]

#### 466. 客户或坐席的最早订单_copy

- 所属模块：订单中心/订单外部接口
- 请求方式：`POST`
- 请求路径：`/order/order/earliest_1586835725675`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户或坐席id，示例：`23`

**请求体**

- `application/json`：type=object; fields=[CustomerId(integer, 必填); UserId(integer, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(number, 非必填); msg(string, 非必填); data(string, 非必填, 订单创建时间)]

#### 467. 计算客户某个时间之前订单的累计消费和最大一笔消费

- 所属模块：订单中心/订单外部接口
- 请求方式：`POST`
- 请求路径：`/order/orders/amount`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户id); OrderTime(string, 必填, 订单时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 468. 查询商品某天的售卖信息

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/goodsSaleInfo`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `ProductId`：required=True，type=string，说明：商品ID，示例：`123`
- `Date`：required=True，type=string，说明：日期，示例：`2019-12-26`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 返回码); msg(string, 必填, 信息); data(object, 必填)]

#### 469. 客户某天数内是否有成交记录

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/hasTransaction`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户Id
- `days`：required=True，type=string，说明：天数以内

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 编码); Msg(string, 必填, 消息); Data(boolean, 必填, 数据)]

#### 470. 客户是否有未结案订单

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/hasUnFinished`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=False，type=string，说明：客户ID，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 返回码); msg(string, 必填, 消息); data(boolean, 必填, 返回值)]

#### 471. 客户的购买历史5条

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/history`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户ID，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 返回码); msg(string, 必填, 消息); data(array, 必填)]

#### 472. 查询客户最近下单时间

- 所属模块：订单中心/订单外部接口
- 请求方式：`POST`
- 请求路径：`/order/orders/lastOrderTime`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerIds(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 返回信息); Data(object, 必填)]

#### 473. 查询客户最近使用的收货地址ID

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/lastUsedAddressId`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 返回码); Msg(string, 必填, 返回信息); Data(integer, 必填, 收货地址ID)]

#### 474. 客户的最近订单5条

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/latestByCustomerId`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户ID，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 返回码); msg(string, 必填, 消息); data(array, 必填)]

#### 475. 客户正常订单的所有真正销售额

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/realAmountAll`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户id，示例：`1`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 476. 筛选未成交客户(for联络)

- 所属模块：订单中心/订单外部接口
- 请求方式：`POST`
- 请求路径：`/order/orders/screenUnDealCustomer`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[IsReject(boolean, 必填, 是否拒收); List(array, 必填, 客户列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 编码); Msg(string, 必填, 消息); Data(array, 必填, 数据)]

#### 477. 外呼清单查询订单列表

- 所属模块：订单中心/订单外部接口
- 请求方式：`POST`
- 请求路径：`/order/orders/searchForCallout`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[UserId(integer, 必填, 用户ID); CustomerIdList(array, 必填, 客户ID列表); IsCurrentMonthNoBuy(boolean, 必填, 当月未购买); UnBuyDay(integer, 必填, 未购买天数（7，10，15，20，28)); BuyTimesStart(integer, 必填, 购买次数开始时间); BuyTimesEnded(integer, 必填, 购买次数终止); OrderTotalStart(string, 必填, 累计订单金额开始); OrderTotalEnd(string, 必填, 累计订单金额结束); LastBuyStartTime(string, 必填, 上次购买开始时间（最近一次正常订单）); LastBuyEndTime(string, 必填, 上次购买终止时间（最近一次正常订单)); HistoryRejectTimes(integer, 必填, 历史拒收次数)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 编码); Msg(string, 必填, 消息); Data(array, 必填, 数据)]

#### 478. 外呼清单查询订单列表_列表展示

- 所属模块：订单中心/订单外部接口
- 请求方式：`POST`
- 请求路径：`/order/orders/searchForCallout_history`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerIds(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填, 编码); Msg(string, 必填, 消息); Data(array, 必填, 数据)]

#### 479. 客户的订单概况

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/survey`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description, request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：客户ID，示例：`1`
- `status`：required=True，type=string，说明：状态，示例：`20`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 返回码); msg(string, 必填, 消息); data(object, 必填)]

#### 480. 媒体数据分配与回收

- 所属模块：订单中心/订单外部接口
- 请求方式：`POST`
- 请求路径：`/order/orders/undeal`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[IsReject(boolean, 必填, 是否拒收); Customers(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(array, 必填)]

#### 481. 未处理的已存预存款订单列表

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/undealedPrePayed`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(number, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 482. 查询某期间有订单的用户列表

- 所属模块：订单中心/订单外部接口
- 请求方式：`GET`
- 请求路径：`/order/orders/usersOfPeriod`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `startTime`：required=True，type=string，说明：开始时间，示例：`2019-01-12 12:00:00`
- `endTime`：required=True，type=string，说明：结束时间，示例：`2019-09-24 12:00:00`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 必填, 返回码); msg(string, 必填, 消息); data(array, 必填)]

#### 483. 财务审核 审核订单

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/financial`
- 接口说明：财务审核 审核订单
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 必填, 订单编号); Mark(string, 非必填, 财务审核备注); PayWay(integer, 非必填, 支付方式 0现金 1pos 2银行转账 3微信 4支付宝 5其他); Pass(integer, 必填, 是否审核通过 0不通过 1通过); TransferCode(string, 非必填, 转账码)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 484. 财务审核 批量审核订单

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/financial/batch`
- 接口说明：财务审核 批量审核订单
- 鉴权方式：未声明/未识别
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[codes(array, 非必填, 订单编号); status(integer, 非必填, 订单状态); customerName(string, 非必填, 客户名); customerNum(string, 非必填, 客户编号); customerId(integer, 非必填, 客户id); reviewerId(integer, 非必填, 合规审单人ID); makerId(integer, 非必填, 制单人ID); makerOrgId(integer, 非必填, 制单人部门); minOrderMoney(integer, 非必填, 订单金额（起）); maxOrderMoney(integer, 非必填, 订单金额（止）); orderType(integer, 非必填, 订单类型); startTime(string, 非必填, 制单时间（起）); endTime(string, 非必填, 制单结束（止）); mark(string, 非必填, 财务备注（批量财务审核订单传入）); payWay(integer, 非必填, 支付方式（批量财务审核订单传入）); ids(array, 非必填, 订单IdList（批量财务审核订单传入）); ...其余 15 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(boolean, 非必填)]

#### 485. 财务审单 校验转账码是否被使用过

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/financial/checkTransferCode`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[TransferCode(string, 必填, 转账码)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填); Msg(string, 必填); Data(boolean, 必填, true：被使用  false：否)]

#### 486. 财务审核 分页查询

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/financial/page`
- 接口说明：财务审核 分页查询
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Codes(array, 非必填, 订单编号); Status(integer, 非必填, 订单状态); CustomerName(string, 非必填, 客户名); CustomerNum(string, 非必填, 客户编号); CustomerId(integer, 非必填, 客户id); ReviewerId(integer, 非必填, 合规审单人ID); MakerId(integer, 非必填, 制单人ID); MakerOrgId(integer, 非必填, 制单人部门); MinOrderMoney(integer, 非必填, 订单金额（起）); MaxOrderMoney(integer, 非必填, 订单金额（止）); OrderType(integer, 非必填, 订单类型); StartTime(string, 非必填, 制单时间（起）); EndTime(string, 非必填, 制单结束（止）)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 487. 经理审核

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/manager`
- 接口说明：经理审核
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单id); Result(integer, 必填, 审核结果 0不通过 1通过); Remark(string, 必填, 备注)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 非必填)]

#### 488. 合规审单 批量分配

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/rule/batch`
- 接口说明：合规审单 批量分配
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ReviewIds(array, 必填, 审单表id); UserIds(array, 必填, 用户id); Num(integer, 必填, 分配数量)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 489. 合规审单 校验订单是否可审

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/rule/judge/{orderId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `orderId`：required=True，type=string，说明：无，示例：`119`

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 490. 合规审单 不通过

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/rule/notPass/{code}`
- 接口说明：合规审单 不通过
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：订单编号

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ReviewDesc(string, 非必填, 合规审单备注); NotPassReason(integer, 非必填, 退回原因); ActualFreeReview(integer, 非必填, 实际免审 0否 1是); PayFreight(integer, 必填, 运费规则); Type(integer, 必填, 订单类型); IsHasSurvey(boolean, 非必填, 是否已经满意度调研)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 491. 合规审单 查询该订单合规审单信息

- 所属模块：订单中心/订单审核
- 请求方式：`GET`
- 请求路径：`/order/review/rule/open/{code}`
- 接口说明：合规审单 查询该订单合规审单信息
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：订单编号

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 492. 合规审单 分页查询

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/rule/page`
- 接口说明：合规审单 分页查询
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Code(string, 非必填, 订单号); Status(integer, 非必填, 订单状态); ReviewerId(integer, 非必填, 审单人id); MakerId(integer, 非必填, 制单人id); RequiredOrgId(integer, 非必填, 制单中心); CustomerLevel(array, 非必填, 客户级别); Distribute(integer, 非必填, 是否已分配 0否 1是 依据是否有审单人判断); MinAmount(number, 非必填, 订单金额（起）); MaxAmount(number, 非必填, 订单金额（止）); CustomerNumber(string, 非必填, 客户编号); CustomerName(string, 非必填, 客户姓名); Must(integer, 非必填, 必审订单 1是); IsSystemReview(integer, 非必填, 是否系统免审 1是); Relate(integer, 非必填, 是否与我相关 1是); MinMakeTime(string, 非必填, 制单时间（起）); MaxMakeTime(string, 非必填, 制单时间（止）); ...其余 9 个字段]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 493. 合规审单 通过

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/rule/pass/{code}`
- 接口说明：合规审单 通过
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：订单编号

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ReviewDesc(string, 非必填, 合规审单备注); NotPassReason(integer, 非必填, 退回原因); ActualFreeReview(integer, 非必填, 实际免审 0否 1是); PayFreight(integer, 必填, 运费规则); Type(integer, 必填, 订单类型); IsHasSurvey(boolean, 非必填, 是否已经满意度调研)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Mmsg(string, 非必填); Data(boolean, 非必填)]

#### 494. 合规审单 暂存

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/order/review/rule/storage/{code}`
- 接口说明：合规审单 暂存
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `code`：required=True，type=string，说明：订单编号

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[ReviewDesc(string, 非必填, 合规审单备注); NotPassReason(integer, 非必填, 退回原因); ActualFreeReview(integer, 非必填, 实际免审 0否 1是); PayFreight(integer, 必填, 运费规则); Type(integer, 必填, 订单类型)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 495. 合规审单 自取审单

- 所属模块：订单中心/订单审核
- 请求方式：`POST`
- 请求路径：`/review/rule/take`
- 接口说明：合规审单 自取审单
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：无

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`
- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填)]

#### 496. 保存

- 所属模块：订单中心/订单收藏
- 请求方式：`POST`
- 请求路径：`/order/goods/collection/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无
- `Authorization`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Name(string, 必填, 名称); Items(array, 必填, 收藏商品列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 497. 根据userId获取收藏列表

- 所属模块：订单中心/订单收藏
- 请求方式：`POST`
- 请求路径：`/order/goods/collection/{userId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***
- `Authorization`：required=False，type=string，说明：无
- `Token`：required=False，type=string，说明：无

**Path 参数**

- `userId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[QueryGoodsParam(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(array, 必填)]

#### 498. 删除

- 所属模块：订单中心/订单收藏
- 请求方式：`POST`
- 请求路径：`/order/goods/collection/{userId}/{collectionId}/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description, request_body

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `userId`：required=True，type=integer，说明：无
- `collectionId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 499. 查询订单的超售产品

- 所属模块：订单中心/订单校验
- 请求方式：`GET`
- 请求路径：`/order/check/oversale/{orderId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：OpenAPI security=bearer
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderId`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Msg(string, 必填); Code(integer, 必填); Data(array, 必填)]

#### 500. 校验订单政策是否可以下单

- 所属模块：订单中心/订单校验
- 请求方式：`POST`
- 请求路径：`/order/extend/policy/buy/number`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); OrderId(number, 非必填, 订单ID (修改时传入)); List(array, 必填, 政策列表)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回码); Msg(string, 必填, 返回信息)]

#### 501. 未结案订单中是否有下单商品的同类商品

- 所属模块：订单中心/订单校验
- 请求方式：`GET`
- 请求路径：`/order/notFinish/sameGoods`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description, request_body

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=False，type=string，说明：无
- `CustomerId`：required=True，type=string，说明：无
- `OrderGoodsIds`：required=True，type=array，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 502. 未结案订单中是否有下单商品的同类商品

- 所属模块：订单中心/订单校验
- 请求方式：`POST`
- 请求路径：`/order/notFinish/sameGoods`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(string, 非必填); CustomerId(string, 必填); OrderGoodsIds(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 503. 查询政策在订单中是否已经下单

- 所属模块：订单中心/订单校验
- 请求方式：`GET`
- 请求路径：`/order/policy/use/number/{policyId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `policyId`：required=True，type=string，说明：政策ID

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 必填, 返回吗); Msg(string, 必填, 返回信息); Data(number, 必填, 使用个数)]

#### 504. 删除坐席下单缓存

- 所属模块：订单中心/订单校验
- 请求方式：`POST`
- 请求路径：`/order/temporary/delete`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(number, 必填, 客户ID); EmployeeId(number, 必填, 坐席ID)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(number, 非必填, 返回码); Msg(string, 非必填, 返回信息)]

#### 505. 根据订单编号查询满意度调研信息

- 所属模块：订单中心/订单满意度调研
- 请求方式：`GET`
- 请求路径：`/127.0.0.1/order/review/appraise/{orderId}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- `orderId`：required=True，type=string，说明：订单编号

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(null, 必填); Data(object, 必填)]

#### 506. 保存满意度调研

- 所属模块：订单中心/订单满意度调研
- 请求方式：`POST`
- 请求路径：`/127.0.0.1/order/review/save/appraise`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 非必填, 调研编号，存在时，说明是修改); OrderId(integer, 必填, 订单编号); OverallRating(integer, 必填, 总体评价); GradeNum(integer, 非必填, 得分); ServiceProblemType(array, 非必填, 问题类型列表); ProblemDescribe(string, 非必填, 问题描述)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(boolean, 必填)]

#### 507. 规则新增

- 所属模块：订单中心/订单编号规则
- 请求方式：`POST`
- 请求路径：`/order/code/rule/add`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderTypes(array, 必填, 订单类型id); CodePrefix(string, 必填, 订单前缀); ChannelId(integer, 必填, 下单平台id); CompanyId(integer, 必填, 公司id); DepartmentIds(array, 必填, 部门id 数组)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(integer, 非必填)]

#### 508. 规则停用/启用

- 所属模块：订单中心/订单编号规则
- 请求方式：`POST`
- 请求路径：`/order/code/rule/changeStatus`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Ids(array, 必填); Status(integer, 必填, 0启用，1停用)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(boolean, 非必填, true成功，false 失败)]

#### 509. 列表查询

- 所属模块：订单中心/订单编号规则
- 请求方式：`POST`
- 请求路径：`/order/code/rule/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderType(integer, 非必填, 订单类型); PageIndex(integer, 非必填); PageSize(integer, 非必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(object, 非必填)]

#### 510. 规则更新

- 所属模块：订单中心/订单编号规则
- 请求方式：`POST`
- 请求路径：`/order/code/rule/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[Id(integer, 必填, id); OrderTypes(array, 必填, 订单类型id); CodePrefix(string, 必填, 订单前缀); ChannelId(integer, 必填, 下单平台); CompanyId(integer, 必填, 公司id); DepartmentIds(array, 必填, 部门id 数组)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(integer, 非必填)]

#### 511. 根据发货批次号查询订单详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/batchNo`
- 接口说明：根据发货批次号查询订单详情
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `batchNo`：required=True，type=string，说明：无
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 512. 根据订单编号查询订单详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/code`
- 接口说明：根据订单编号查询订单详情
- 鉴权方式：Authorization 请求头
- 缺失字段：request_body

**请求头**

- `Authorization`：required=False，type=string，说明：无

**Path 参数**

- 无/未声明

**Query 参数**

- `orderCode`：required=True，type=string，说明：无
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 513. 查询订单礼券详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/coupon`
- 接口说明：查询订单礼券详情
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 514. 查询订单使用礼券详情（聚合展示）

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/coupon/combine`
- 接口说明：查询订单使用礼券详情（聚合展示）
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 515. 查询订单客户详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/customer`
- 接口说明：查询订单客户详情
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 516. 查询订单运单号

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/detail/logistics/code`
- 接口说明：查询订单使用礼券详情（聚合展示）
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=True，type=string，说明：订单ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 非必填); Msg(string, 非必填); Data(string, 非必填, 运单号，多个以逗号隔开，第一个为母单号，其他为子单号)]

#### 517. 查询订单审单详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/detail/review`
- 接口说明：查询订单审单详情
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 518. Description 客户或坐席的最早订单时间

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/earliest`
- 接口说明：Description 客户或坐席的最早订单时间
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `customerId`：required=True，type=string，说明：无，示例：`0`
- `userId`：required=True，type=string，说明：无，示例：`0`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 519. 查询订单商品

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/goods`
- 接口说明：查询订单商品
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `OrderId`：required=True，type=integer，说明：订单ID
- `QuerySource`：required=False，type=integer，说明：查询来源（0：订单修改页，1：订单详情页），不传默认为1

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 520. 查询订单商品（可查询出政策名称）

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/goods/with/policy`
- 接口说明：查询订单商品
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 521. 查询订单介绍人详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/introduce`
- 接口说明：查询订单介绍人详情
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 522. selectOrderLogistics

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/logistics`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 523. 根据物流单号查询订单详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/logisticsCode`
- 接口说明：根据物流单号查询订单详情
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `logisticsCode`：required=True，type=string，说明：无
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 524. 查询客户订单应收金额(分)

- 所属模块：订单中心/订单详情
- 请求方式：`POST`
- 请求路径：`/order/money/get/pay/amount`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerId(string, 必填, 客户id); StartTime(string, 必填, 开始时间); EndTime(string, 必填, 结束时间)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Data(integer, 必填, 应收金额); Msg(string, 必填)]

#### 525. 查询政策在订单中使用次数

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/policy/count`
- 接口说明：查询政策在订单中使用次数
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `policyId`：required=True，type=string，说明：无
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(integer, 非必填)]

#### 526. 查询订单收货人详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/receiver`
- 接口说明：查询订单收货人详情
- 鉴权方式：Authorization 请求头；CurrentUser 请求头
- 缺失字段：request_body

**请求头**

- `Authorization`：required=True，type=string，说明：无，示例：***已脱敏***
- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 527. 查询订单奖励详情

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/reward`
- 接口说明：查询订单奖励详情
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `orderId`：required=True，type=string，说明：订单ID
- `isDeleted`：required=False，type=string，说明：无
- `userId`：required=False，type=string，说明：无
- `userName`：required=False，type=string，说明：无
- `orgId`：required=False，type=string，说明：无
- `loginId`：required=False，type=string，说明：无
- `loginUserName`：required=False，type=string，说明：无
- `loginOrgId`：required=False，type=string，说明：无
- `userAccount`：required=False，type=string，说明：无
- `createSource`：required=False，type=string，说明：无
- `createTime`：required=False，type=string，说明：无
- `updateSource`：required=False，type=string，说明：无
- `updateTime`：required=False，type=string，说明：无
- `total`：required=False，type=string，说明：无
- `pageIndex`：required=False，type=string，说明：无
- `pageSize`：required=False，type=string，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(object, 非必填)]

#### 528. 订单状态映射查询

- 所属模块：订单中心/订单详情
- 请求方式：`GET`
- 请求路径：`/order/status`
- 接口说明：订单状态映射查询
- 鉴权方式：未声明/未识别
- 缺失字段：headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[code(integer, 非必填); msg(string, 非必填); data(array, 非必填)]

#### 529. 查询订单配置详情（单条）

- 所属模块：订单中心/订单配置
- 请求方式：`GET`
- 请求路径：`/order/config/detail/{Id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, request_body

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- `Id`：required=True，type=string，说明：无

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 530. 保存订单包邮配置

- 所属模块：订单中心/订单配置
- 请求方式：`POST`
- 请求路径：`/order/config/save`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DepartmentId(integer, 必填, 部门ID); PackageMailMoney(integer, 必填, 订单包邮金额); NoAuditTime(integer, 必填, 免审时长); ReturnTimes(integer, 必填, 退回次数); IsEditFreight(integer, 必填, 是否可修改运费（0：不可以；1：可以编辑）); PoolId(integer, 必填, 第三方平台客户导入的数据池ID); GoodsList(array, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 531. 查询订单包邮配置

- 所属模块：订单中心/订单配置
- 请求方式：`GET`
- 请求路径：`/order/config/select`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `DepartmentId`：required=True，type=string，说明：部门id
- `GoodsId`：required=True，type=string，说明：商品id
- `PackageMailMoneyBegin`：required=True，type=string，说明：金额开始金额
- `PackageMailMoneyEnd`：required=True，type=string，说明：金额结束金额

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(object, 必填)]

#### 532. 修改订单包邮配置

- 所属模块：订单中心/订单配置
- 请求方式：`POST`
- 请求路径：`/order/config/update`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[DepartmentId(integer, 必填, 部门ID); PackageMailMoney(integer, 必填, 订单包邮金额); NoAuditTime(integer, 必填, 免审时长); ReturnTimes(integer, 必填, 退回次数); IsEditFreight(integer, 必填, 是否可修改运费（0：不可以；1：可以编辑）); PoolId(integer, 必填, 第三方平台客户导入的数据池ID); GoodsList(array, 必填); Id(integer, 必填, Id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

#### 533. 查询默认配置项

- 所属模块：订单中心/订单配置/可消费额度配置
- 请求方式：`GET`
- 请求路径：`/config/consumable/default`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 534. 配置查询 - 分页

- 所属模块：订单中心/订单配置/可消费额度配置
- 请求方式：`GET`
- 请求路径：`/config/consumable/quota`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `CustomerName`：required=False，type=string，说明：无
- `CustomerCode`：required=False，type=string，说明：无
- `PageSize`：required=True，type=number，说明：无
- `PageIndex`：required=True，type=number，说明：无

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(integer, 必填); Msg(string, 必填); Data(object, 必填)]

#### 535. 创建一个消费额度配置

- 所属模块：订单中心/订单配置/可消费额度配置
- 请求方式：`POST`
- 请求路径：`/config/consumable/quota`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description

**请求头**

- `CurrentUser`：required=True，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[CustomerCode(string, 必填); ExtraConsumableMoneyQuota(integer, 非必填, 增加额度); ExtraPayAmount(integer, 非必填, 增加订单应收金额额度); ExtraMonthCollectionMoney(integer, 非必填, 增加每月订单快递代收总额); ExtraMonthDeliveryMoney(integer, 非必填, 增加每月订单款到发货总额); Remark(string, 必填)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 536. 删除一个消费额度配置

- 所属模块：订单中心/订单配置/可消费额度配置
- 请求方式：`POST`
- 请求路径：`/config/consumable/quota/delete/{id}`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：CurrentUser 请求头
- 缺失字段：description, request_body

**请求头**

- `CurrentUser`：required=False，type=string，说明：无，示例：***已脱敏***

**Path 参数**

- `id`：required=True，type=string，说明：需删除的配置id

**Query 参数**

- 无/未声明

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` type=object; fields=[]

#### 537. 校验是否有联系客户的权限（拨打和转订单）

- 所属模块：资源相关操作 Controller
- 请求方式：`POST`
- 请求路径：`/customerservice/media/task/auth`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/CustomerContactReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABBoolean%C2%BB

#### 538. 校验是否有下单的权限

- 所属模块：资源相关操作 Controller
- 请求方式：`POST`
- 请求路径：`/customerservice/media/task/auth/order`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/CustomerContactReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABBoolean%C2%BB

#### 539. 订单成交关闭资源

- 所属模块：资源相关操作 Controller
- 请求方式：`POST`
- 请求路径：`/customerservice/media/task/deal`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/MediaTaskDealReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 540. 订单结案关闭资源

- 所属模块：资源相关操作 Controller
- 请求方式：`POST`
- 请求路径：`/customerservice/media/task/finish`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：ref=#/components/schemas/MediaTaskFinishReqVO

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg

#### 541. updateMediaTaskOrderStatus

- 所属模块：资源相关操作 Controller
- 请求方式：`GET`
- 请求路径：`/customerservice/media/task/update/order/status`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description, headers, request_body

**请求头**

- 无/未声明

**Path 参数**

- 无/未声明

**Query 参数**

- `Id`：required=True，type=integer，说明：无，示例：`0`
- `Status`：required=True，type=integer，说明：无，示例：`0`

**请求体**

无/未声明

**返回体**

- `200`：无描述；`application/json` ref=#/components/schemas/ReturnMsg%C2%ABT%C2%BB

#### 542. 媒体下单时记录标签

- 所属模块：通话记录
- 请求方式：`POST`
- 请求路径：`/callrecords/add/media/customer/pool`
- 接口说明：Apifox description 未填写，当前仅可使用接口名称辅助理解。
- 鉴权方式：未声明/未识别
- 缺失字段：description

**请求头**

- `Content-Type`：required=True，type=string，说明：无，示例：`application/json`

**Path 参数**

- 无/未声明

**Query 参数**

- 无/未声明

**请求体**

- `application/json`：type=object; fields=[OrderId(integer, 必填, 订单id); CustomerId(integer, 必填, 客户id)]

**返回体**

- `200`：无描述；`application/json` type=object; fields=[Code(string, 必填); Msg(string, 必填); Data(string, 必填)]

## 5. 同步问题与缺失项

### 5.1 已发现问题

- `description` 缺失较多：核心订单接口中 `458` 条接口缺少接口描述，后续测试只能依赖接口名称、路径和参数推断用途。
- 请求头未统一结构化：核心订单接口中 `175` 条接口未声明请求头；另有 `199` 条接口虽然有 `Authorization` 或 `CurrentUser`，但 `auth_type` 字段为空。
- 路径规范问题：核心订单接口中 `10` 条路径带有 `/127.0.0.1`、`/localhost` 或 `/http://...` 片段，后续自动化执行前需要做 Base URL 与 path 归一化。
- 文档示例值风险：Apifox 导出的接口文档中存在 Authorization/CurrentUser 等请求头示例值。验证报告已脱敏，但建议后续同步器对知识库源文件也做敏感示例脱敏。
- 工单与订单存在关键词混淆：`work_order`、客服工单、审计工单会被广义关键词命中，后续需求映射时需要结合模块和业务语义过滤。

### 5.2 未发现的问题

- 丝路 Apifox 项目文件存在且可解析。
- 丝路数据库结构文件存在且可解析。
- 核心订单表包含字段、字段类型、是否可为空、默认值、主键和索引信息。
- 核心订单接口包含 method、path、headers/path/query/body/response 等结构字段；缺失项已写入 `missing_fields`。

## 6. 是否可支撑后续测试使用

| 使用场景 | 是否支撑 | 说明 |
|---|---|---|
| 需求到接口候选映射 | 可以 | 订单相关接口数量充足，模块和路径信息可用于候选匹配。 |
| 测试用例设计参考 | 可以 | 数据表和接口字段能支持识别订单主表、明细、金额、审核、物流、售后等测试点。 |
| 自动化脚本初稿生成 | 部分可以 | method/path/body/response 已具备，但路径归一化和鉴权配置需要补齐。 |
| 直接稳定执行自动化 | 暂不建议直接执行 | 缺少统一 auth_type、部分接口 description/header/body 缺失，部分 path 不是标准相对路径。 |
| 数据造数结构分析 | 可以作为依据 | 数据库结构完整，但仅凭结构不能确认业务必填规则，仍需结合接口和业务规则。 |

## 7. 建议后续动作

1. 对丝路订单接口做 path 归一化：清理 `/127.0.0.1`、`/localhost`、`/http://...` 这类路径。
2. 建立订单接口鉴权规则映射：把 `Authorization`、`CurrentUser`、业务用户上下文统一抽象成自动化可配置认证模型。
3. 对知识库源文件做请求头示例脱敏，尤其是 Authorization、CurrentUser、Cookie、Token。
4. 按模块拆分订单接口子集：制单、查询、审核、财务、物流、售后、分销商、外部平台订单。
5. 后续测试任务进入接口自动化前，先由接口获取 Agent 输出“需求相关接口子集 + 相关库表子集”，不要把全部核心订单接口一次性交给自动化 Agent。