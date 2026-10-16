# Requirement traceability matrix {{as_of}}

方向：来源 → 需求 → 验收标准 → 实现
反查：给定任一实现方式，可回到原始诉求。

> 机器可读版见 `traceability.yaml`，符合 `schemas/traceability.schema.yaml`。

## 正向追踪

| 来源 | 类型 | 需求 | 版本 | 验收标准 | 实现 | 状态 |
|---|---|---|---|---|---|---|
{{forward_rows}}

## 孤儿项

- 有来源但没有需求：{{orphan_sources}}
- 有需求但没有来源：{{orphan_requirements}}
- 有验收但没有对应测试：{{orphan_acceptance}}

> 每项为空时写「无」。不允许删除本节。

## 定位候选

第 {{candidate_count}} 条，等待项目定位 Skill 处理：

{{positioning_candidates}}

## 备注

{{notes}}
