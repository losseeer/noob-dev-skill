# 任务：执行需求门禁

对单个新需求读取 `.project/positioning/current.yaml`，判断它是否符合当前定位。不要在门禁阶段直接实现需求。

## 可选输入：定位变更候选

可选读取 `.project/requirements/positioning_candidates.yaml`（由 requirement-analysis-skill 产生）。

| 情况 | 处理 |
|---|---|
| 存在且含与本需求相关的 `POS-CAND-xxx` | 把候选当作门禁输入之一；候选不是结论，仍需按下方检查顺序判定 |
| 不存在、为空或格式不支持 | 记为 `not_found` / `skipped`，**不阻塞、不报错**，继续正常门禁 |

约束：

- **绝不修改**该文件，包括不回写候选 `status`。
- 引用候选时只在门禁结果的 `reason` 中写候选 ID。
- 候选缺失时不得要求用户先跑需求分析，也不得据此放宽判定。

## 检查顺序

0. 读取 `status`；若为 `frozen`，输出 `out_of_scope`，直到用户明确解冻并执行重定位 review。
1. 需求服务对象是否在 `positioning.users` 中？
2. 需求是否属于 `do_now` 的核心路径？
3. 需求是否命中 `do_not` 或 `reserved`？
4. 需求是否提高数据敏感度、收费、合同、权限或监管要求？
5. 需求是否超过维护时间、预算、可靠性或交付约束？
6. 需求是否命中任一 `reposition_triggers.condition`？
7. 是否存在安全、合规或不可逆数据风险？将结果明确标为 `clear`、`unresolved` 或 `blocked`；证据不足必须是 `unresolved`，不能当成 `clear`。
8. 该请求是否即使重定位也不应实现？若是，标记 `prohibited_even_after_reposition: true`。

## 决策优先级

按 `rules/gate_rules.yaml` 从高到低匹配，第一条命中规则生效：

- `reject`：存在未解决的硬约束，不能按当前请求直接实现
- `out_of_scope`：需要先重定位，或明确在当前 `do_not` 中
- `must`：当前定位核心路径不可缺少
- `should`：符合范围但不是核心路径

不要把 `out_of_scope` 写成永久拒绝；同时给出可检查的 `upgrade_trigger`。

## 输出

输出符合 `schemas/requirement_gate.schema.yaml` 的 YAML，并包含：

- 需求原文
- 当前定位版本、状态与等级
- 命中的规则和证据路径；无匹配时使用 `current.yaml#scope:no-match`
- `risk_state`、`prohibited_even_after_reposition`、`in_do_not`、`trigger_reposition`、`exceeds_hard_budget`、`core_path`、`fits_scope`
- 决策、理由、升级条件、下一步动作
- 判断日期
- 定位候选读取情况（仅在读到了候选时写候选 ID；未读到时写 `not_found` 或不写）

默认保存到 `.project/positioning/gates/<date>-<slug>.yaml`。
