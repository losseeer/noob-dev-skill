# 步骤 3：需求映射

## 目的

把上游每张卡的 `acceptance_criteria` 落到本方案的具体产物上，让「有没有被照顾到」变成可判定的。

## 做什么

逐条处理 `REQ-xxx.yaml` 的 `acceptance_criteria`：

1. 每条 AC 登记进 `current.yaml` 的 `coverage`，带 `requirement_ref`。
2. 判断它该由什么承担：

| AC 的类型 | 落到 |
|---|---|
| 描述外部可见行为（返回什么、跳转到哪） | `interfaces` |
| 描述数据约束（唯一、必填、累计） | `entities` 的字段或索引 |
| 描述页面上的交互 | `pages` |
| 是一组方案的取舍 | `decisions` |

3. `status` 取值：

- `covered`：已有明确的接口 / 字段 / 页面承担
- `partial`：只覆盖了一部分，要在 `note` 里写清缺什么
- `gap`：本轮没做进方案，**必须在 `open_questions` 或 `out_of_scope` 里交代**
- `skipped`：需求明确不在范围内（来自上游 `out_of_scope`），要在 `note` 里引用来源

## 硬性约束

- `status` 为 `covered` 或 `partial` 时，`covered_by` 至少要有一项非空。
  `validate_bundle.py` 会检查这一点——**写空等于把未完成说成已完成**。
- 上游 `assumptions` 里没解决的项目，原样进本方案的 `open_questions`，不许悄悄消化掉。
- 本步骤不改需求卡，也不替用户决定某条 AC 要不要做。

## 反模式

- 所有 AC 一律标 `covered` 然后忘了填 `covered_by`。
- 某个 AC 做不了，就把它从 `coverage` 里删掉——应该标 `gap` 或 `skipped` 并说明。
