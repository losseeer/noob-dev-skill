# 步骤 4：技术选型

## 目的

对每个技术面做出有依据的选择，并把依据本身记下来。

## 读什么

`rules/stack_rules.yaml`（面清单、默认推荐值、约束绑定）与 `templates/stack.yaml.tpl`。

## 做什么

按 `area_defaults` 逐个面走。**先读用户现有项目**，有既定技术栈就跟随（省一轮决策），
读不到再用 `fallback` 默认值。

每个非平凡的选择写一条 `SEL-xxx`：

| 字段 | 要求 |
|---|---|
| `basis` | 四选一：`constraint` / `requirement` / `assumption` / `user_choice` |
| `source_ref` | `constraint` 与 `requirement` 型**必填**，指出依据来自哪个具体字段 |
| `why_assumed` + `revisit_when` | `assumption` 型**必填**（schema 强制，不写校验不过） |
| `alternatives` | 至少一条，每条要有 `rejected_because` |
| `decision_ref` | 非平凡选型要有对应的 ADR 文件 |

## 候选要给推荐值

候选 ≤ 3，每个一句话写清代价，**明确说推荐哪个、为什么**。
用户在超时或未授权时，默认执行推荐值——这一条和另外两个 Skill 的约定一致。

## 什么时候写 ADR

满足任一条件就写：

- 涉及成本或运维模式的改变
- 后续很难回头（存储、认证、部署形态）
- 本条目本来就有多个持平方案

ADR 模板见 `templates/adr.md.tpl`，必须写「代价」和「复审条件」两节，
**只写收益不写代价的 ADR 等于没写**。

## 硬性约束

- 一个 `area` 一条选型，不要在同一个面里堆多个方案再让用户挑。
- `locked_by_constraint: true` 的选型不接受用户当场改；要改必须走
  `escalated_to_positioning` 回上游。

## 反模式

- 所有选型都写 `basis: assumption` 然后不填 `why_assumed`——schema 会挡住，别绕。
- 因为没有实测数据却引入缓存、消息队列、微服务——没有证据的复杂度是纯负债。
