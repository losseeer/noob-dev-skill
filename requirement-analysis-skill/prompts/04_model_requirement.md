# 任务：把需求建模成需求卡

## 前置条件

覆盖矩阵必须满足 `rules/coverage_rules.yaml` 的 exit_criteria。
未满足时不得建模——回去补澄清，不要用「假设」把坑填平假装完成。

## 步骤

1. **写用户故事。** 一句 `作为 <actor>，我要 <能力>，以便 <价值>`。
   多个 actor 时分别写，不要混成「作为用户」。

2. **写主流程。** 有序列表，每步必须是**可被观测到发生了没有**的动作。
   「系统处理数据」这种不可观测的描述必须拆成「校验 X」「写入 Y」「返回 Z」。

3. **写备用流程。** 不走主路径但不是失败的情况（例如未登录、已存在、走批量通道）。

4. **写异常流程。** 至少覆盖：
   - 网络失败
   - 数据校验失败
   - 越权/未登录

   每条异常流程必须写清：用户看到什么、数据停留在什么状态、能不能重试。
   适用时套用 `rules/default_rules.yaml` 的 DEF-002 / DEF-003 / DEF-006。

5. **定义数据。** `inputs` / `outputs` / `entities` 都要具名。
   涉及持久化时补 `retention`。

6. **定义接口。** 仅在确实存在跨系统调用时写。
   `method` 从 enum 里选；`request` / `response` 给出字段形状；有幂等要求时写 `idempotency_key`。

7. **定义权限。** 每条写清「谁能做」+「其他人被拒时看到什么」。
   未说明时套 DEF-005（仅本人可读写）。

8. **写非功能需求。** 必须可量化：数字 + 单位 + 条件。
   未说明时延/量级时套 DEF-009。**禁止出现「快速」「稳定」「友好」这类词**（QC-001）。

9. **写 `out_of_scope`。** 只写**本需求不包含**的事项，不写项目级边界。
   每条建议附一句话说明放到哪一期，避免变成悬空条目。

10. **回填假设与开放问题。** 所有未经用户确认的处理，必须落在 `assumptions` 或 `open_questions`。
    两者区别：`assumptions` 是按某条 rule 推断且可逆；`open_questions` 是必须用户回答的。

11. **优先级。** 按 `rules/priority_rules.yaml` 的 MoSCoW 取值。默认 `should`。
    涉及越权、数据丢失、资金的不得降级（PRIO-003）。

## 硬性规则

- `actors` 与 `triggers` 至少各一项，且 actors 不能只有「用户」一个模糊词
- `exception_flows` 至少一项
- `trace.source` 必须来自解析阶段，找不到就写 `unknown` 并在 `open_questions` 说明
- `status` 初始一律 `draft`，`reviewed` 只能由质量门禁写入
- `version` 从 `v0.1` 起

## 输出

符合 `schemas/requirement.schema.yaml` 的需求卡，写入
`.project/requirements/requirements/REQ-xxx.yaml`。

同时用 `templates/requirement.md.tpl` 生成人类可读版，写进 review 记录或 `current.md`。
