# 任务：生成项目定位卡

综合覆盖矩阵与问卷答案，生成可执行、可 review、可版本化的定位卡。

## 前置门槛

出现以下任一情况时停止生成并列出阻塞项：

- P0 仍为 `missing`
- 任一维度为 `conflict`
- 风险相关推断没有 source 或 reason

## 生成步骤

1. 读取 `rules/level_rules.yaml`，选择满足条件的最高等级。
2. 用一句话明确服务对象、交付形态与核心价值。
3. 根据等级和证据排列 `non_functional_priority`。
4. 生成可执行约束：架构、数据、部署、认证、租户、审计、备份、测试、监控。
5. 生成 `do_now`：当前阶段必须完成的最小集合。
6. 生成 `do_not`：每项包含 `item`、`reason`、`upgrade_trigger`。
7. 生成 `reserved`：只保留接口、数据边界或迁移点，不提前实现功能。
8. 生成 `undecided`：每项包含默认值、理由、触发重审条件。
9. 生成可观察的 `reposition_triggers`，避免“以后需要时”这类不可判定表述。
10. 写入来源摘要与版本历史。

## 版本与状态

- 首次生成使用 `v0.1` 和 `draft`。
- 每次重定位使用未被占用的下一个版本。
- 用户明确确认后才能改为 `reviewed`。
- `frozen` 只用于用户明确要求冻结的基线。
- 被新版本替代的旧版本标记为 `superseded`，但不覆盖归档文件。

## 输出

1. `.project/positioning/coverage.yaml`：保留最终覆盖矩阵与默认值来源
2. `.project/positioning/current.yaml`：符合 `schemas/positioning.schema.yaml`
3. `.project/positioning/current.md`：按 `templates/current.md.tpl` 渲染
4. `.project/positioning/reviews/<date>-<version>.md`：按 `templates/review.md.tpl` 记录 review
5. 一句话确认摘要：定位、等级、当前范围、最大风险

模板使用 Handlebars-compatible 语法。渲染 YAML 模板时必须提供 `yaml` helper，用 YAML 库安全序列化标量；禁止直接拼接未转义字符串。

保持 `current.md` 一页可读；完整机器字段保留在 `current.yaml`。
