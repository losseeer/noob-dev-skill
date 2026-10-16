# 任务：可选的项目定位桥接

这是需求分析 Skill 与项目定位 Skill 之间**唯一**的协作点。两边不互相调用，只通过文件约定传递。

## 输入侧：可选读取

检查 `.project/positioning/current.yaml`：

| 情况 | 处理 |
|---|---|
| 存在 | 只读 `summary` / `constraints` / `glossary`，覆盖矩阵 `positioning_context: read` |
| 不存在 | `positioning_context: not_found`，**不阻塞**，正常执行 |
| 存在但读失败/格式不支持 | `positioning_context: skipped`，在 warnings 里写明原因，不阻塞 |

**绝对禁止：**

- 修改定位卡任何内容
- 读取 `do_not` / `reserved` / `reposition_triggers` 并据此拒绝或降级需求
- 调用或要求调用项目定位 Skill

理由：是否拒绝一个需求属于**范围门禁**，是对方职责。需求分析只负责「写清楚」。

允许的正当用法：

- `glossary`：统一术语命名，避免同义词
- `constraints`：把已有硬约束填进 `non_functional` 或 `assumptions`
- `summary`：用于理解项目背景；写进需求时必须标明来源，不得直接当成已确认事实

## 输出侧：定位变更候选

在需求中出现以下信号时，写一条候选：

| signal | 触发词举例 |
|---|---|
| `payment` | 支付、收款、下单、退款 |
| `subscription` | 订阅、会员、套餐、续费 |
| `billing` | 账单、发票、结算、对账 |
| `multi_tenant` | 多租户、团队空间、企业版 |
| `compliance` | 合规、等级保护、隐私合规 |
| `sla` | SLA、可用性承诺、故障赔偿 |
| `audit` | 审计、操作留痕、监管报送 |
| `scale` | 百万级、高并发、全球化部署 |
| `regulation` | 个人信息保护法、数据出境 |
| `external_integration` | 对接第三方、开放 API、ISV |

写入 `.project/requirements/positioning_candidates.yaml`，符合
`schemas/positioning_candidate.schema.yaml`。

每条候选的 `action` 固定为：`建议交给项目定位 Skill 做范围门禁`。

## 三条纪律

1. **不决策。** 只写候选与理由，不写「因此该需求不做」或「需要升级项目等级」。
2. **不静默。** 写完必须在回复里告诉用户有一条候选待对方处理，不能悄悄落文件。
3. **不阻塞。** 候选存在与否都不影响本 Skill 继续产出需求卡。

## 输出汇报格式

```
定位上下文：已读取 / 未知 / 跳过
读到的影响项：glossary（术语 3 条）、constraints（2 条）
新增定位候选：POS-CAND-001 <标题>（<原因一句话>）
下一步：<交给项目定位 Skill 做范围门禁>
```
