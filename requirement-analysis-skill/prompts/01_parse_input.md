# 任务：解析输入

把原始输入变成需求候选与初始覆盖矩阵。这一阶段**不提问**，只抽取。

## 输入形态

任意一种或多种组合：

- 一段模糊想法（「我想做个能收藏文章的功能」）
- 用户反馈（「点收藏没反应，也不知道成功没」）
- Issue / ticket 正文
- 聊天记录片段
- 已有 bugs 描述或代码片段

## 处理步骤

1. **切分需求候选。**
   按「一次可以独立验收的事」切分，而不是按段落切分。
   一句输入里可以同时有功能诉求、抱怨、隐含的非功能要求——它们可能对应多个候选。

2. **给每个候选一个临时编号** `REQ-001` 起，按用户叙述顺序编号。

3. **标注来源。** 每个候选的 `trace.source` 必须写明出处：
   `用户反馈-2026-10-01` / `issue#123` / `聊天记录 10-01 14:20` / `代码 comments in src/x.ts`。
   找不到来源时写 `unknown`，并在 `open_questions` 里显式说明，**不要用「推断的来源」凑数**。

4. **逐维度抽取。** 对每个候选跑一遍 17 个维度（见 `rules/coverage_rules.yaml` 的 dimensions）。

5. **标记状态。** 每个维度只能有一个状态：

   | 状态 | 判定依据 |
   |---|---|
   | `explicit` | 明确陈述，带证据原文 |
   | `inferred` | 未明说但可由上下文推出；必须写 source + reason + confidence |
   | `missing` | 完全没有线索 |
   | `low_confidence` | 有线索但不足以稳定判断 |
   | `conflict` | 证据互相矛盾；必须给 ≥ 2 条证据 |
   | `undecided` | 用户明确说没想好 |

6. **跑冲突检测。** 应用 `rules/conflict_rules.yaml` 的全部 blocking 规则，命中即标 `conflict` 并写进 `conflicts`。

## 边界

- 不做范围判断。不判断这个需求该不该做、是否在某个项目定位内。
- 不使用 `rules/default_rules.yaml` 补 P0 缺失——那是下一步的事。
- 不替用户改述诉求。原文写不清的，抽出来标 `low_confidence`，交给澄清。

## 输出

对每个候选输出一份符合 `schemas/coverage.schema.yaml` 的覆盖矩阵，写入
`.project/requirements/coverage/REQ-xxx.coverage.yaml`。

字段要求：

- `coverage` 必须包含全部 17 个维度，缺一个维度就等于没跑全量扫描
- `questions`、`skipped`、`defaults_applied` 在本阶段先填空数组
- `ready_for_modeling` 先填 `false`
- `positioning_context`：本阶段不读定位卡，填 `not_found`

最后用列表汇报：抽出了几个候选需求，每个的一句话目标，以及哪些维度完全没有线索。
