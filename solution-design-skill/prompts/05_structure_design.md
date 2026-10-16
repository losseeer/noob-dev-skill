# 步骤 5：结构设计

## 目的

把选型落成具体的可实现结构：数据长什么样、接口长什么样、代码怎么摆。

## 产出三份

### `tech/data-model.yaml`

- 每个 entity 的 `source_refs` 追到 `REQ-xxx`。
- 每个 field 标 `basis`：`requirement`（需求里有约束）/ `derived`（由实现自然推出）/
  `assumption`（猜的，`basis: assumption` 时 schema 强制要有 `why_assumed`）。
- 每条 index 必须写 `reason`，**写了索引但说不出为什么，等于白占写入开销**。

### `tech/interfaces.yaml`

- 每条接口的 `acceptance_refs` 至少要有一条，指向它承担的 AC。
- `kind` 按 schema 的 `dependencies`：
  - `http` 必须给 `method` 和 `path`
  - `cli` 必须给 `path`
  - `page` 必须给 `page_ref`
  - `event` / `internal` 两者都不需要
- `errors` 要呼应上游 `exception_flows`。需求里写了异常分支但这里没有错误码，是覆盖缺口。

### `tech/layout.md`

目录结构与模块边界。这份是 Markdown，**不进 schema**，给人看。
写清每个目录的职责边界，以及哪些边界不允许被跨越（例如「UI 层不直接碰数据库」）。

## 硬性约束

- 本 Skill 到此为止，**不写实现代码**。动手写代码由 `dev-companion-skill` 承接。
- 数据与接口的字段命名要统一；同一个概念跨两份文件出现，必须同名。
- 本步骤结束后，`current.yaml` 的 `coverage` 里应当不再有 `status: gap`，
  除非明确标了 `skipped` 并在 `note` 里引用上游 `out_of_scope`。

## 反模式

- 数据模型里塞进需求从未提到的字段，且不标 `basis`——后面没人知道它是哪来的。
- 接口只写成功分支，异常全留空。
