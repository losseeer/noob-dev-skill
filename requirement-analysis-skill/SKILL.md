---
name: requirement-analysis-skill
description: Convert fuzzy ideas, user feedback, issues, chat logs, or code comments into reviewable, versioned, AI-readable requirement artifacts. Produces coverage matrices, requirement cards with Given/When/Then acceptance criteria, quality gate results, traceability matrices, split plans, and change diffs. Trigger on 需求分析 / 帮我分析这个需求 / 这个需求怎么写 / 需求澄清 / 需求评审 / 验收标准 / 需求变更 / 需求拆分, or before development splitting and requirement review. Do NOT use for deciding whether a requirement should be done at all — that is the scope gate owned by project-positioning-skill.
---

# Requirement Analysis Skill

把模糊输入翻译成「可以进入开发」的需求规格：一组 requirement card + 可测试的 acceptance criteria + 质量门禁结论 + 追踪矩阵。

与 `project-positioning-skill` 的分工是一句话：

> 项目定位 Skill 决定「做不做」，需求分析 Skill 决定「做成什么样才算完成」。

两者只通过文件约定协作，不互相调用。

## 边界（不可越界）

| 本 Skill 不做 | 归属 |
|---|---|
| 定义项目类型、等级、用户规模、收费、合规等级、关键性 | 项目定位 Skill |
| 生成项目级 `do_now` / `do_not` / `reserved` | 项目定位 Skill |
| 判断某需求是否在项目定位范围内 | 项目定位 Skill （`requirement_gate`） |
| 输出定位卡、重定位 | 项目定位 Skill |

硬性约束：

- 不依赖项目定位 Skill，不要求定位卡存在。
- 可选读取 `.project/positioning/current.yaml`，**只作上下文**（`summary` / `constraints` / `glossary`）。
- **绝不修改**定位卡，也**不读** `do_not` / `reserved` 来做范围拒绝。
- 本 Skill 里的「范围」只指**单个需求或迭代**的 `out_of_scope`。
- 发现可能影响定位时，只写一条 `POS-CAND-xxx` 候选，**不自己决策**。

## 先判定任务类型

按以下顺序路由：

1. 用户仅询问概念、方案或某需求是否值得做时，只回答问题，不写文件。
2. 已有需求产物且用户提出修改、追加、删减时，执行**变更管理**（步骤 8）。
3. 已有需求产物且用户要求 review 或评审时，执行**质量门禁**（步骤 6）+ review 文档。
4. 已有通过门禁的需求卡，用户要求排期或开发顺序时，执行**拆分与计划**（步骤 7）。
5. 其余新想法、用户反馈、Issue、聊天记录、「帮我分析这个需求」，执行**完整流程**（步骤 1-6，按需 7-9）。

**变窄规则**：若用户只要求其中一步（例如「只写验收标准」），只执行该步骤，并把缺的上游信息标为 `missing` 后显式告知，不静默补跑全流程。

## 证据与状态

按以下优先级使用信息：

1. 用户当前明确陈述
2. 用户提供的已有需求产物与定位卡
3. Issue / 聊天记录 / README / 已有代码事实
4. 合理推断
5. 用户接受的默认值

每个覆盖维度必须标记一种状态：

- `explicit`：明确说了
- `inferred`：可合理推断；必须记 `source` 与 `reason`
- `missing`：完全没提
- `low_confidence`：说了但模糊
- `conflict`：前后矛盾；必须提供 ≥ 2 条证据
- `undecided`：明确说「还没想好」；必须给默认值 + `review_trigger`

禁止把推断写成明确事实。禁止用默认值绕过 P0 `missing` 或 `conflict`。

## 核心流程

### 1. 解析输入

读取 `prompts/01_parse_input.md`。只抽取，不提问。
输出符合 `schemas/coverage.schema.yaml` 的**每个候选需求一份**初始覆盖矩阵。

### 2. 覆盖矩阵与缺口

读取 `prompts/02_coverage_gap.md`、`rules/coverage_rules.yaml`、`rules/default_rules.yaml`、`rules/conflict_rules.yaml`。

维度优先级（见 `rules/coverage_rules.yaml`）：

- P0：`actor` `goal` `trigger` `main_flow` `acceptance` `data` `exception` `permission`
- P1：`preconditions` `alternate_flow` `non_functional` `interface` `dependency`
- P2：`glossary` `trace` `risk` `test_notes`

处置：

- P0 `missing` → 必须问
- `conflict` → 必须问，并引用冲突证据
- P1 `missing` → 应用默认值并记录 `rule_id` + `review_trigger`
- P2 `missing` → 直接默认，不打扰
- `explicit` / 可靠 `inferred` → 跳过

### 3. 自适应澄清

读取 `prompts/03_adaptive_clarify.md`。每轮最多 3 题，生活化语言，不要求用户懂需求工程术语。

