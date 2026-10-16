version: 1
reviewed_at: {{date}}
reviewer: ""
design_version: v0.1
decision: request_changes           # approve / request_changes / insufficient_evidence
checks:
  - id: C1
    item: 每条选型的 basis 都可追溯
    passed: false
    evidence_ref: ""
    note: ""
  - id: C2
    item: 所有 assumption 都写了 impact_if_wrong 与 mitigation
    passed: false
  - id: C3
    item: 上游每条 AC 在 coverage 里有登记且都有出处认领
    passed: false
    evidence_ref: scripts/validate_bundle.py
    note: 必须以 bundle 校验输出为依据，不许凭印象填
  - id: C4
    item: 上游 constraints 与本方案的冲突已全部处置
    passed: false
  - id: C5
    item: 数据模型字段可追溯或显式标注 derived / assumption
    passed: false
  - id: C6
    item: http 接口的错误分支覆盖了对应 AC 的异常场景
    passed: false
  - id: C7
    item: 涉及 UI 时页面能落到至少一条 REQ
    passed: false
    note: 无 UI 时标 true 并注明不适用
findings:
  - severity: major                 # blocker / major / minor
    description: ""
    evidence_ref: ""
    disposition: must_fix           # must_fix / accepted_risk / escalate / deferred
    note: ""
unresolved_assumptions: []          # ASM-xxx
status_after: draft                 # draft / reviewed
summary: ""
