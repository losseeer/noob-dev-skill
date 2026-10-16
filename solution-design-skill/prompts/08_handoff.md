# 步骤 8：交付摘要

## 目的

把方案整理成 `dev-companion` 能直接接着干的输入。**写文件，不调用对方 Skill。**

## 产出

### `.project/design/current.md`

给人读的摘要，一段话讲清：

- 用了什么技术栈，为什么
- 数据模型与接口的要点
- 有哪些假设还没验证，复审条件是什么
- 原型在哪，review 状态如何

### 交付清单

在 `current.md` 末尾附一张表，把每项产出落成「下一步该做什么」：

| 产出 | 下一步归属 |
|---|---|
| `tech/interfaces.yaml` 的每条接口 | 一条实施任务 |
| `tech/data-model.yaml` 的索引与约束 | 迁移脚本任务 |
| `prototype/` 的页面 | 前端实现任务（含尚未补齐的错误态） |
| `open_questions` | 阻塞项，实施前必须先有答案 |
| `assumptions` | 探针任务，或写进验收条件 |

## 硬性约束

- **不调用 `dev-companion`**，也不在产物里写「根据 dev-companion 第 X 条」。
  产物只对 abstraction（ shape）负责，与另外两个 Skill 一样遵循「只通过文件约定协作」。
- 本 Skill 不写实现代码，也不替对方拆分任务粒度——那属于开发陪伴 Skill 的决策点处理。
- `open_questions` 里有未答复项时，摘要里必须显式标出阻塞，不能含糊带过。

## 反模式

- 摘要里写「方案已完成，可以开工」，但 `open_questions` 里还躺着三个未决项。
- 把推测的工期、人手、上线时间写进摘要——本 Skill 不产出这类信息。
