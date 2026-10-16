# 任务：处理需求变更

## 触发

用户修改、追加、删减已存在的需求，或提出的新信息与已定稿需求冲突。

## 步骤

1. **锁定基线。** 找到 `.project/requirements/requirements/REQ-xxx.yaml` 的当前版本。
   找不到基线时明确告知，不要凭会话记忆重建需求。

2. **生成 diff。** 逐字段对比：

   | diff 类型 | 含义 |
   |---|---|
   | `added` | 新增的需求、流程步骤、字段、AC |
   | `removed` | 删掉的项 |
   | `modified` | 值改变的项，写 `from` / `to` |
   | `conflicted` | 与已有内容冲突、无法自动合并的项 |

3. **影响分析。** 必须答出四个问题：

   - **哪些 AC 失效** —— 流程变了，对应的 Given/When/Then 必须重写
   - **哪些依赖方受影响** —— 有谁 `depends_on` 这条需求
   - **是否引入新的 P0 缺口** —— 变更后重跑一遍覆盖矩阵
   - **是否需要新的定位候选** —— 出现支付、多租户、合规等信号时写 `POS-CAND`

4. **归档。** 把当前版本复制到 `history/REQ-xxx/<version>.yaml`，再生成 `changes/<date>-REQ-xxx.yaml`。
   **不覆盖历史，版本号单调递增。**

5. **重跑覆盖矩阵。** 至少把受影响维度标为待复核；引入 P0 缺口时按 clarifier 步骤补问。

6. **重跑质量门禁。** 已通过的需求一旦变更，门禁结论立即失效，必须重新出具。
   `status` 从 `reviewed` 回退到 `changed`。

## 状态与版本语义

| status | 含义 |
|---|---|
| `draft` | 初稿或整改中 |
| `reviewed` | 通过质量门禁 |
| `approved` | 用户确认，可开发 |
| `implemented` | 已实现并验证 |
| `changed` | 已变更，待重新评审 |
| `rejected` | 质量门禁拒绝 |

版本号：小步修正递增小数位（`v0.1 → v0.2`）；语义级别变化递增整数位（`v0.2 → v1.0`）。

## 输出

- `changes/<date>-REQ-xxx.yaml`：diff + 影响分析
- `history/REQ-xxx/<old-version>.yaml`：归档快照
- 更新后的 `requirements/REQ-xxx.yaml`（新版本号）
- 更新后的 `traceability.md`
- 新的质量门禁结论

汇报时必须讲清：**改了什么、影响了谁、哪些验收要重写、门禁现在什么结论**。
不要用「已更新」一句话带过。
