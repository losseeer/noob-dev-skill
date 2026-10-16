# 任务：解析已有输入

只从现有材料抽取定位变量，不提问，不生成最终定位结论。

## 输入

- 开发者原始描述
- README、需求草稿、ADR（如有）
- 已有定位卡（如有）

## 维度

至少检查：

`users`、`scale`、`charging`、`data`、`data_sensitivity`、`compliance`、`criticality`、`delivery`、`stage`、`maintenance`、`budget`、`form`、`regulation`、`downtime`、`data_loss`、`enterprise`、`contractual_obligation`、`audit_required`、`auth`、`experience`、`rewrite`、`i18n`。

其中 `form` 用于确定产品形态与交付边界，`experience` 用于控制方案复杂度；二者不直接决定等级，但会约束实施方案。条件不适用时也要在 `skipped` 中记录原因。

## 状态判定

- `explicit`：材料直接陈述，保留原文引用
- `inferred`：可由多个事实合理推出，写出推理依据与置信度
- `missing`：完全没有相关证据
- `low_confidence`：只有含糊线索或证据不足
- `conflict`：两个及以上来源得出不兼容结论
- `undecided`：用户明确说“没想好”“待定”等

## 规则

1. 不把常见做法当成项目事实。
2. 不把“未提及”直接解释为 `false`、`low` 或 `none`。
3. 每个非 `missing` 项记录 `source`；冲突项保留所有证据。
4. 推断项必须记录 `reason` 和 `confidence`。
5. 只输出解析结果，不提出问题。

## 输出

输出符合 `schemas/coverage.schema.yaml` 的 YAML，并保存到 `.project/positioning/coverage.yaml`。顶层使用：

```yaml
version: 1
as_of: YYYY-MM-DD
coverage: []
questions: []
skipped: []
defaults_applied: []
```

此阶段的 `questions`、`skipped`、`defaults_applied` 保持空数组。
