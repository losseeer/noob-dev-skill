# 步骤 1：解析上游输入

## 目的

把上游两份产物读进来，建立本轮设计的事实起点。**只读，不做任何推断补充，不提问。**

## 读什么

按下面顺序找，找不到就记 `not_found`，**不阻塞、不报错、不要求用户先补齐**：

| 来源 | 路径 | 关心什么 |
|---|---|---|
| 项目定位 Skill | `.project/positioning/current.yaml` | `constraints`、`non_functional_priority`，以及 `positioning` 里的等级类字段 |
| 需求分析 Skill | `.project/requirements/requirements/*.yaml` | 每张卡的 `acceptance_criteria`、`out_of_scope`、`assumptions` |
| 用户项目本身 | 包管理文件、README、源码目录 | 现有技术栈（决定 `language` / `framework` 选型能不能直接跟随） |

## 输出

写入 `current.yaml` 的 `upstream` 字段：

- `positioning.status`：`found` / `not_found` / `skipped`
- `requirements.status`：同上
- 两者为 `found` 时，`fields_read` 要列出实际读了哪些字段
- 两者为 `not_found` 时，在 `note` 里写清「技术选型因此少了哪些依据」，**不要假装读过**

同时建立 `coverage` 骨架：每条 `acceptance_criteria` 登记一条，`status` 先统一填 `gap`，
`covered_by` 留空。后续步骤逐步填实。

## 硬性约束

- **不修改**上游任何文件。定位卡、需求卡一律只读。
- 不调用另外两个 Skill，也不读取它们的 `SKILL.md`。
- 用户项目里有既有技术栈时，`language` 和 `framework` 直接跟随现有栈，
  `basis` 记为 `user_choice`、`source_ref` 写清是从哪个文件读到的。
- 本步骤结束时，`coverage` 里不允许出现任何 `status: covered`。

## 反模式

- 上游文件不存在，就在 `note` 里写「已按最佳实践补充」——这是把缺失伪装成推断。
- 上游 `assumptions` 里的内容当成事实继续推导——它们是待确认项，要进 `open_questions`。
