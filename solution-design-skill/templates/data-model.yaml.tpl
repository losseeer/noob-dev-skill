version: 1
storage_selection_ref: SEL-000      # 指向 stack.yaml 里的存储选型
entities:
  - name: ""
    source_refs: []                 # REQ-xxx
    purpose: ""
    fields:
      - name: id
        type: INTEGER
        required: true
        unique: true
        basis: derived
      - name: ""
        type: ""
        required: false
        basis: requirement          # requirement / derived / assumption
        validation: ""
        note: ""
      # basis: assumption 时必须写 why_assumed，否则校验不过
    indexes:
      - fields: [""]
        kind: unique                # primary / unique / index / composite
        reason: ""                  # 说不出理由的索引不要写
    relationships: []
migration_note: ""
