---
name: project-positioning-skill
description: This skill should be used when starting a software project, reviewing a project's scope before requirements analysis, evaluating whether a new requirement fits the current positioning, or repositioning an existing project. It converts non-technical developer input into reviewable, versioned positioning artifacts and applies those artifacts as a requirement gate. Trigger on requests such as “帮我定位这个项目”, “这个需求该不该做”, “项目要不要升级定位”, or before substantial project planning. Do NOT use for writing requirement cards, acceptance criteria, or quality review of requirement wording — that is owned by requirement-analysis-skill. Do NOT use for choosing technology, designing data models or interfaces, or building UI prototypes — that is owned by solution-design-skill. Do NOT use for explaining concepts or tracking day-to-day build progress — that is owned by dev-companion.
---

# Project Positioning Skill

把开发者的生活化描述转换为可 review、可 diff、可版本化、可被 AI 读取的项目定位产物，并用该产物约束后续需求分析与开发。

## 先判定任务类型

按以下顺序路由：

1. **纯打听类不归本 Skill，本条只作误路由兜底**：若用户只是问某个概念什么意思、
   某个技术方案怎么看，应先去 `dev-companion`（概念解释）或 `solution-design-skill`
   （技术方案），详见下方裁决表。若已被路由进来 → 只回答，不写文件。
2. 已有 `.project/positioning/current.yaml` 且用户提出单个新需求时，执行需求门禁。
3. 已有定位卡，且命中 `reposition_triggers` 或用户明确要求改变定位时，执行重定位。
4. 用户要求 review 现有定位时，执行定位 review。
5. 其余新项目启动、需求分析前置或“帮我定位项目”请求，执行首次定位。

## 相邻 Skill 的归属裁决

平台只靠 `description` 路由，四个 Skill 同时装必然有边界模糊的请求。判不清时按下表裁决：

| 情形 | 归属 |
|---|---|
| 「这个需求该不该做」「要不要升级定位」「我的项目是什么类型」 | **本 Skill**（范围判定） |
| 「这个需求怎么写」「验收标准是什么」 | `requirement-analysis-skill` |
| 「用什么技术实现」「数据模型怎么设计」「画个原型看看」 | `solution-design-skill` |
| 「下一步干嘛」「术语看不懂」「进度到哪了」 | `dev-companion` |

判定的分界线是「这是范围问题还是实现问题」——只要问的是要不要、能不能、属于哪一类，就在本 Skill。

## 证据与状态

按以下优先级使用信息：

1. 用户当前明确陈述
2. 用户提供的已有定位卡
3. README、需求草稿和仓库事实
4. 合理推断
5. 用户接受的默认值

每个定位维度必须标记一种状态：

- `explicit`：用户明确陈述
- `inferred`：可由上下文合理推出；必须记录 source 与理由
- `missing`：没有证据
- `low_confidence`：有线索但不足以稳定判断
- `conflict`：证据互相矛盾
- `undecided`：用户明确表示尚未决定

禁止把推断写成明确事实。禁止静默应用会改变风险等级的默认值。

## 首次定位流程

### 1. 解析已有输入

读取 `prompts/01_parse_input.md`。只抽取，不提问。输出符合 `schemas/coverage.schema.yaml` 的初始覆盖矩阵，并写入 `.project/positioning/coverage.yaml`。

### 2. 分析缺口

读取 `prompts/02_gap_analysis.md`、`rules/default_rules.yaml` 与 `rules/conflict_rules.yaml`。生成：

- 覆盖矩阵
- 待问清单
- 可跳过清单及原因
- 已应用默认值清单

### 3. 自适应提问

读取 `prompts/03_adaptive_questionnaire.md`。每轮最多问 3 题，只问待问项：

- `conflict` 必须问，并引用冲突证据
- P0 的 `missing` 必须问
- `low_confidence` 只追问一句
- `undecided` 提供推荐默认值与触发重审条件
- `explicit` 与可靠的 `inferred` 不再问

用户回答后重新生成覆盖矩阵；仍有 P0 `missing`、任意 `conflict`，或 `undecided` 缺少用户知情的默认值与复审条件时，不得生成最终定位卡。

### 4. 生成定位卡

读取 `prompts/04_generate_positioning.md`、`rules/level_rules.yaml` 和模板。生成：

- `.project/positioning/current.yaml`
- `.project/positioning/current.md`
- `.project/positioning/reviews/<date>-<version>.md`

生成内容必须通过 `schemas/positioning.schema.yaml`。初始状态使用 `draft`；用户确认后改为 `reviewed`。不要把“未回答”伪装成“低风险”。

### 5. 给出确认摘要

用一段话汇报：定位类型、等级、当前做什么、明确不做什么、仍未决定什么。对每个 `do_not` 同时给出 `upgrade_trigger`。

## 需求门禁

读取 `prompts/05_gate_requirement.md`、当前定位卡和 `rules/gate_rules.yaml`。每个新需求单独输出一个符合 `schemas/requirement_gate.schema.yaml` 的结果；一次出现多个需求时逐条判定，不合并结论。

定位卡为 `frozen` 时，任何新增范围默认 `out_of_scope`，直到用户明确解冻并执行重定位 review。安全或合规证据不足时使用 `risk_state: unresolved` 并输出 `reject`，不得静默放行。

决策语义：

- `must`：定位核心路径不可缺少
- `should`：符合定位但不是核心路径
- `out_of_scope`：当前定位不做；记录升级条件，不直接实现
- `reject`：即使重定位也不应按当前请求实现，或存在未解决的安全、合规、预算硬约束

