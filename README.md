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
PKG=<本包目录>
DEST=~/.workbuddy/skills

# 全装
rsync -a --exclude '.workbuddy/' --exclude 'dist/' --exclude 'outputs/' \
      "$PKG/project-positioning-skill"  "$DEST/"
rsync -a --exclude '.workbuddy/' --exclude 'dist/' --exclude 'outputs/' \
      "$PKG/requirement-analysis-skill" "$DEST/"
rsync -a --exclude '.workbuddy/' --exclude 'dist/' --exclude 'outputs/' \
      "$PKG/dev-companion"              "$DEST/"

# 只装其中一个也完全可以，例如
rsync -a --exclude '.workbuddy/' --exclude 'dist/' --exclude 'outputs/' \
      "$PKG/dev-companion" "$DEST/"
```

**为什么不能用裸 `cp -r`**：`.workbuddy/`（本机会话与项目笔记）、`dist/`（打包产物）、
`outputs/`（运行时产物）三项都写在包根 `.gitignore` 里，但 `cp -r` 不看 `.gitignore`，
会原样把它们拷进运行时安装目录。macOS 与主流 Linux 均自带 `rsync`。

没有 rsync 时，用 `cp -r` 装完后手动删掉各 skill 目录下的 `.workbuddy/`、`dist/`、`outputs/`。

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

三个 Skill 是同一套规范长出来的，不是三个独立作品。共有四条约束。

**四条在每个 Skill 里的落地形态不同，这是刻意的**——它们绑定的是各自不同的产物结构，
统一措辞会让约束变得不可判定。下表是四条原则在三处的实际形态：

| # | 原则 | ① 定位 | ② 需求 | ③ 开发陪伴 |
|---|---|---|---|---|
| 1 | 问题 ≠ 指令 | 路由第 1 条：只回答，不写文件 | 路由第 1 条：只回答，不写文件 | Do NOT use：纯问答不建树 |
| 2 | 不许把推断写成事实 | 覆盖矩阵每维度必标六状态：`explicit` / `inferred` / `missing` / `low_confidence` / `conflict` / `undecided` | 同左 | 完成证据不可空；「未验证」不得标 `[x]`；无 git 则如实写 `none`，不编 hash；不得新建空壳冒充历史 |
| 3 | 不许静默降级 | 安全合规证据不足时用 `risk_state: unresolved` 并判 `reject`，不得放行；Review 失败不得假装已确认 | `reject` 不得降级为 `pass`，门禁失败必须在 `decision` 里显式体现 | H6：脚本缺失 / Python 不可用 / 产物丢失，全部显式报告；不许当成 PASS 继续推进 |
| 4 | 单一真源 | 定位卡与覆盖矩阵同源；不写 `.project/positioning/` 之外的目录 | `REQ-xxx.yaml` 是需求卡唯一事实源 | `TREE.md` 唯一真源；进度行取 `check_tree.py --progress` 输出，不估算、不手抄校验脚本 |

改动其中一处的措辞时，回头检查另外两处是否也该动。

### 关于「抽成 `shared/`」

核对过的结论：**不做**。三条理由：

1. **会断链。** 安装方式是只拷 `<skill>/` 子目录（见上文），包级的 `shared/` 不会被拷过去，
   三个 `SKILL.md` 里的引用会指向不存在的路径。
2. **只有第 3 条真同源。** 第 1、2 条在 ③ 里换了一套词表（完成证据 / 未验证 / `none`），
   第 4 条在三处指向的对象各不相同。抽出来只能保留抽象表述，会丢掉上面表格里那些可判定的具体约束。
3. **与本包的设计决策冲突。**「互不调用、各自完整自洽」是写死的，引入共享文件等于引入运行时依赖。

上表本身就是对齐的产物，放在包级 README 给人看，不进 Skill 运行时。
