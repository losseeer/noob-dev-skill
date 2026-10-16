# 任务：拆分需求与排执行顺序

## 触发条件

需求已通过质量门禁（`decision: pass`），且用户需要把它变成可执行的工作项。
未通过门禁时不拆——把没写清楚的需求拆开会放大歧义。

## 选策略

按 `rules/split_rules.yaml` 的 strategy_priority 依次尝试：

1. `acceptance_independence`：能单独写 Given/When/Then 的最小单元一个子需求（**默认策略**）
2. `user_value`：一个需求里塞了几种价值主张时
3. `risk`：存在未验证技术或外部依赖时，先 spike 再实现
4. `workflow_step`：主流程超过 7 步时按阶段切
5. `data_entity`：多个实体的 CRUD 各自独立时

一次拆出超过 7 个子需求 → 说明粒度分错层，换下一个策略（考核 SPL-007）。

## 硬性规则

- 每个子需求**可独立验收**，至少一条 AC 只依赖它自己（SPL-001）
- 每个子需求有明确 `actor` 与 `goal`，不能出现「配合 XXX」这种无主需求（SPL-002）
- 不允许环形依赖；有环时抽公共子需求打断（SPL-004）
- 子需求继承父需求 `trace.source`，并写 `trace.parent`（SPL-006）
- 优先垂直切片，不按前端/后端/测试分层拆（SPL-005）

## Spike（探针）

存在高风险且未验证的部分时，先出一个 spike：

- `goal`：验证某个不确定性，产出结论
- 验收形状：Given 待验证假设 / When 完成 <探针动作> / Then 输出结论与推荐方案
- 退出结论只能是三者之一：可行 / 不可行 / 换方案，必须附证据

spike 的验收标准里**不允许出现「用户可以…」**（见 anti_patterns）。

## 排顺序

按 `rules/priority_rules.yaml` 的 algorithm：

1. 按 `priority_rank` 分组（must > should > could > wont）
2. 组内做依赖拓扑排序，被依赖者先做
3. 高风险需求替换成「spike + 实现」两个节点，spike 在前
4. 拓扑同级时按价值密度降序
5. 再按垂直切片大小升序，小的先落地

## 输出

- 每个子需求一份需求卡 `requirements/REQ-xxx.yaml`
- 父需求写 `children`，子需求写 `parent`
- 有序的执行清单（编号 1..N），每个条目一行：
  `序号. REQ-xxx <标题> — <为什么在这个位置>`
- 未安排或延后的部分写进父需求 `out_of_scope` 或 `wont` 子需求

最后明确标注：**这份顺序是推荐值，用户可直接采用**（见 USER 偏好：每条决策都给推荐值，不是只列选项）。
