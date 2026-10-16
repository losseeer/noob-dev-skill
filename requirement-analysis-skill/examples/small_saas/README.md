## small_saas · 冲突检测与 revise

一句话概况：一句话里埋两处自相矛盾，被冲突规则抓出来，初稿门禁 `revise`。

### 关键节点

| 环节 | 这里发生了什么 |
|---|---|
| 解析 | 「别让人注册」与「要看到谁加入的」同时出现 → CON-002 + CON-007 |
| 缺口 | `exception` 初稿只覆盖网络失败，令牌类异常缺失，标 `low_confidence` |
| 澄清 | Q1 追问异常覆盖；未答则执行 `recommendation` 并标记 `undecided` |
| 建模 | 冲突按推荐值收敛：邮箱 + 验证码的免密加入，取代完全匿名 |
| 验收 | 6 条 AC，缺 `unauthenticated` 场景 |
| 门禁 | `unambiguous` 与 `complete` 两项 fail → `revise` |

### 看这个示例要看什么

1. **冲突不是靠直觉取一边。** `conflicts` 里每条都附两条原文证据，且写明 `resolution` 依据。
2. **revise 不是失败。** 它把「 vague word」和「缺场景」精确定位到字段级（`non_functional[0]`），改两处即可复跑。
3. **需求卡里保留了 `assumptions`**，把冲突消解的结果显式记下来，而不是悄悄写进主流程。
