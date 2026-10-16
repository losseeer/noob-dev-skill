# 定位 Review {{date}}

- 版本：`{{version}}`
- 状态：`{{status}}`
- Reviewer：{{reviewer}}

## 检查项

- [ ] 定位单一明确，能在一句话内说明用户、交付与价值
- [ ] 所有 P0 维度均有证据，没有 `missing` 或 `conflict`
- [ ] `do_now` 与当前阶段一致
- [ ] 每个 `do_not` 都有可检查的升级条件
- [ ] 每个 `undecided` 都有默认值与复审触发条件
- [ ] 约束包可执行，且与等级一致
- [ ] 没有提前实现仅需预留的能力
- [ ] 没有低估数据、安全、可靠性或合规要求
- [ ] 推断和默认值均可追溯到 source 或 rule ID
- [ ] 重定位触发条件可观察、可判断

## 阻塞项

{{#each blockers}}
- {{this}}
{{/each}}

## 结论

`{{decision}}`

可用结论：`approve` / `request_changes` / `insufficient_evidence`

## 备注

{{notes}}
