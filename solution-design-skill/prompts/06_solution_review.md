# 步骤 6：方案校验与 Review

## 目的

用机器能判的部分先过一遍，剩下的再由人来判。

## 第一步：跑脚本（不可跳过）

```bash
cd <本 skill 目录>/scripts && python validate_bundle.py
```

它检查五件事：ADR 文件是否存在、接口认领的 AC 有没有登记、标了 `covered` 的 AC
有没有人认领、`assumption` 有没有 `why_assumed`、prototype 页面文件在不在。

输出必须是 `Bundle validation passed`。
**脚本缺失、Python 不可用、依赖没装——全部显式报告，不许当成通过。**

## 第二步：七项人工检查

逐条比 `rules/review_rules.yaml`，结果写进 `reviews/<date>-<version>.yaml` 的 `checks`，
每项 `passed` 必须是显式布尔值。

其中 C3（交叉引用）必须以上一步的脚本输出为依据，**不许凭印象填 `passed: true`**。

## 第三步：决策语义

| decision | 触发条件 | 之后 |
|---|---|---|
| `approve` | 七项全 passed 且无 `blocker` | `status_after: reviewed`，`current.yaml` 的 `status` 改 `reviewed` |
| `request_changes` | 任一项 failed | 保持 `draft`，列出整改项 |
| `insufficient_evidence` | 选型性状无法判定（例如没读过现有代码就定了框架） | 保持 `draft`，先补最小事实 |

`findings` 里只要有 `severity: blocker`，`decision` 就不得为 `approve`。

## 硬性约束

- Review 失败不得假装已确认。
- 校验脚本跑不起来时，C3 记 `passed: false` 并在 `note` 里写清退化原因——
  不能写成 `passed: true`。这跟另外两个 Skill 的「不许静默降级」是同一条。
- `current.yaml` 里每条 `assumptions` 都要有 `mitigation`，
  只写「如果错了会怎样」而不写「错了怎么办」等于没写。

## 反模式

- 跳第一步直接写 review，`checks` 全 `passed: true`。
- `findings` 里全是 minor，把真正的 blocker 降级成 minor 好让 decision 变成 approve。
