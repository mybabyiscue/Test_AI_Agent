# 知识库同步

根据用户输入判断同步范围，运行 `scripts/sync_knowledge.py` 完成同步，并汇报结果。

## 同步范围解析规则

从用户输入 `$ARGUMENTS` 中解析同步目标：

| 用户表达 | 脚本参数 |
|----------|----------|
| "全部"/"全量"/无指定 | `python scripts/sync_knowledge.py` |
| "只同步数据库"/"数据库" | `python scripts/sync_knowledge.py --db-only` |
| "只同步接口"/"接口" | `python scripts/sync_knowledge.py --api-only` |
| "丝路"/"silkroad" | `python scripts/sync_knowledge.py --system silkroad` |
| "丝路数据库"/"silkroad db" | `python scripts/sync_knowledge.py --system silkroad --db-only` |
| "丝路接口"/"silkroad api" | `python scripts/sync_knowledge.py --system silkroad --api-only` |
| "saas"/"享佳云"/"鲨域" | `python scripts/sync_knowledge.py --system saas` |
| "呼叫中心"/"callcenter" | `python scripts/sync_knowledge.py --system callcenter` |
| "鲨域数据库"/"shark db" | `python scripts/sync_knowledge.py --system shark --db-only` |
| "丝路 center 库" | `python scripts/sync_knowledge.py --system silkroad --db center` |
| "saas 接口 4152663" | `python scripts/sync_knowledge.py --system saas --project 4152663` |

## 系统名称映射

- 丝路 = silkroad
- 鲨域 = shark
- saas = 享佳云 = 鲨域(接口) = saas
- 呼叫中心 = callcenter

## 可用数据库列表

- silkroad: center, cms, crm_core, cx, ec, oms, result
- shark: mall4cloud_saas_admin, mall4cloud_saas_order, mall4cloud_saas_product, mall4cloud_saas_user, scrm 等 23 个库
- saas: contact, customer, ec, etl, saas, scrm, shark, shop, sop

## 可用接口项目

- silkroad: 776242
- saas: 4152663
- callcenter: 460082

## 执行步骤

1. 解析 `$ARGUMENTS` 确定同步范围
2. 运行对应命令
3. 输出同步结果摘要（成功/失败数量、变化项）
