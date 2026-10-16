# noob-dev-skills

面向「用 AI agent 做项目」的一整套 Agent Skill，覆盖从「有个模糊想法」到「开发落地」的链路。

| 阶段 | Skill | 它决定什么 | 产物落在哪 |
|---|---|---|---|
| ① 定位 | `project-positioning-skill` | **做不做**——项目类型、等级、范围、这个需求该不该做 | `.project/positioning/*.yaml` |
| ② 需求 | `requirement-analysis-skill` | **做成什么样才算完成**——需求卡、验收标准、质量门禁 | `.project/requirements/*.yaml` |
| ③ 方案设计 | `solution-design-skill` | **怎么解**——技术选型、数据模型、接口契约、UI 原型 | `.project/design/` |
| ④ 开发 | `dev-companion-skill` | **怎么一步步做下去**——决策留痕、进度可接续 | `dev-tree/TREE.md` + `versions/*.md` |

一句话分工：

> 定位决定**做不做**，需求决定**做成什么样**，方案设计决定**怎么解**，
> 开发陪伴负责**真的做下去并记得住**。

## 四个 Skill 彼此独立

它们是四个**完整的 Agent Skill**，都能单独安装、单独使用。本仓库只是把它们放在一处分发与维护。

四者**只通过文件约定协作，不互相调用**——这是刻意的设计：

- 定位 Skill 不依赖需求 Skill，需求 Skill 也不依赖定位 Skill（定位卡存在时只作上下文）。
- 方案设计 Skill 只读上游产物，不存在时记 `not_found` 并继续，不要求用户先补齐。
- 任一环节缺失，后面的 Skill 都能独立工作，只是信息少一些。

所以你可以只装其中一个。

**链路是可以断的**：只想做技术选型不必先跑需求分析，只想写需求卡也不必先做定位。
各自的入口都不要求上游产物存在。

## 安装

把需要的 Skill 目录放到相应 agent 的 skills 目录下即可。
目录名必须与 `SKILL.md` 里的 `name` 字段一致——平台按这个识别。

## 目录结构

```
noob-dev-skills/
├── README.md                      # 本文件
├── project-positioning-skill/     # ① 项目定位
├── requirement-analysis-skill/    # ② 需求分析
├── solution-design-skill/         # ③ 方案设计（技术选型 + UI 原型）
└── dev-companion-skill/           # ④ 开发陪伴（原 noob-dev）
```

各 Skill 内部自带 `SKILL.md`、`prompts/` 或 `references/`、`schemas/`、`examples/`、`scripts/`。
