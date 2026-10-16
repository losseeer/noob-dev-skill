# 任务：执行重定位

在用户明确要求改变定位，或当前需求命中复审触发条件时，生成可回滚的新定位版本。

## 前置动作

1. 读取当前 `current.yaml`、`current.md`、`coverage.yaml`、最近 review 和相关 gate 结果。
2. 在 `.project/positioning/history/<old-version>/` 创建归档：复制 `current.md`、`coverage.yaml`，并把旧定位卡的归档副本写为 `current.yaml`，仅将其 `status` 改为 `superseded`。
3. 确认归档完整且通过 schema 校验后再写新版本；写入新版本前不修改现有 current 文件。

## 增量流程

1. 把新事实与旧覆盖矩阵合并，保留来源。
2. 只询问发生变化、缺少证据或产生冲突的维度。
3. 重新执行等级判定，不沿用旧等级作为默认答案。
4. 生成新版本定位卡与 review。
5. 归档副本状态为 `superseded`；除状态和归档元数据外，不改写旧版本的实质结论。

## 差异分析

至少比较：

- 用户与规模
- 数据模型、敏感度、保留与迁移
- 身份、权限与多租户
- 架构与集成边界
- 部署、可用性与恢复目标
- 测试与发布策略
- 监控、审计与维护预算
- 收费、合同、合规与监管

每项输出 `before`、`after`、`impact`、`required_action`。

## 迁移策略

从以下策略中选择一个，并说明依据：

- `none`：仅文档范围变化，不需要技术迁移
- `rewrite`：现有实现无法安全演进，且替换成本可控
- `strangler_fig`：需要逐步替换现有能力并维持服务
- `dual_run`：需要并行验证新旧路径的一致性
- `incremental`：可按兼容步骤逐项迁移

不要为了显得完整而默认“重写”。

## 输出

- 新 `current.yaml` / `current.md`
- `.project/positioning/history/<old-version>/`
- `.project/positioning/reviews/<date>-<new-version>.md`
- ADR：变更原因、策略、回滚点
- 技术债清单：责任、触发条件、处理时机
