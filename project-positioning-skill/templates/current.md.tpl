# 项目定位卡 {{version}}

状态：{{status}}  
更新时间：{{updated}}  
一句话：{{summary}}

## 结论

- 定位类型：`{{positioning.type}}`
- 等级：`{{positioning.level}}`
- 当前阶段：`{{positioning.stage}}`
- 用户：{{#each positioning.users}}`{{this}}` {{/each}}
- 规模：`{{positioning.scale}}`
- 交付：`{{positioning.delivery}}`
- 收费：`{{positioning.charging}}`
- 关键性：`{{positioning.criticality}}`
- 合规：`{{positioning.compliance}}`
- 数据敏感度：`{{positioning.data_sensitivity}}`
- 非功能优先级：{{#each non_functional_priority}}`{{this}}` {{/each}}

## 现在做

{{#each do_now}}
- **{{item}}**：{{reason}}
{{/each}}

## 暂时不做

{{#each do_not}}
- **{{item}}**：{{reason}}
  - 升级条件：{{upgrade_trigger}}
{{/each}}

## 只预留边界

{{#each reserved}}
- **{{item}}**：仅保留 {{boundary}}；触发条件：{{trigger}}
{{/each}}

## 未定项与默认值

{{#each undecided}}
- **{{key}}**：默认 `{{default}}`。{{reason}} 复审条件：{{review_trigger}}
{{/each}}

## 关键约束

- 架构：`{{constraints.architecture}}`
- 数据库：`{{constraints.database}}`
- 部署：`{{constraints.deploy}}`
- 认证：`{{constraints.auth}}`
- 多租户：`{{constraints.multi_tenant}}`
- 审计：`{{constraints.audit}}`
- 备份：`{{constraints.backup}}`
- 测试：`{{constraints.testing}}`
- 监控：`{{constraints.monitoring}}`
- 维护预算：`{{constraints.maintenance_budget}}`

## 重定位触发条件

{{#each reposition_triggers}}
- `{{id}}`：{{condition}}
{{/each}}

{{#if glossary}}
## 术语表

{{#each glossary}}
- **{{term}}**：{{definition}}
{{/each}}

{{/if}}
## 变更历史

{{#each history}}
- {{date}} · {{version}} · {{change}}
{{/each}}
