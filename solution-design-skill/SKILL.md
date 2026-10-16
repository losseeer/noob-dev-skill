---
name: solution-design-skill
description: Turn accepted requirements into a reviewable technical solution and, when there is UI, a runnable interactive prototype. Produces technology selections with traceable basis, architecture layout, data model, interface contracts, ADRs, and a review record. Trigger on 技术方案 / 怎么实现 / 技术选型 / 架构怎么设计 / 数据模型 / 接口设计 / 数据库怎么设计 / 画个原型 / 做个能点的 demo / 先看一下交互长什么样, or after requirements are settled and before implementation starts. Do NOT use for deciding whether something should be done — that is the scope gate owned by project-positioning-skill. Do NOT use for writing requirement cards, acceptance criteria, or reviewing requirement wording — that is owned by requirement-analysis-skill. Do NOT use for explaining concepts in plain language, tracking day-to-day build progress, or asking what to do next once implementation has started — those are owned by dev-companion-skill.
---

# Solution Design Skill

把已经确定要做的需求翻译成「可以开工」的技术方案，涉及 UI 时再给出一个能点、能看的交互原型。

一句分工：

> 定位决定**做不做**，需求决定**做成什么样**，**方案设计决定怎么解**，开发陪伴负责**真的做下去并记得住**。

与另外三个 Skill **只通过文件约定协作，不互相调用**。

## 边界（不可越界）

| 本 Skill 不做 | 归属 |
|---|---|
| 判断某需求该不该做、是否在范围内 | 项目定位 Skill（`requirement_gate`） |
| 定义需求本身、写验收标准、review 需求措辞 | 需求分析 Skill |
| 解释概念、记录日常开发进度 | 开发陪伴 Skill |
| **写实现代码** | 开发陪伴 Skill（本 Skill 只到「可 review 的方案和原型」为止） |
| 上下游 Form-data、UI 视觉稿的最终定稿 | 由用户 review 决定 |

硬性约束：

- 不依赖另外两个 Skill，不要求它们的产物存在。
- 可选读取 `.project/positioning/current.yaml` 的 `constraints` 与 `non_functional_priority`，
  **只作约束输入，不修改、不调用**。
- 可选读取 `.project/requirements/` 下的需求卡与验收标准，同样只读。
- 上游文件不存在时记 `not_found`，**不阻塞、不报错、不要求用户先补齐**，
  但要在 `note` 里写清因此少了哪些依据。
- **不得自行放宽上游 constraints**。约束不合理只能记 `escalated_to_positioning`，
  交回项目定位 Skill，本 Skill 不自行放宽。

## 先判定任务类型

按顺序路由：

1. **纯打听类不归本 Skill，本条只作误路由兜底**：用户只是问某个技术怎么选、
   某个架构怎么看、某个概念什么意思，**没说要开工** → 归 `dev-companion-skill` 的能力 B，
   详见下方裁决表。若已被路由进来 → 只回答，不写文件，不启动本 Skill 的流程。
2. 已有设计方案且用户提出修改 → 走**步骤 4-8**，并递增版本号，不覆盖历史。
3. 已有设计方案且用户要求 review → 走**步骤 6**，出 review 记录。
4. 已有设计方案且用户要原型 → 只走**步骤 7**。
5. 其余「需求已定、要开工」的请求 → 走**完整流程**（步骤 1-8，按需跳过 7）。

**变窄规则**：用户只要求其中一步（例如「只做技术选型」），只执行该步，
其余产出在 `current.yaml` 里标 `gap` 并显式告知，不静默补跑全流程。

## 相邻 Skill 的归属裁决

平台只靠 `description` 路由，四个 Skill 同时装必然有边界模糊的请求。路由层判不清时按下面裁决：

| 情形 | 归属 |
|---|---|
| 「用 A 还是 B 实现」——技术选型本身 | **本 Skill**，产出 `stack.yaml` + ADR |
| 「先做哪个任务」「下一步干嘛」——选型已定后的排序 | `dev-companion-skill`（本轮还在做选型时除外） |
| 「做个能点的 demo」「画个原型」 | **本 Skill**，原型登记进 `current.yaml`，不是一次性产物 |
| 写完就扔的一次性临时脚本 | `dev-companion-skill`：仍用能力 B/C 回答，但**不建树**；它不是任何 Skill 的设计产物 |
| 「这是什么意思」「用大白话讲讲」——只解释不落文件 | `dev-companion-skill`（能力 B），本 Skill 不接 |
| 「这个技术方案该怎么设计」——要出产物 | **本 Skill** |
| 正在开发中且已有 `dev-tree/TREE.md` 当前活动节点，问下一步 | 让位给 `dev-companion-skill`，本 Skill 不接 |

## 证据与依据

这是本 Skill 落地「不许把推断写成事实」的形态——**不是六状态枚举，而是选型依据四分类**。
两者服务于不同对象，不要互相套用。

每条技术选型必须标记一种 `basis`：

- `constraint`：来自上游定位卡的约束；**必须写 `source_ref`** 指向具体字段
- `requirement`：来自上游验收标准；同样必须写 `source_ref`
- `assumption`：推断；**必须写 `why_assumed` 与 `revisit_when`**（schema 强制）
- `user_choice`：用户明确选择的；写清从哪得知

禁止把 `assumption` 写成 `requirement`。禁止给 `constraint` 型选型不写 `source_ref`。

## 核心流程

### 0. 脚本自测（可选但推荐）

