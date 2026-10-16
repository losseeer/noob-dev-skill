# requirement-analysis-skill

把模糊输入翻译成「可以进入开发」的需求规格。

> 项目定位 Skill 决定「做不做」，需求分析 Skill 决定「做成什么样才算完成」。

## 一分钟上手

```
用户模糊输入
   │
   ├─ 1 解析输入          prompts/01    覆盖矩阵初稿（不提问）
   ├─ 2 覆盖矩阵与缺口    prompts/02    决定哪些要问、哪些用默认值
   ├─ 3 自适应澄清        prompts/03    最多 3 题，带推荐值
   ├─ 4 需求建模          prompts/04    REQ-xxx.yaml
   ├─ 5 验收标准          prompts/05    Given / When / Then
   ├─ 6 质量门禁          prompts/06    pass / revise / reject
   ├─ 7 拆分与计划        prompts/07    独立可验收 + 依赖拓扑排序
   ├─ 8 变更管理          prompts/08    diff + 影响分析 + 重跑门禁
   └─ 9 可选定位桥        prompts/09    只读定位卡，只写候选
```

最小闭环是 1-6，够用。7-9 按需。

## 与项目定位 Skill 的关系

两个 Skill 不互相调用，只通过文件约定协作：

| 方向 | 文件 | 约束 |
|---|---|---|
| 输入（可选） | `.project/positioning/current.yaml` | 只读 `summary` / `constraints` / `glossary`，**不修改**、**不读 do_not 做拒绝** |
| 输出（可选） | `.project/requirements/positioning_candidates.yaml` | 只记录候选，**不决策** |

本 Skill 不做的事：定义项目等级、判断该不该做、生成项目级 `do_now` / `do_not`。
这些都属于对方的范围门禁。

## 目录

```text
requirement-analysis-skill/
  SKILL.md                        主入口，先看这个
  prompts/  01..09                九个环节的指令
  schemas/  6 个 JSON Schema      coverage / requirement / requirement_set
                                  / quality_gate / traceability / positioning_candidate
  templates/ 7 个模板             md 给人看，tpl 给 agent 用
  rules/    6 个规则              coverage / quality / conflict / default / split / priority
  examples/ personal_tool         最小闭环，门禁 pass
            small_saas            冲突检测，门禁 revise
            enterprise            完整闭环 + 定位桥接 + 拆分
  scripts/  validate_artifact.py  本地校验
  assets/   requirement-check.yml CI 模板
```

> `examples/` 里为了便于对照，把每个产物放在同一层并用 `REQ-xxx.yaml` / `coverage-REQ-xxx.yaml` 命名；
> 真实项目请按下面「产物落位」的目录结构存放。

## 产物落位

```text
.project/requirements/
  current.md / current.yaml       需求集索引
  coverage/REQ-xxx.coverage.yaml  每需求一份覆盖矩阵
  requirements/REQ-xxx.yaml       需求卡（唯一事实源）
  reviews/<date>-<version>.yaml   门禁结论
  changes/<date>-REQ-xxx.yaml     变更 diff
  history/REQ-xxx/<version>.yaml  历史归档
  traceability.yaml               追踪矩阵
  positioning_candidates.yaml     给项目定位 Skill 的候选
```

## 本地校验

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r scripts/requirements.txt

python scripts/validate_artifact.py requirement  .project/requirements/requirements/REQ-001.yaml
python scripts/validate_artifact.py coverage     .project/requirements/coverage/REQ-001.coverage.yaml
python scripts/validate_artifact.py quality_gate .project/requirements/reviews/2026-10-15-v0.1.yaml
```

支持的 kind：`coverage` / `requirement` / `requirement_set` / `quality_gate` / `traceability` / `positioning_candidate`。

examples 下的产物也可以直接校验，例如：

```bash
python scripts/validate_artifact.py requirement     examples/personal_tool/REQ-001.yaml
python scripts/validate_artifact.py coverage        examples/enterprise/coverage-REQ-010.yaml
python scripts/validate_artifact.py quality_gate    examples/small_saas/gate-REQ-002.yaml
```

## CI

把 `assets/requirement-check.yml` 复制到目标仓库的 `.github/workflows/`：

- 校验全部需求卡 schema
- 校验 `must` 需求都有 Given/When/Then 齐全的验收标准
- 扫描禁止模糊词（友好 / 快速 / 稳定 / 安全 / 合理 / 尽快 …）

## 三条不能破的规矩

1. **P0 缺失或冲突不能靠默认值糊过去。** 必须问。
2. **门禁不能静默降级。** `reject` 不能因为赶进度写成 `pass`，拿不到信息就写 `unknown`。
3. **不做范围判断。** 发现定位影响只写候选，不替对方 Skill 拿主意。
