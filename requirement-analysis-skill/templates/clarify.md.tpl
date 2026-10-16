# Clarify session {{date}}

需求：`{{requirement_id}}` {{version}}
轮次：第 {{round}} 轮 / 剩余待问 {{remaining}}
定位上下文：{{positioning_context}}

## 本轮要解决什么

{{goal_of_this_round}}

---

## Q1 · {{q1_dimension}}（{{q1_priority}}，{{q1_rule_id}}）

{{q1_prompt}}

- A. {{q1_a_label}}　—　{{q1_a_impact}}
- B. {{q1_b_label}}　—　{{q1_b_impact}}　**【推荐】** {{q1_recommendation_reason}}
- C. {{q1_c_label}}　—　{{q1_c_impact}}
- 其他（请填写）：______

## Q2 · {{q2_dimension}}（{{q2_priority}}，{{q2_rule_id}}）

{{q2_prompt}}

- A. {{q2_a_label}}　—　{{q2_a_impact}}
- B. {{q2_b_label}}　—　{{q2_b_impact}}
- 其他（请填写）：______

## Q3 · {{q3_dimension}}（{{q3_priority}}，{{q3_rule_id}}）

{{q3_prompt}}

- A. {{q3_a_label}}　—　{{q3_a_impact}}
- B. {{q3_b_label}}　—　{{q3_b_impact}}
- 其他（请填写）：______

> 本轮少于 3 题时，删除多余的 Q 段，不要留空占位。

---

## 不回答时会怎样

未选择时按下列推荐值执行，并在对应维度记 `undecided` + `review_trigger`：

{{fallback_defaults}}

## 不在本次提问范围

{{skipped_items}}
