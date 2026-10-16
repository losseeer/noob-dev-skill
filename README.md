# noob-dev-skills

面向「用 AI agent 做项目」的一整套 Agent Skill，覆盖从「有个模糊想法」到「开发落地」的链路。

| 阶段 | Skill | 它决定什么 | 产物落在哪 |
|---|---|---|---|
| ① 定位 | `project-positioning-skill` | **做不做**——项目类型、等级、范围、这个需求该不该做 | `.project/positioning/*.yaml` |
| ② 需求 | `requirement-analysis-skill` | **做成什么样才算完成**——需求卡、验收标准、质量门禁 | `REQ-xxx.yaml` |
| ③ 开发 | `dev-companion` | **怎么一步步做下去**——决策留痕、进度可接续 | `dev-tree/TREE.md` + `versions/*.md` |

一句话分工：

> 定位决定**做不做**，需求决定**做成什么样**，开发陪伴负责**真的做下去并记得住**。

## 三个 Skill 彼此独立

它们是三个**完整的 Agent Skill**，都能单独安装、单独使用。本仓库只是把它们放在一处分发与维护。

三者**只通过文件约定协作，不互相调用**——这是刻意的设计：

- 定位 Skill 不依赖需求 Skill，需求 Skill 也不依赖定位 Skill（定位卡存在时只作上下文）。
- 任一环节缺失，后面的 Skill 都能独立工作，只是信息少一些。

所以你可以只装其中一个。

## 安装

每个 Skill 单独复制到 WorkBuddy 的 skills 目录。**复制子目录，不要复制整个包**：

```bash
# 全装
cp -r <本包目录>/project-positioning-skill ~/.workbuddy/skills/
cp -r <本包目录>/requirement-analysis-skill ~/.workbuddy/skills/
cp -r <本包目录>/dev-companion            ~/.workbuddy/skills/

# 只装其中一个也完全可以，例如
cp -r <本包目录>/dev-companion ~/.workbuddy/skills/
```

安装后目录名必须与各 `SKILL.md` 里的 `name` 字段一致（平台按这个识别）。

验证安装：

```bash
python ~/.workbuddy/skills/dev-companion/scripts/check_tree.py --selftest
# 输出形如 selftest: N passed, 0 failed 即正常（看 failed 是否为 0）
```

## 目录结构

```
noob-dev-skills/
├── README.md                      # 本文件
├── project-positioning-skill/     # ① 项目定位
├── requirement-analysis-skill/    # ② 需求分析
└── dev-companion/                 # ③ 开发陪伴（原 noob-dev）
```

各 Skill 内部自带 `SKILL.md`、`prompts/` 或 `references/`、`schemas/`、`examples/`、`scripts/`。

## 共享的设计原则

三个 Skill 是同一套规范长出来的，不是三个独立作品。共有四条，改任何一处都要一起改：

1. **问题 ≠ 指令。** 用户只是提问、没说要改什么时，只回答，不写文件。
2. **不许把推断写成事实。** 每个结论都要标证据状态（`explicit` / `inferred` / `missing` / `low_confidence` / `conflict` / `undecided`）。
3. **不许静默降级。** key 失效、文件丢失、解析丢弃、校验跑不起来——全部显式报告，不许当成通过。
4. **单一真源。** 状态只记一份，任何可视化都由脚本生成，不手写第二份。

## 待办

- [ ] 把上述"共享的设计原则"抽成 `shared/` 下的独立文件，三个 Skill 各自引用。
      目前这条原则在三个 Skill 里各写了一遍（措辞略有出入），是三份副本。
