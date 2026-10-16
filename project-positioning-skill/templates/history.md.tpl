# 项目重定位记录 {{from_version}} → {{to_version}}

日期：{{date}}  
原因：{{reason}}  
迁移策略：`{{migration.strategy}}`

## 定位差异

{{#each differences}}
### {{dimension}}

- 之前：{{before}}
- 之后：{{after}}
- 影响：{{impact}}
- 必须动作：{{required_action}}
{{/each}}

## 迁移策略依据

{{migration.reason}}

## 回滚点

{{migration.rollback}}

## ADR

- 决策：{{adr.decision}}
- 依据：{{adr.rationale}}
- 被放弃方案：{{adr.alternatives}}

## 技术债

{{#each technical_debt}}
- **{{item}}**：责任 {{owner}}；触发 {{trigger}}；处理时机 {{due}}
{{/each}}
