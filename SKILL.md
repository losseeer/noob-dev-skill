---
name: noob-dev
description: "Build a software project together with a beginner developer. Two capabilities: (A) always-on — keep a project development status tree at dev-tree/TREE.md whose checkbox nodes each record a decision and link to a version snapshot .md, branching a subtree on every 「which implementation」 or 「which task first」 decision the user answers; (B) on demand — explain things in plain language with no undefined jargon, conclusion first, then minimal runnable code, then step-by-step, then a glossary. Use when the user is building a project with an agent and asks 解释 / 看不懂 / 什么意思 / 用大白话 / 我是新手, or wants a visible, resumable plan that survives across sessions. Do NOT use for standalone questions about existing code with nothing being built, or for throwaway one-off scripts."
agent_created: true
---

# noob-dev

面向「用 agent 做项目的编程新手」的开发陪伴协议。

```text
用户目标
   │
   ├─ A. 项目开发状态树（always-on）      dev-tree/TREE.md + versions/*.md
   │      决策点 → 开子树 → 新版本快照 → 校验
   │
   └─ B. 大白话解释模式（on demand）      结论 → 最小可运行代码 → 逐步说明 → 术语表
```

两条能力优先级固定：**A 是地基**，只要在开发就得维护，用户没提也一样；**B 是开关**，触发后本次会话持续生效，用户说「不用解释」就关。

---

## When To Use

- 用户（尤其是新手）在用 agent 从零做项目、加功能、改 bug，需要一个能跨会话接上的进度记录。
- 用户要求「做个计划」「记录一下进度」「别让我下次来又要重说一遍」。
- 用户问为什么 / 看不懂 / 什么意思 / 用大白话——能力 B。

**Do NOT use：**

- 纯问答：只是解释现有代码、不改任何东西 → 直接回答，不建树。
- 一次性的临时脚本，写完就扔 → 不建树（用户明确要除外）。
- 用户已经明确说「别记了，直接做」→ 关闭 A 的状态树更新，但保留已有 TREE.md 不动。

---

## 硬规则（Hard Rules）

违反任意一条即视为本次任务失败，不是瑕疵。**唯一例外：用户当面、明确地撤销**（例如「别管树了赶紧写」），
此时按用户说的做，但下一轮开头要提醒一次欠的更新（见失败策略表）。

| # | 规则 |
|---|---|
| H1 | **树的更新优先于汇报。** 改完项目文件后，先更新 `dev-tree/TREE.md` 和版本文档，**再**向用户说话。禁止「先说完，树以后补」。 |
| H2 | **待完成节点必须是叶子。** 给节点加子节点时，父节点的交付目标必须已达成（详见 `references/tree-protocol.md` 第 3 节的冲突处置） |
| H3 | **每个决策点必须留痕。** 用户回答了「选哪个方案 / 先做哪个任务」，必须体现在树形和新版本文档里；明确放弃的候选删节点 |
| H4 | **标 `[x]` 必须有完成证据。** 版本文档里的完成证据允许写「未验证」，但**不允许为空**；写着未验证就不能标完成 |
| H5 | **改完树必跑校验。** `python <本 skill 目录>/scripts/check_tree.py <项目目录>`（路径见下方文件布局，脚本**不在**用户项目里），输出必须是 PASS。**PASS 不等于全部不变量都过了**——I4（兄弟顺序）、I5 的第 1/3/4 条、I6 的候选名与章节 `§x.y` 引用，脚本一行都没看（完整清单见 `references/tree-protocol.md` 第 3 节的「谁判定」列） |
| H6 | **不许把失败伪装成结果。** 脚本缺失、Python 不可用、TREE.md 丢失、`versions/` 缺文档——全部**显式报告**，不许当成 PASS 继续推进 |
| H7 | **树的产物只写项目本身。** `TREE.md` / `versions/*.md` 里禁止出现「根据某某规范第 X 条」这类协议元信息 |
| H8 | **问选择题必带推荐值。** 候选 ≤ 3，每个一句话写清代价，明确说推荐哪个、为什么 |
| H9 | **编号引用必须带锚点。** 引用节点 / 版本标签 / 候选 / `§x.y` 时，必须同时给出能定位到它的链接、全标题或归属；候选一律用 slug 命名（`302-redirect`），禁止「选 B」这种裸编号。详见 `references/tree-protocol.md` I6 |

---

## 文件布局

```
noob-dev/                          # 本 skill
├── SKILL.md
├── references/
│   ├── tree-protocol.md           # 能力 A 的完整协议（不变量、决策点、完成协议）
│   └── explain-mode.md            # 能力 B 的完整规范（含反模式清单与正反示例）
├── assets/
│   ├── TREE.template.md
│   └── version.template.md
├── scripts/check_tree.py          # 一致性校验，stdlib only，带 --selftest
└── examples/shortlink/            # 端到端示例，真实通过校验
```

**运行时产物落在用户项目里：**

```
<用户项目>/
└── dev-tree/
    ├── TREE.md                    # 唯一真源
    └── versions/NNN-slug.md       # 每个节点一个版本快照
```

校验脚本用**本 skill 目录里的那一份**，不要复制进用户项目（避免污染和版本漂移）。
因此**在用户项目根目录下执行 `scripts/check_tree.py` 是跑不通的**——你必须用下面的完整路径：

```bash
python ~/.workbuddy/skills/noob-dev/scripts/check_tree.py <用户项目目录>
python ~/.workbuddy/skills/noob-dev/scripts/check_tree.py --selftest   # 校验脚本自身
```

如果本 skill 装在别处（例如 `~/Dev/skills/noob-dev-skill`），把上面路径换成实际安装位置即可。

