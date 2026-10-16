# 任务：跑需求质量门禁

**这是质量门禁，不是范围门禁。**
结论只回答「这份需求有没有写好、能不能测」，不回答「这件事该不该做」。
该不该做由项目定位 Skill 的范围门禁负责。

## 七项检查

按 `rules/quality_rules.yaml` 逐项跑，每项只能得 `pass` / `fail` / `unknown`：

| 检查 | rule_id | 判定要点 |
|---|---|---|
| `unambiguous` | QC-001 | 无模糊词，术语都有定义 |
| `testable` | QC-002 | 每条 AC 都有 Given/When/Then 且结果可观测 |
| `complete` | QC-003 | P0 维度齐全，标准场景覆盖或注明不适用 |
| `consistent` | QC-004 | 无 blocking 冲突 |
| `feasible` | QC-005 | 高风险假设有对应探针 |
| `traceable` | QC-006 | `trace.source` 存在且已知 |
| `prioritized` | QC-007 | MoSCoW 优先级确定，wont 已进入 out_of_scope |

拿不到足够信息判定的项写 `unknown` 并说明缺什么，**不允许默认 pass**。

## 决策

- `pass`：七项全部 pass；允许留档 warning
- `revise`：blocking 失败 ≤ 3 项
- `reject`：任一为真
  - blocking 失败 > 3 项
  - `actor` 与 `goal` 同时缺失
  - 命中 PRIO-003（越权、数据丢失、资金类需求被降级）
  - 连续两轮 revise 后仍有 blocking 失败

## 每条 issue 必须写全

- `check`：属于哪一项
- `severity`：blocking / warning
- `message`：问题是什么
- `rule_id` / `location`：命中哪条规则、在需求卡的哪个字段
- `fix`：具体怎么改

## 反自欺条款

- 不允许因为「用户赶时间」把 `reject` 写成 `pass`
- 不允许把 `unknown` 计入 pass
- 不允许在无 `issues` 的情况下输出 `revise`
- decision 为 `pass` 时 `issues` 必须为空数组
- 静默降级等同于伪造结论，必须显式写进 `scope_note` 之外的说明里

## 输出

符合 `schemas/quality_gate.schema.yaml` 的结果，写入
`.project/requirements/reviews/<date>-<version>.yaml`。

`pass` 时把需求卡 `status` 改为 `reviewed`。
`revise` / `reject` 时保持 `draft`，并把 `issues` 与 `action` 汇报给用户，
明确指出「补充 XX 后可重新评审」，不要用「建议优化」这类软话掩盖阻塞。
