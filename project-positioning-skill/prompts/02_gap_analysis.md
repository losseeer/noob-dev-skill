# 任务：生成覆盖矩阵与缺口

基于解析结果决定哪些信息必须追问、哪些可以推断、哪些可以使用默认值。

## 优先级

- P0：`users`、`criticality`、`data`、`charging`、`compliance`
- P1：`scale`、`downtime`、`data_loss`、`delivery`、`enterprise`、`contractual_obligation`、`audit_required`
- P2：`experience`、`budget`、`maintenance`、`rewrite`、`i18n`

`auth` 在数据为 `sensitive` 或 `regulated` 时按 P0 处理，其余情况按 P1；`stage`、`form`、`data_sensitivity`、`regulation` 根据上下文映射到最相关优先级，可能改变等级或合规结论时按 P0 处理。

## 判定顺序

1. 运行 `rules/conflict_rules.yaml`；命中后标记 `conflict`。
2. 对 P0 的 `missing` 或所有 `conflict` 生成必问题。
3. 对 `low_confidence` 生成一个最小澄清问题。
4. 对可靠的 `inferred` 保留结论，不提问。
5. 对 P1/P2 的 `missing`，按 `rules/default_rules.yaml` 判断是否可默认；`scale`、`enterprise` 等影响等级的维度缺失时必须问，不能静默默认。
6. 对 `undecided` 给出推荐默认值，并记录复审触发条件。
7. 应用默认值后重新执行冲突检测；若默认值造成 blocking 冲突，撤销该默认值并加入待问清单。

## 硬约束

- P0 不得因“常见”“大概率”而静默默认。
- 默认值必须记录规则 ID、理由与触发重审条件。
- 一条问题只解决一个核心歧义；能合并选项说明时不要拆成多题。
- 已有明确答案不得再次提问。

## 输出

更新符合 `schemas/coverage.schema.yaml` 的 YAML：

- `coverage`：完整维度状态
- `questions`：按 P0、P1、P2 排序的待问项
- `skipped`：已检查但条件不适用、且没有应用默认值的维度及原因
- `defaults_applied`：已接受或规则允许的默认值；应用默认值的维度不得重复放入 `skipped`

将更新后的完整矩阵写回 `.project/positioning/coverage.yaml`。