```bash
python <本 skill 目录>/scripts/validate_bundle.py --selftest
# 输出 selftest: 7 passed, 0 failed 即校验脚本本身没问题
```

### 1. 解析输入

读取 `prompts/01_parse_input.md`。只读不提问。输出 `current.yaml` 的 `upstream` 与 `coverage` 骨架
（每条 AC 一条，先标 `gap`）。

### 2. 提取约束

读取 `prompts/02_constraint_extract.md`、`rules/stack_rules.yaml`、`rules/constraint_rules.yaml`。
把定位卡维度映射到选型面，逐条比对冲突，每条冲突必须有 `disposition`。

### 3. 需求映射

读取 `prompts/03_requirement_mapping.md`。把每条 AC 落到接口 / 实体 / 页面 / 决策，
填 `covered_by`。`covered` 或 `partial` 时 `covered_by` 不得为空。

### 4. 技术选型

读取 `prompts/04_tech_selection.md` 与 `templates/stack.yaml.tpl`。
候选 ≤ 3 且**必须给推荐值**（用户超时或未授权时默认执行推荐值）。
非平凡选型写 ADR 到 `decisions/`，必须含「代价」与「复审条件」两节。

### 5. 结构设计

读取 `prompts/05_structure_design.md`。产出 `tech/data-model.yaml`、`tech/interfaces.yaml`、
`tech/layout.md`。**本 Skill 不写实现代码。**

### 6. 方案校验与 Review

读取 `prompts/06_solution_review.md` 与 `rules/review_rules.yaml`。

先**跑脚本**（不可跳过）：

```bash
cd <本 skill 目录>/scripts && python validate_bundle.py
```

再做七项人工检查写进 `reviews/<date>-<version>.yaml`。

决策语义：

- `approve`：七项全过且无 `blocker` → `status: reviewed`
- `request_changes`：保持 `draft`，列整改项
- `insufficient_evidence`：选型性状无法判定 → 保持 `draft`，先补最小事实

**校验脚本跑不起来必须显式报告，不许写成 `passed: true`。**

### 7. UI 原型（仅涉及前端 UI 时）

读取 `prompts/07_ui_prototype.md`。**每次都要问用户技术栈并给推荐值**，
默认推荐纯 HTML 单文件 + CDN（零构建、双击即开）；项目已有 Vue/React 栈时改推对应项。

产出到 `prototype/`，必须能直接打开跑。
**本目录内容不进 schema 校验**，只有 `current.yaml` 里的页面清单受校验。

### 8. 交付摘要

读取 `prompts/08_handoff.md`。写出 `.project/design/current.md` 与交付清单。
**不调用 `dev-companion-skill`**，只留文件。

## 产物约定

```text
.project/design/
  current.yaml               方案索引（机器读，进 schema）
  current.md                 人类读摘要 + 交付清单
  tech/
    stack.yaml               技术选型记录（每条带 basis）
    architecture.md          分层与模块边界
    data-model.yaml          数据模型（每个字段带 basis）
    interfaces.yaml          接口契约（每条带 acceptance_refs）
    layout.md                目录结构（不进 schema）
  decisions/
    ADR-001-<slug>.md        每条非平凡选型一条 ADR
  reviews/
    <date>-<version>.yaml    review 记录
  prototype/                 ← 不进 schema 校验
    _index.md                页面清单 + review 要点
    index.html               可交互页面，双击即开
```

写入前创建缺失目录。日期统一 `YYYY-MM-DD`。
ID 约定：`SEL-\d{3}` / `IF-\d{3}` / `ADR-\d{3}` / `ASM-\d{3}` / `CONF-\d{3}` / `AC-\d{3}`（沿用上游）/ 版本 `^v\d+\.\d+$`。
版本号单调递增，永不覆盖历史。

## 本 Skill 的四条共享原则形态

与其他三个 Skill 同源，但落地形态不同（详见包 README 的对照表）：

1. **问题 ≠ 指令** → 路由第 1 条：只讨论技术不落文件时，只回答，不写文件。
2. **不许把推断写成事实** → 选型 `basis` 四分类；`assumption` 强制带 `why_assumed` + `revisit_when`。
3. **不许静默降级** → 校验脚本跑不起来、原型打不开、上游文件缺失，全部显式报告。
4. **单一真源** → `current.yaml` 是索引唯一真源；`prototype/` 页面只由 `current.yaml` 登记，
   不手写第二份清单。

## 资源索引

- 解析输入：`prompts/01_parse_input.md`
- 提取约束：`prompts/02_constraint_extract.md`
- 需求映射：`prompts/03_requirement_mapping.md`
- 技术选型：`prompts/04_tech_selection.md`
- 结构设计：`prompts/05_structure_design.md`
- 方案 Review：`prompts/06_solution_review.md`
- UI 原型：`prompts/07_ui_prototype.md`
- 交付摘要：`prompts/08_handoff.md`
- 选型默认值与约束绑定：`rules/stack_rules.yaml`
- 冲突检测：`rules/constraint_rules.yaml`
- Review 七项：`rules/review_rules.yaml`
- Schema：`schemas/`
- 产物模板：`templates/`
- 完整示例：`examples/shortlink/`
- 校验脚本：`scripts/validate_artifact.py`（单产物）与 `scripts/validate_bundle.py`（交叉引用与示例一致性，带 `--selftest`）
- CI 工作流模板：`assets/solution-check.yml`
