version: 1
as_of: {{date}}
selections:
  # 每个非平凡技术面一条。basis 四选一：constraint / requirement / assumption / user_choice
  - id: SEL-001
    area: language                 # 见 rules/stack_rules.yaml 的 area 枚举
    choice: ""
    basis: user_choice
    source_ref: ""                 # 从哪个文件读到的现有技术栈
    confidence: high
    risk_level: low
    note: ""
  # constraint 型必须写 source_ref，指向定位卡里的具体字段
  - id: SEL-002
    area: storage
    choice: ""
    basis: constraint
    source_ref: constraints.<field>
    locked_by_constraint: true     # 该选型不接受当场修改
    decision_ref: ADR-001
    alternatives:
      - name: ""
        rejected_because: ""
        would_reconsider_when: ""
    confidence: high
  # assumption 型必须写 why_assumed 与 revisit_when，否则校验不过
  - id: SEL-003
    area: frontend
    choice: ""
    basis: assumption
    why_assumed: ""
    revisit_when: ""
    confidence: low
    risk_level: medium
