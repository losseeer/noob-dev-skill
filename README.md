# noob-dev

给**用 AI agent 做项目的编程新手**用的开发陪伴 skill。三条能力：

| | 能力 | 触发 | 解决什么 |
|---|---|---|---|
| A | 项目开发状态树（`dev-tree/TREE.md`） | **always-on** | 每次决策留痕，节点链到版本快照，换会话能接着干 |
| B | 大白话解释模式 | 按需 | **看不懂**——结论先行、零未定义术语、最小可运行代码 |
| C | 行动优先模式 | 按需 | **做不到**——第一行给动作、编号步骤、每轮重述进度 |

B 和 C 可以同时开：B 管措辞深度，C 管输出形状，冲突时 C 的形状优先。

C 的进度行直接读状态树的真实数字（`[2/7 已完成] · 你在：A › B › C`），
不是让模型自己估——这是它和原版 `i-have-adhd`（ayghri/i-have-adhd, MIT）最大的不同。

---

## 安装

```bash
cp -r /path/to/noob-dev-skill ~/.workbuddy/skills/noob-dev
python ~/.workbuddy/skills/noob-dev/scripts/check_tree.py --selftest
```

自检输出形如 `selftest: N passed, 0 failed` 即安装正常（**看 `failed` 是否为 0**，不要核对 N 的具体数值——随版本会变）。零依赖（只用 Python 标准库）。

---

## 它会在你的项目里放什么

```
你的项目/
└── dev-tree/
    ├── TREE.md              # 状态树，唯一真源
    └── versions/
        ├── 001-init.md
        └── 002-....md       # 每个节点一个版本快照
```

`TREE.md` 长这样（checkbox 就是状态，链接跳版本快照）：

```markdown
- [x] 启动：确认目标与技术栈 — [v001](versions/001-init.md)
    - [x] 搭最小骨架，能本地跑起来 — [v002](versions/002-skeleton.md)
        - [x] 跳转方式定稿（301 / 302） — [v003](versions/003-redirect-choice.md)
            - [ ] 实现 /s/<code> 的 302 跳转 — [v004](versions/004-redirect-impl.md)
            - [ ] 生成 6 位短码 — [v005](versions/005-shortcode.md)
        - [ ] 用 SQLite 存短链映射 — [v006](versions/006-sqlite.md)
        - [ ] 加一个简单的管理页面 — [v007](versions/007-admin.md)
```

规则：`[ ]` 待完成的必须是叶子；标 `[x]` 必须有验证记录；兄弟从上到下 = 你决定的执行顺序。

---

## 日常用法

```bash
# 常规校验（每次改完树都跑）
python ~/.workbuddy/skills/noob-dev/scripts/check_tree.py ./我的项目

# 看当前在干哪一步（路径面包屑）
python ~/.workbuddy/skills/noob-dev/scripts/check_tree.py ./我的项目 --map

# 出图（mermaid，可贴到 GitHub / 预览器）
python ~/.workbuddy/skills/noob-dev/scripts/check_tree.py ./我的项目 --mermaid

# 一行进度（行动优先模式 C 直接复制这一行）
python ~/.workbuddy/skills/noob-dev/scripts/check_tree.py ./我的项目 --progress
# → [3/7 已完成] · 你在：启动 › 搭骨架 › 跳转定稿 › 实现跳转

# 给 CI 或脚本用
python ~/.workbuddy/skills/noob-dev/scripts/check_tree.py ./我的项目 --json
```

退出码：`0` 通过 / `1` 有错 / `2` 找不到树或有节点解析不出来。

---

## 错误码

| 码 | 含义 | 怎么修 |
|---|---|---|
| E1 | 待完成节点有子节点 | 要么先做完父节点，要么把还没做的事拆到别处 |
| E2 | 节点缺版本文档链接 | 补 `[vNNN](versions/NNN-x.md)` |
| E3 | 版本文档不存在 | 补文件或改链接 |
| E4 | 孤儿版本文档（没人引用） | 接上节点，或删掉 |
| E5 | 版本标签重复 | 一个标签只能给一个节点 |
| E6 | 层级跳级 | 补全中间层，或修正缩进 |
| E7 | 已完成节点没有完成证据 | 补验证命令 + 输出；真没验证就写「未验证」并且**不要**标完成 |
| E8 | 头部当前活动节点非法 | 它必须是树上存在、且待完成的节点 |
| E9 | 正文引用了树上不存在的 `vNNN` | 改成真实存在的标签，或把漏掉的节点补上 |
| E10 | 候选表缺「落地节点」列，或推荐行该列没写清 | 候选名（含 slug）不提供追踪能力，**追踪靠这一列** |
| E11 | 版本链接不在 `dev-tree/versions/` 下，或不是 `.md` | 链接必须指向版本目录里的 `.md` |
| E12 | 表格格式的节点 ID 重复 | ID 必须唯一，否则层级会塌陷 |
| W1 | 版本文档缺「交付目标」 | 补一句话的可验证目标 |
| W2 | 标题含 TODO/TBD 等占位符 | 写清楚到底要做什么 |
| W4 | 版本标签是裸写，没写成链接 | 写成 `[vNNN](versions/NNN-x.md)`，带上锚点 |

**注意**：`check_tree.py` 只判定不变量的一部分。I4（兄弟顺序 = 执行顺序）、I5 的第 1/3/4 条、
I6 的候选与章节引用**脚本一行都没看**——PASS 不是放行条，见 `references/tree-protocol.md` 第 3 节。

---

## 目录

| 文件 | 内容 |
|---|---|
| `SKILL.md` | 主入口：路由、硬规则、bootstrap、决策点与完成流程、失败策略 |
| `references/tree-protocol.md` | 状态树完整协议：书写契约、不变量推导、两种书写格式、边界记录 |
| `references/explain-mode.md` | 能力 B 大白话解释模式：四段结构、术语规则、反模式、正反示例 |
| `references/action-first-mode.md` | 能力 C 行动优先模式：十条输出整形规则、与状态树的三处裁决 |
| `assets/TREE.template.md` | 状态树初始模板 |
| `assets/version.template.md` | 版本快照模板 |
| `scripts/check_tree.py` | 一致性校验（`--map` / `--mermaid` / `--json` / `--selftest`） |
| `examples/shortlink/` | 短链服务端到端示例，真实通过校验 |