---

## Bootstrap：第一次进入一个项目

1. **先看，不要先问。** 读 `README.md`、包管理文件、源码目录，尽量从已有素材推断目标和栈。
2. 如果推断不出来，或推断出来的东西和用户想法有出入 → **最多问 3 个问题**，每个带推荐默认值。
3. 按 `assets/TREE.template.md` 创建 `dev-tree/TREE.md`，首个节点 = 「启动：确认目标与技术栈」（待完成叶子）。
4. 按 `assets/version.template.md` 创建 `versions/001-init.md`，写入当前项目状态。
5. 把 TREE.md 头部「当前活动节点」指向它，跑一次校验。

已有 `dev-tree/TREE.md` 时：**先读头部**，取「当前活动节点」，用 `--map` 看路径，然后从那个节点接着干，不要重开一棵。

---

## 每次回复前的自检（Pre-reply Checklist）

逐条过，不过就先补齐再回答：

1. 本轮动过项目文件吗？→ 树和版本文档是否已反映？
2. 本轮问了用户选择题吗？→ 那是决策点，用户回答后按下面的流程处理；**没回答就别先动树**。
3. 有节点标了 `[x]` 吗？→ 完成证据填了吗？
4. 跑 `check_tree.py` 了吗？→ 必须 PASS，或明确报告 FAIL 原因（H6）。
5. **本轮用了大白话解释模式吗？**（能力 B 已开启时）→ 四段顺序对吗（结论 → 最小可运行代码 → 逐步说明 → 术语表）？新术语 ≤ 3 个？术语首次出现都带括号解释和类比了吗？代码能直接复制跑吗？

---

## 决策点处理流程

用户回答了选择题之后，**按顺序**做：

```text
① 把候选对比表写进**当前节点已有的那份**版本文档（它是这个决策发生的地方，
   不要再新建一份——新建的那份没人引用会触发 E4 孤儿）
   表里的候选用 slug 命名（302-redirect，不要 A/B/C）
   最后一列「落地节点」必填：
       D1 方案选型：推荐行 → 链到它产生的节点；落选行 → 写「不产生节点」
       D2 任务排序：每行都 → 链到它最终对应的节点（候选只是排后，不是被淘汰）
② 当前活动节点：
     - 若它还没达成 → 把标题改写成「已达成的事实」（如「XX：方案定稿」）
     - 标 [x]，并在版本文档补完成证据
③ 在它下面建子树：
     D1 方案选型 → 子节点 = 选定方案的落地任务
     D2 任务排序 → 子节点 = 用户排好序的任务，建成兄弟（同一父节点下），自上而下即顺序
④ 给③里每个新建的子节点各建一个版本文档（完成证据先写「未验证」）
   漏掉这步会触发 E2/E3 卡在⑦，流程走不下去
⑤ 用户明确放弃的候选 → 删除该节点**及其子树**，它对应的版本文档**同步删除**（否则变孤儿触发 E4），
   并在父版本文档留一行「已放弃：X（原因）」
⑥ 更新头部「当前活动节点」→ 指向新建的第一个待完成叶子
⑦ 跑校验，PASS 后才向用户汇报
```

**降级**：不产生新任务的纯参数选择（颜色、端口号、变量名）**不开子树**，只在当前版本文档的决策记录里追加一行。

---

## 节点完成流程

满足全部四条才能标 `[x]`：

1. 交付目标（版本文档第 1 节）已实现；
2. 完成证据写了验证命令 + 实际输出摘要；**没做就写「未验证」，此时不得标完成**；
3. 版本文档的「项目状态」更新到当下（文件清单、怎么跑起来）；
4. TREE.md 头部的最近校验行更新。

---

## 失败策略（Failure Policy）

| 情况 | 处置 |
|---|---|
| Python 不可用 / 脚本跑不起来 | **显式告诉用户「本轮没有校验」**，并说明退化原因。不许默默跳过 |
| `versions/` 下有文档丢失 | 显式报告缺失文件名；**不得新建一个空壳冒充历史**，按现状重建并标注「历史缺失」 |
| 用户项目未初始化 git | 不影响协议，版本文档不依赖 git；但要在版本文档里如实写 git 状态为 none |
| 树被改坏了（E1/E6 等） | 停下开发，先修树。带着具体行号告诉用户哪里不对 |
| 用户要求「别管树了赶紧写」 | 按用户说的做，但在下一轮开头提醒一次「树还欠一次更新」，然后继续 |

---

## 反模式（Anti-patterns）

- 把树写成任务清单而不是决策记录——每个版本文档必须有「为什么这么做」。
- 一口气问 5 个问题。一次一个决策点，候选 ≤ 3，带推荐。
- 为了让树好看而拆分 trivial 步骤（开个文件也算一个节点）。
- 汇报里讲「我更新了状态树」当成果——用户关心的是项目进展，树的更新是义务不是成果。
- 解释时先讲社区最佳实践，再给结论 → 违反能力 B，见 `references/explain-mode.md`。
- 在同一个节点上反复追加决策，从不 `标 [x]` —— 树会变成一条长流水账。
- 候选只写 `A/B/C`，回复里说「选 B」——候选编号是决策点**局部**的，隔一轮就无法消歧（H9）。
- 以为候选起了个好名字就能追踪——**追踪靠候选表的「落地节点」列，命名只解决可读性**。

---

## 详细协议

- 能力 A 全部细节（书写契约、不变量推导、两种格式、边界记录）→ `references/tree-protocol.md`
- 能力 B 全部细节（四段结构、术语规则、反模式、正反示例）→ `references/explain-mode.md`
- 可运行的端到端样例 → `examples/shortlink/`