- 每题给 A/B/C + 「其他（请填写）」
- 标注「推荐」选项及依据（用户在超时或未授权时，默认执行推荐值）
- 冲突题先摆证据再问
- 用户答「还没想好」→ 采用推荐默认值，标 `undecided` 并记触发复审条件

回答后立即重跑覆盖矩阵与冲突检测，可能引入新一轮问题。

### 4. 需求建模

读取 `prompts/04_model_requirement.md` 与 `templates/requirement.yaml.tpl`。
产出用户故事、主/备用/异常流程、数据输入输出、实体、接口、权限、非功能需求、单需求 `out_of_scope`。
遵循 `schemas/requirement.schema.yaml`；每条 conflict 或 default 都写回 `assumptions` / `open_questions`。

### 5. 验收标准

读取 `prompts/05_acceptance_criteria.md`。统一 Given / When / Then，`AC-xxx` 编号。
必须覆盖：正常路径、空数据、重复操作、权限不足、未登录、网络失败、边界值，以及并发或幂等（如适用）。
不适用的场景要在 `test_notes` 里显式写明「不适用 + 原因」，不允许留空糊过去。

### 6. 质量门禁

读取 `prompts/06_quality_gate.md` 与 `rules/quality_rules.yaml`。七项检查：
`unambiguous` `testable` `complete` `consistent` `feasible` `traceable` `prioritized`。

决策语义：

- `pass`：可进入开发
- `revise`：列出整改项，补充后重新评审
- `reject`：需求质量不可接受，需重写请求

**这不是范围门禁。** 一个需求通过本门禁不代表它该做；该不该做由项目定位 Skill 决定。
`reject` 不得被降级为 `pass` 输出；门禁失败必须在 `decision` 里显式体现。

### 7. 拆分与计划

读取 `prompts/07_split_and_plan.md` 与 `rules/split_rules.yaml`、`rules/priority_rules.yaml`。
按 `user_value` / `workflow_step` / `data_entity` / `risk` / `acceptance_independence` 拆分。
每个子需求必须可**独立验收**且有明确 actor 与 goal；高风险或不确定项优先做探针（spike）。

### 8. 变更管理

读取 `prompts/08_change_manage.md`。变更时：生成 diff → 影响分析 → 更新追踪矩阵 → 归档到 `history/` → **重新过质量门禁**。
版本号单调递增，永不覆盖历史。

### 9. 可选定位桥

读取 `prompts/09_optional_positioning_bridge.md`。

- 存在 `.project/positioning/current.yaml` → 只读 `summary` / `constraints` / `glossary`，不修改、不调用对方 Skill
- 不存在 → 标记「定位上下文未知」，**不阻塞**
- 检出可能影响定位的信号（支付、多租户、合规、SLA…）→ 写入 `.project/requirements/positioning_candidates.yaml`，附 `action: 建议交给项目定位 Skill 做范围门禁`

## 产物约定

```text
.project/requirements/
  current.md                 当前对话正在处理的需求集摘要（人类读）
  current.yaml               需求集索引（机器读）
  coverage/
    REQ-001.coverage.yaml    每需求一份覆盖矩阵
  requirements/
    REQ-001.yaml             需求卡（唯一事实源）
  reviews/
    2026-10-15-v0.1.md       门禁 + review 记录
  changes/
    2026-10-15-REQ-001.yaml  变更 diff 与影响分析
  history/
    REQ-001/
      v0.1.yaml              归档的历史版本
  traceability.md            来源 → 需求 → 验收 → 实现 的追踪矩阵
  positioning_candidates.yaml 给项目定位 Skill 的候选（可选）
```

写入前创建缺失目录。日期统一 `YYYY-MM-DD`。
ID 约定：`REQ-\d{3}` / `AC-\d{3}` / `Q\d+` / `POS-CAND-\d{3}` / 版本 `^v\d+\.\d+$`。

## 资源索引

- 解析输入：`prompts/01_parse_input.md`
- 覆盖矩阵：`prompts/02_coverage_gap.md`
- 自适应澄清：`prompts/03_adaptive_clarify.md`
- 需求建模：`prompts/04_model_requirement.md`
- 验收标准：`prompts/05_acceptance_criteria.md`
- 质量门禁：`prompts/06_quality_gate.md`
- 拆分与计划：`prompts/07_split_and_plan.md`
- 变更管理：`prompts/08_change_manage.md`
- 可选定位桥：`prompts/09_optional_positioning_bridge.md`
- 维度与处置规则：`rules/coverage_rules.yaml`
- 门禁规则：`rules/quality_rules.yaml`
- 冲突检测：`rules/conflict_rules.yaml`
- 默认值：`rules/default_rules.yaml`
- 拆分规则：`rules/split_rules.yaml`
- 优先级规则：`rules/priority_rules.yaml`
- Schema：`schemas/`
- 产物模板：`templates/`
- 完整示例：`examples/`
- 校验脚本：`scripts/validate_artifact.py`
- CI 工作流模板：`assets/requirement-check.yml`
