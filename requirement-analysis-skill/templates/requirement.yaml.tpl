# Requirement card skeleton
# Rule set: schemas/requirement.schema.yaml
# Copy -> .project/requirements/requirements/REQ-xxx.yaml
# Required fields must be filled before quality gate; missing values are not allowed to be faked.

id: REQ-000            # REQ-\d{3}
title: ""              # 一句话标题
version: v0.1          # ^v\d+\.\d+$
status: draft          # draft|reviewed|approved|implemented|changed|rejected
type: functional       # functional|non_functional|data|interface|constraint
priority: should       # must|should|could|wont，见 rules/priority_rules.yaml
user_story: ""         # 作为 <actor>，我要 <能力>，以便 <价值>

actors: []             # 至少 1 项，含边界角色（未登录用户、管理员等）
goal: ""               # 为了解决什么问题，不是「做了什么」
value: ""
source: ""             # 找不到就写 unknown，并在 open_questions 说明

preconditions: []
triggers: []           # 至少 1 项
main_flow: []          # 至少 1 项，每步必须可观测

alternate_flows: []
#  - name: ""
#    when: ""
#    steps: []

exception_flows: []    # 至少 1 项
#  - name: "网络失败"
#    when: ""
#    steps:
#      - "提示失败"
#      - "保留用户输入，允许重试"
#      - "记录结构化日志"

data:
  inputs: []
  outputs: []
  entities: []
  retention: ""

interfaces: []
#  - name: ""
#    method: POST      # GET|POST|PUT|PATCH|DELETE|EVENT|WEBHOOK|CLI|OTHER
#    request: {}
#    response: {}
#    errors: []
#    idempotency_key: ""
#    auth: ""

permission: []         # 至少 1 项，写清「谁能做」+「被拒时看到什么」
non_functional: []     # 必须可量化：数字 + 单位 + 条件

acceptance_criteria: []  # 至少 1 项
#  - id: AC-001
#    scenario: happy_path   # happy_path|empty_data|duplicate|permission_denied
#                           # |unauthenticated|network_failure|boundary
#                           # |concurrency|idempotency|other
#    given: ""
#    when: ""
#    then: ""

out_of_scope: []       # 仅本需求不包含项，不写项目级边界
dependencies: []
assumptions: []        # 按某 rule_id 推断且可逆的处理
open_questions: []     # 必须用户回答的问题
risks: []
#  - description: ""
#    level: medium
#    mitigation: ""
#    probe: ""

test_notes: []         # 不适用的标准场景必须写「不适用 + 原因」
glossary: []
#  - term: ""
#    definition: ""

trace:
  source: ""
  source_type: unknown   # user_feedback|issue|chat|code|document|meeting|other|unknown
  related: []
  parent: ""
  realization: []

updated_at: YYYY-MM-DD
parent: ""
children: []
history: []
