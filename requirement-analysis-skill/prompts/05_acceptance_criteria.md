# 任务：写验收标准

统一使用 Given / When / Then。目标是「任何一个不了解需求的人都能照着判断通过与否」。

## 编号

`AC-001` 起递增，`requirement_id` 字段回填所属需求。

## 必须覆盖的场景

按 `rules/quality_rules.yaml` 的 QC-003 逐个走：

| scenario | 说明 |
|---|---|
| `happy_path` | 主流程顺利走完 |
| `empty_data` | 没有数据时展示什么 |
| `duplicate` | 重复提交同一件事 |
| `permission_denied` | 有权限边界但越权访问 |
| `unauthenticated` | 未登录时访问 |
| `network_failure` | 网络或依赖失败 |
| `boundary` | 空值、最大长度/数量 |
| `concurrency` | 并发操作同一资源（适用时） |
| `idempotency` | 重复请求的幂等结果（写操作） |

**不适用的场景不能留空。**必须在 `test_notes` 里写「XXX 场景不适用：<原因>」。
留空和「确认过不需要」是两种状态（DEF-015）。

## 写法要求

- `given`：前置状态，必须是可以被构造出来的
- `when`：恰好一个动作
- `then`：可观测结果，可以多条，每条单独一个断言
- 禁止在 `then` 里写主观判断（「感觉很快」「界面友好」）
- 禁止把实现细节写进 `then`（例如「调用了 update_user 方法」）——只写外部可观测结果
- 权限类断言要写清被拒时的具体表现，不能只写「拒绝访问」

## 量化而非形容

| 不要这样 | 要这样 |
|---|---|
| 响应要快 | P95 < 500ms（本地网络，单次请求） |
| 支持大量数据 | 支持单篇文章 ≤ 10 万字 |
| 失败要有提示 | 展示「网络异常，重试」按钮，不刷新当前输入 |

## 与优先级联动

- `must`：必须覆盖 happy_path + 全部 exception_flows 对应的场景（PRIO-001）
- `should`：至少 happy_path + 主要异常
- `could`：至少 happy_path
- `wont`：不写验收标准，但对应内容必须进入 `out_of_scope`（PRIO-002）

## 输出

把 `acceptance_criteria` 填回需求卡；把「不适用的场景 + 原因」填进 `test_notes`。
每条 AC 的 `scenario` 字段必须显式填，不允许省略。