**不要与 requirement-analysis-skill 的质量门禁 `reject` 混用**：本 Skill 的 `reject` 是范围判定（定位上不能做），对方的 `reject` 是质量判定（需求描述不可接受、需重写）。两者同名不同义，不得互相解读或替代。

门禁结果默认写入 `.project/positioning/gates/<date>-<slug>.yaml`。仅当用户要求继续实现时，才进入后续开发。

## 重定位

读取 `prompts/06_reposition.md`。先归档，再生成新版本：

1. 将旧 `current.md`、`coverage.yaml` 与状态改为 `superseded` 的旧 `current.yaml` 归档到 `.project/positioning/history/<version>/`。
2. 只对发生变化或缺少证据的维度执行增量问卷。
3. 生成单调递增的新版本，不覆盖历史。
4. 输出数据、权限、架构、部署、测试、运维、合规差异。
5. 从 `重写`、`Strangler Fig pattern`、`双轨运行`、`渐进迁移` 中选择迁移策略并说明依据；没有迁移需求时明确写 `none`。
6. 记录 ADR、技术债、回滚点与 review 结论。

## 定位 Review

使用 `templates/review.md.tpl` 检查：

- 定位是否单一明确
- `do_now` / `do_not` 是否可执行
- 每个 `do_not` 是否有升级条件
- 每个 `undecided` 是否有默认值和复审触发条件
- 约束是否与等级一致
- 是否存在过度设计或设计不足
- 定位卡与覆盖矩阵是否存在无来源结论

将 review 记录写入 `.project/positioning/reviews/<date>-<version>.md`。状态转换规则：

- `approve` 且用户明确确认 → `reviewed`
- `request_changes` → 保持 `draft` 并列出阻塞项
- `insufficient_evidence` → 保持 `draft`，继续最小补问
- 只有用户明确要求冻结已确认基线时 → `frozen`

Review 失败时不得假装已确认。

## 与 requirement-analysis-skill 的可选协作（双向契约）

分工一句话：本 Skill 决定「做不做」，对方决定「做成什么样才算完成」。两边**只通过文件约定协作，不互相调用**。

对方负责：需求卡、验收标准、需求质量门禁、拆分与追踪矩阵。
本 Skill 负责：定位卡、范围门禁、重定位。

### 三条硬约束（保证两侧都能单独使用）

1. **读侧可选**：可选读取 `.project/requirements/positioning_candidates.yaml`。文件不存在、为空或格式不支持时记为 `not_found` / `skipped`，**不阻塞、不报错、不降级**，门禁照常按定位卡判定。
2. **写侧不跨目录**：只写 `.project/positioning/`，**绝不写 `.project/requirements/` 下任何文件**，包括不回写对方候选的 `status`。对方是否安装，不影响本 Skill 产物完整自洽。
3. **字段可选**：`glossary` 是定位卡的可选字段，不进 `required`；没有它定位卡照样通过 schema 校验。

违反以上任一条即视为把可选协作做成硬依赖，必须回退。

### 输入侧：定位变更候选

对方需求中出现支付、订阅、多租户、合规、SLA、审计、强监管、外部集成等信号时，会写 `POS-CAND-xxx` 候选到 `.project/requirements/positioning_candidates.yaml`，其 `decision_owner` 固定为 `project-positioning-skill`。

收到候选时：

- 把候选当作**门禁输入**，对对应需求执行范围门禁，不把候选本身当成结论。
- 候选命中 `reposition_triggers` 或 `do_not` 时，按门禁规则输出 `out_of_scope` 并记录升级条件。
- **不修改候选文件**；如需要回执，只在本 Skill 的门禁结果 `reason` 中引用候选 ID。
- 候选不存在时不做任何提示性假设，也不要求用户先跑需求分析。

### 输出侧：供对方只读的上下文

对方只会读取定位卡的 `summary`、`constraints`、`glossary` 三个字段，不会读 `do_not` / `reserved` 做范围拒绝。因此这三个字段必须保持准确、自解释；`glossary` 用于统一术语命名，避免同一概念出现多个叫法。

## 产物约定

```text
.project/positioning/
  current.md
  current.yaml
  coverage.yaml
  gates/
  history/
  reviews/
```

写入前创建缺失目录。所有变更保留历史，不覆盖旧版本。日期统一使用 `YYYY-MM-DD`。

本 Skill 不写 `.project/positioning/` 之外的任何目录；单独安装即可跑完整流程。

## 资源索引

- 解析输入：`prompts/01_parse_input.md`
- 缺口分析：`prompts/02_gap_analysis.md`
- 自适应提问：`prompts/03_adaptive_questionnaire.md`
- 生成定位卡：`prompts/04_generate_positioning.md`
- 需求门禁：`prompts/05_gate_requirement.md`
- 重定位：`prompts/06_reposition.md`
- Schema：`schemas/`
- 判定规则：`rules/`
- 产物模板：`templates/`（Handlebars-compatible；YAML 模板要求 `yaml` helper 安全序列化标量）
- 完整示例：`examples/`
- 单独使用保证：`glossary` 为可选字段，且示例 `small_saas`、`enterprise` 的定位卡不含 `glossary` 仍通过校验；`scripts/validate_bundle.py` 会检查这一点
- 校验脚本：`scripts/validate_artifact.py`（单个产物）与 `scripts/validate_bundle.py`（schema、规则字段与示例一致性）
- CI 工作流模板：`assets/positioning-check.yml`（复制到目标仓库的 `.github/workflows/`，并按实际 Skill 安装路径调整）
