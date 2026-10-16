# 任务：跑覆盖矩阵与确定缺口

在初始覆盖矩阵基础上，决定每一项是跳过、给默认值，还是必须问。

## 输入

`prompts/01_parse_input.md` 产出的覆盖矩阵、`rules/coverage_rules.yaml`、`rules/default_rules.yaml`、`rules/conflict_rules.yaml`。

## 处置矩阵

严格按 `rules/coverage_rules.yaml` 的 `handling` 执行：

| 状态 | P0 | P1 | P2 |
|---|---|---|---|
| `missing` | **必须问** | 默认值 + 记录 | 默认值，不打扰 |
| `conflict` | **必须问** | 必须问 | 必须问 |
| `low_confidence` | 追问一句 | 追问一句 | 记为假设 |
| `undecided` | 默认值 + `review_trigger` | 同左 | 默认值 |
| `explicit` | 跳过 | 跳过 | 跳过 |
| `inferred` | 跳过，保留 source | 跳过 | 跳过 |

关键禁忌：

- **禁止用默认值绕过 P0 `missing`**（COV-001）
- **禁止默认化解 conflict**，哪怕某一项看起来更合理（COV-002）
- 每个默认值都要能追溯到 `rule_id`（COV-005）

## 处理步骤

1. **应用默认值。** 对允许默认处理的维度，从 `rules/default_rules.yaml` 取对应条目，
   写入 `defaults_applied`，每条包含 `dimension` / `value` / `rule_id` / `reason` / `review_trigger`。
   同时把该项的覆盖矩阵 `status` 更新为 `inferred` 或在 P2 场景保持原状但记录。

2. **登记跳过项。** 对 `explicit` 与可靠 `inferred` 的维度写入 `skipped`，
   `reason` 要具体到「为什么不必再问」，不能写「已明确」。

3. **生成待问清单。** 对每个必须问或追问的维度生成一条 question：
   - `id`：`Q1` 起递增
   - `prompt`：用 `rules/coverage_rules.yaml` 里该维度的 `question_when_missing` 作为基础措辞
   - `options`：2-4 个，每个带 `impact`
   - `recommendation`：**必须给**，这是用户不响应时的默认执行值
   - `rule_id`：命中的规则

4. **重排问题顺序。**
   `conflict` 优先 → P0 `missing` 次之 → `low_confidence` 再次 → `undecided` 最后。
   同级按维度在 `priorities` 里的出现顺序。

5. **重新判定 `ready_for_modeling`。** 满足以下全部才置 `true`：

   - 没有 P0 维度处于 `missing`
   - 没有 `conflict`
   - 每个 `undecided` 都有默认值与 `review_trigger`
   - 每个应用的默认值都有 `rule_id`

## 输出

更新 `.project/requirements/coverage/REQ-xxx.coverage.yaml`，并汇报：

- 本轮一共几条待问（不超过 3 条进入下一轮提问，其余排队）
- 应用了哪些默认值，每个值的复审触发条件
- 跳过了哪些项及原因
- 是否达到建模条件；未达到时明确指出卡在哪个维度
