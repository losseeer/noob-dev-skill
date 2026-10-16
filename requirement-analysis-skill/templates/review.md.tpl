# Requirement quality gate {{date}}

需求：{{requirement_id}}　版本：{{version_of_requirement}}
Reviewer：{{reviewer}}
轮次：第 {{revision_round}} 轮

> **本结论是质量门禁，不是范围门禁。**
> `pass` 只代表「写得清楚、可以测、可以开工」，不代表「该做」；
> 是否该做由项目定位 Skill 的范围门禁决定。

## 检查项

| 检查 | 结果 | 依据 | 备注 |
|---|---|---|---|
| 无歧义 unambiguous | {{r_unambiguous}} | QC-001 | {{n_unambiguous}} |
| 可测试 testable | {{r_testable}} | QC-002 | {{n_testable}} |
| 完整 complete | {{r_complete}} | QC-003 | {{n_complete}} |
| 一致 consistent | {{r_consistent}} | QC-004 | {{n_consistent}} |
| 可行 feasible | {{r_feasible}} | QC-005 | {{n_feasible}} |
| 可追踪 traceable | {{r_traceable}} | QC-006 | {{n_traceable}} |
| 已排序 prioritized | {{r_prioritized}} | QC-007 | {{n_prioritized}} |

## 结论

**{{decision}}**（pass / revise / reject）

{{decision_reason}}

## 问题

{{issues}}

> `pass` 时本节必须写「无」，不允许留填空话。

## 整改动作

{{action}}

## 复跑建议

{{rerun_advice}}
