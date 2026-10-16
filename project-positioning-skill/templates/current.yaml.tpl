version: {{yaml version}}
status: {{yaml status}}
updated: {{yaml updated}}
summary: {{yaml summary}}
positioning:
  type: {{yaml positioning.type}}
  level: {{yaml positioning.level}}
  stage: {{yaml positioning.stage}}
  users:
{{#each positioning.users}}
    - {{yaml this}}
{{/each}}
  scale: {{yaml positioning.scale}}
  delivery: {{yaml positioning.delivery}}
  charging: {{yaml positioning.charging}}
  criticality: {{yaml positioning.criticality}}
  compliance: {{yaml positioning.compliance}}
  data_sensitivity: {{yaml positioning.data_sensitivity}}
non_functional_priority:
{{#each non_functional_priority}}
  - {{yaml this}}
{{/each}}
constraints:
  architecture: {{yaml constraints.architecture}}
  database: {{yaml constraints.database}}
  deploy: {{yaml constraints.deploy}}
  auth: {{yaml constraints.auth}}
  multi_tenant: {{yaml constraints.multi_tenant}}
  audit: {{yaml constraints.audit}}
  backup: {{yaml constraints.backup}}
  testing: {{yaml constraints.testing}}
  monitoring: {{yaml constraints.monitoring}}
  maintenance_budget: {{yaml constraints.maintenance_budget}}
do_now:
{{#each do_now}}
  - item: {{yaml item}}
    reason: {{yaml reason}}
{{/each}}
do_not:
{{#each do_not}}
  - item: {{yaml item}}
    reason: {{yaml reason}}
    upgrade_trigger: {{yaml upgrade_trigger}}
{{/each}}
reserved:
{{#each reserved}}
  - item: {{yaml item}}
    boundary: {{yaml boundary}}
    trigger: {{yaml trigger}}
{{/each}}
undecided:
{{#each undecided}}
  - key: {{yaml key}}
    default: {{yaml default}}
    reason: {{yaml reason}}
    review_trigger: {{yaml review_trigger}}
{{/each}}
reposition_triggers:
{{#each reposition_triggers}}
  - id: {{yaml id}}
    condition: {{yaml condition}}
    action: reposition_review
{{/each}}
source_summary:
{{#each source_summary}}
  - dimension: {{yaml dimension}}
    status: {{yaml status}}
    source: {{yaml source}}
{{#if rule_id}}
    rule_id: {{yaml rule_id}}
{{/if}}
{{#if reason}}
    reason: {{yaml reason}}
{{/if}}
{{#if confidence}}
    confidence: {{yaml confidence}}
{{/if}}
{{/each}}
glossary: {{#if glossary}}{{else}}[]{{/if}}
{{#each glossary}}
  - term: {{yaml term}}
    definition: {{yaml definition}}
{{#if source}}
    source: {{yaml source}}
{{/if}}
{{/each}}
history:
{{#each history}}
  - date: {{yaml date}}
    version: {{yaml version}}
    change: {{yaml change}}
{{/each}}
