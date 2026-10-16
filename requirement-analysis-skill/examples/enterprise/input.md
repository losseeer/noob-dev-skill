# 示例输入 · enterprise

来源：某企业客户的季度需求沟通（2026-10-12，会议记录摘录）

## 原始输入

> 我们需要把每个月的账单导出成 PDF，财务要留档，还要能显示每笔明细对应的订单。
> 导出的时候要留下操作日志，谁导的、什么时候导的、导出哪个账期。
> 另外我们有几条内部规定：账单数据只允许财务组的同事看，导出文件在服务器上保留 30 天就删掉。
> 导出别太快把系统卡死，大客户的账单一万多行。

## 输入特点

- 出现 **billing / audit / compliance** 三类定位信号 → 触发 `POS-CAND`
- 已有明确的内部硬约束（权限组、保留期限）→ 可以直接落成 AC
- 有一条性能线索（「一万多行」「别卡死」）但没有量化指标

## 期望结果

1. 需求卡写完后门禁 `pass`
2. 输出 3 条定位候选（`billing` / `audit` / `compliance`），并明确不越权决策
3. 演示 `requirement_set` 索引与追踪矩阵的写法
4. 演示拆分：主需求 REQ-010 拆出子需求 REQ-011（导出任务异步化探针）

## 本目录文件

| 文件 | 说明 |
|---|---|
| `coverage-REQ-010.yaml` | 覆盖矩阵，`positioning_context: read` |
| `REQ-010.yaml` | 主需求卡，门禁已通过 |
| `REQ-011.yaml` | 拆分出的子需求（异步导出 spike），体现 `parent` / `children` |
| `gate-REQ-010.yaml` | 质量门禁结果 `pass` |
| `current.yaml` | 需求集索引，符合 `requirement_set.schema.yaml` |
| `traceability.yaml` | 追踪矩阵机器可读版 |
| `positioning_candidates.yaml` | 3 条待项目定位 Skill 处理的候选 |

> 教学点：这是「完整闭环 + 桥接」示例。注意 `positioning_candidates.yaml` 里只有候选与理由，**没有任何一句结论说该需求该做或不该做**。
