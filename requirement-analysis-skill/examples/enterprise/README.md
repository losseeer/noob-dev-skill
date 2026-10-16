## enterprise · 完整闭环 + 定位桥接

一句话概况：企业级账单导出，含探针子需求、需求集索引、追踪矩阵，以及 3 条定位候选。

### 关键节点

| 环节 | 这里发生了什么 |
|---|---|
| 桥接 | `positioning_context: read`，只读 `summary` / `constraints` / `glossary` |
| 拆分 | REQ-010 拆出 REQ-011 作为 spike；spike 的验收是「产出结论」不是「用户可以…」 |
| 排序 | REQ-011（探针，order 1）排在 REQ-010（order 2）之前，符合 PRIO-005 |
| 桥接输出 | billing / audit / compliance 三条候选写入 `positioning_candidates.yaml` |
| 门禁 | REQ-010 `pass` |

### 这个示例最重要的纪律

打开 `positioning_candidates.yaml`，里面没有任何一句说「这个需求该做」或「不该做」。
每条的 `action` 都是同一句话：`建议交给项目定位 Skill 做范围门禁`。

需求分析 Skill **不做范围判断**——这是它与项目定位 Skill 的分界线。
如果把「涉及 billing，所以要升级定位」写进这个文件，就越界了。

### 追踪矩阵怎么用

`traceability.yaml` 里的 `acceptance_without_test` 已经列出全部 9 条 AC 还没落地测试，
这是故意留的真实状态——实现阶段回填后，`status` 才能从 `partially_linked` 变成 `linked`。
