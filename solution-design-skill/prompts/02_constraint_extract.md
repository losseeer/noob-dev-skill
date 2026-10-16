# 步骤 2：提取约束

## 目的

从定位卡里取出「技术方案必须满足的边界」，并把它和初步选型做冲突比对。

## 做什么

1. 读 `rules/stack_rules.yaml` 的 `constraint_dimension_bindings`，
   把定位卡里锁死的维度映射到具体选型面。
   命中的选型必须标 `locked_by_constraint: true`，且 `basis: constraint`。
2. 逐条比对 `rules/constraint_rules.yaml`，把命中的冲突写进 `current.yaml` 的
   `constraint_conflicts`，每条都要有 `disposition`。
3. 还没解决的，`disposition` 填 `open`，并同步进 `open_questions`。

## 冲突的处置只有四种

| disposition | 含义 |
|---|---|
| `resolved` | 已换选型绕过去，要在 `note` 里写清换成了什么 |
| `accepted_risk` | 用户明知代价并接受，**必须同步写进 review 的 findings** |
| `escalated_to_positioning` | 约束本身不合理，产物里留记录，提示用户回去重定位 |
| `open` | 未解决，进 `open_questions`，阻塞最终 review |

## 硬性约束

- **本 Skill 不得自行放宽上游约束。** 想放宽只有 `escalated_to_positioning` 这一条路。
  「这个约束太严了先按宽松做」属于把失败伪装成结果。
- `blocker` 级冲突未处置时，方案不得进步骤 6 的 review，更不得标 `status: reviewed`。
- `non_functional_priority` 里的优先级顺序要写进 `current.yaml` 的 `summary`，
  它是后续所有选型取舍的裁决依据。

## 反模式

- 把 `constraints` 原样抄进 `current.yaml` 就当完成了——必须落到具体选型面才有约束力。
- 冲突写 `disposition: open` 却不进 `open_questions`，于是再也没有人记得它。
