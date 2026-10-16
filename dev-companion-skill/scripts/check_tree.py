#!/usr/bin/env python3
"""dev-companion-skill · 项目开发状态树一致性校验（stdlib only, no dependencies）

用法:
    python check_tree.py <project-root|TREE.md> [--map] [--mermaid] [--json]
    python check_tree.py --selftest

退出码:
    0 = PASS
    1 = FAIL（存在 ERROR）
    2 = 硬失败（树文件缺失 / 无法解析）—— 必须显式报告，不许当成 PASS
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

TREE_REL = os.path.join("dev-tree", "TREE.md")
VER_DIR_REL = os.path.join("dev-tree", "versions")
TABLE_MARK = "<!-- dev-companion-skill:tree format=table -->"
# 历史标记：改名前后写进用户项目 TREE.md 的标记都必须继续识别，
# 否则已有项目会静默退化成「按列表格式解析」——那是把失败藏起来了。
# noob-dev 是最早的名字，dev-companion-skill 是上一次改名的结果。
LEGACY_TABLE_MARKS = (
    "<!-- dev-companion:tree format=table -->",
    "<!-- noob-dev:tree format=table -->",
)
ALL_TABLE_MARKS = (TABLE_MARK,) + LEGACY_TABLE_MARKS
CURRENT_RE = re.compile(r"当前活动节点[：:]")
# 终止态：项目全部完成时没有待完成节点可指，允许写成「当前活动节点：—」或标注「全部完成」
ALL_DONE_RE = re.compile(r"当前活动节点[：:]\s*(?:[—\-–—]|.*全部完成)")
NODE_LINE_RE = re.compile(r"^(?P<indent>[ \t]*)[-*] \[(?P<state>[ xX])\]\s*(?P<rest>.*)$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX)\b", re.IGNORECASE)
# 版本标签引用，如 v003。\b + 恰好三位数字，避免误伤 "v3.9"、"v0031"
VER_TAG_RE = re.compile(r"\bv(\d{3})\b", re.IGNORECASE)
RECOMMEND_WORDS = ("推荐", "采纳", "选用", "选定")
# 版本文档元信息区的 git commit 字段
GIT_COMMIT_RE = re.compile(r"^[-*]\s*git\s*commit\s*[：:]\s*(?P<val>.+?)\s*$", re.IGNORECASE)
# git 短 hash 至少 7 位，完整 40 位
GIT_HASH_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
# 否定形式：「未选定」「不推荐」这类不能被当成推荐行
NEGATIVE_RE = re.compile(r"(?:未|没|不)\s*(?:推荐|采纳|选用|选定)")
# 落地节点列里可接受的「可定位」写法：链接、不产生节点、或节点号（v003 / 1.2.1）
NODE_REF_RE = re.compile(r"v\d{3}|\b\d+(?:\.\d+)+\b", re.IGNORECASE)
# 协议固定的候选表签名，用来把真正的候选对比表和别的表区分开
CANDIDATE_TABLE_SIGNAL = ("做法", "好处", "代价")

CODE_TEXT = {
    "E1": "待完成节点有子节点（违反 I1：待完成必须是叶子）",
    "E2": "节点缺少版本文档链接",
    "E3": "版本文档不存在",
    "E4": "孤儿版本文档（没有任何节点引用它）",
    "E5": "版本标签重复",
    "E6": "层级跳级",
    "E7": "已完成节点缺少完成证据",
    "E8": "头部「当前活动节点」缺失或非法",
    "E9": "引用了不存在的版本标签（悬空引用）",
    "E10": "候选表缺少「落地节点」列，或推荐行没写它落到哪个节点",
    "E11": "版本链接不在 dev-tree/versions/ 下，或不是 .md",
    "E12": "表格格式的节点 ID 重复",
    "ALL_DONE": "全部节点已完成（终止态，不是错误）",
    "W1": "版本文档缺少「交付目标」节",
    "W2": "节点标题为空或含占位符",
    "W4": "版本标签是裸写（I6 要求写成链接，带上锚点）",
    "W5": "git commit 字段填了值，但既不是合法 hash 也不是 none",
}


def _norm_label(s):
    return (s or "").strip().lower()


def scan_lines(body, drop_links):
    """按行返回待扫描文本，保留行号。丢弃 fenced code block 与 H1 里的自身标签标识。

    drop_links=True 时连 markdown 链接一起移除（用于 W4：剩下的就是真正的裸引用）；
    False 时保留链接（用于 E9：链接里的标签也要查存在性）。
    """
    out, in_code = [], False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            out.append("")
            continue
        if in_code:
            out.append("")
            continue
        text = line
        if text.startswith("# "):
            # 一级标题里的「# v001 · xxx」是文档自身标识，不是引用
            text = re.sub(r"^#\s+v\d{3}\b", "", text, flags=re.IGNORECASE)
        out.append(LINK_RE.sub(" ", text) if drop_links else text)
    return out


def check_version_refs(docs, known_labels):
    """E9：正文里引用的 vNNN 必须是树上真实存在的标签。"""
    issues = []
    for docname, body in docs:
        seen = set()
        for lineno, text in enumerate(scan_lines(body, drop_links=False), 1):
            for m in VER_TAG_RE.finditer(text):
                tag = m.group(0)
                if tag.lower() in seen:
                    continue
                seen.add(tag.lower())
                if _norm_label(tag) not in known_labels:
                    issues.append(
                        Issue("E9", f"{docname}:{lineno} 引用 {tag}，树上没这个标签", lineno,
                              "改成真实存在的标签，或把漏掉的节点补上")
                    )
    return issues


def check_decision_table(docname, body):
    """E10：候选表必须有「落地节点」列，且推荐行的「该列」要写明落到哪个节点。

    注意：只在文档**确实存在候选表**时才检查。文档压根没写候选表，
    脚本无从判断它是不是决策点产物，这是已知盲区（规范里已如实写明）。
    """
    lines = body.splitlines()
    issues = []
    in_code = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        row = line.strip()
        if not row.startswith("|"):
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        joined = " ".join(cells)
        if "候选" not in joined or "结论" not in joined:
            continue
        # 判据收紧到协议六列签名：只有「候选 + 结论」的表可能是「已放弃方案」之类的表，不该吃 E10
        if sum(w in joined for w in CANDIDATE_TABLE_SIGNAL) < 2:
            continue
        if "落地节点" not in cells:
            issues.append(Issue("E10", f"{docname} 第 {i + 1} 行的候选表没有「落地节点」列", i + 1,
                                "候选名（含 slug）不提供追踪能力，追踪靠这一列"))
            continue
        land = cells.index("落地节点")
        for j, after in enumerate(lines[i + 2:], start=i + 3):
            r = after.strip()
            if not r.startswith("|"):
                break
            rc = [c.strip() for c in r.strip("|").split("|")]
            rj = " ".join(rc)
            if NEGATIVE_RE.search(rj) or not any(w in rj for w in RECOMMEND_WORDS):
                continue
            # 只认「落地节点」那一列，避免别的列里有个无关链接就蒙混过关
            cell = rc[land] if land < len(rc) else ""
            # I6 说锚点可以是链接 / 全标题 / 归属，所以节点号也算可定位
            if LINK_RE.search(cell) or "不产生节点" in cell or NODE_REF_RE.search(cell):
                continue
            issues.append(Issue("E10", f"{docname} 第 {j} 行推荐候选的「落地节点」列没写清", j,
                                "该列要链到它产生的节点、或写明节点号；明确放弃的写「不产生节点」"))
    return issues


def check_git_commit_field(docs):
    """W5：git commit 字段填了值就得像 hash（7-40 位 hex），或明确写 none。

    只查格式，不去 git 仓库里验证 hash 是否存在——那是 git 的事，
    脚本跑一次还要 spawn 子进程，不值当。缺这个字段不报（避免对既有项目噪音）。
    """
    issues = []
    for docname, body in docs[1:]:  # 跳过 TREE.md
        for lineno, line in enumerate(body.splitlines(), 1):
            m = GIT_COMMIT_RE.match(line.strip())
            if not m:
                continue
            val = m.group("val").strip().strip("`").strip()
            # 还留着 <...> 占位符 = 模板没填，不是填错。新项目开局第一天不该报警
            if "<" in val and ">" in val:
                continue
            if val.lower() == "none":
                continue
            if not GIT_HASH_RE.match(val):
                issues.append(
                    Issue("W5", f"{docname}:{lineno} 的 git commit 是「{val}」", lineno,
                          "填 7-40 位 hex；项目没用 git 就写 none。假的锚点比没有更糟")
                )
    return issues


def check_bare_version_refs(docs):
    """W4：I6 要求版本标签带锚点。移除链接与代码块后剩下的就是裸写。"""
    issues = []
    for docname, body in docs:
        seen = set()
        for lineno, text in enumerate(scan_lines(body, drop_links=True), 1):
            for m in VER_TAG_RE.finditer(text):
                tag = m.group(0)
                if tag.lower() in seen:
                    continue
                seen.add(tag.lower())
                issues.append(
                    Issue("W4", f"{docname}:{lineno} 的 {tag} 是裸写", lineno,
                          "写成 [vNNN](versions/NNN-x.md)；光有编号读者定位不到")
                )
    return issues


class Node:
    """key 是稳定层级键（列表格式由栈生成，表格格式即点分 ID）；
    父子一律由 key/parent_key 表达，不再依赖「相邻行」这种顺序假设。"""

    __slots__ = ("level", "done", "title", "label", "path", "lineno", "children",
                 "key", "parent_key")

    def __init__(self, level, done, title, label, path, lineno, key="", parent_key=None):
        self.level = level
        self.done = done
        self.title = title
        self.label = label
        self.path = path
        self.lineno = lineno
        self.children = 0
        self.key = key
        self.parent_key = parent_key


class Issue:
    def __init__(self, code, msg, lineno=None, hint=""):
        self.code = code
        self.msg = msg
        self.lineno = lineno
        self.hint = hint

    def __str__(self):
        loc = f":{self.lineno}" if self.lineno else ""
        base = f"{self.code}{loc} {self.msg}"
        return f"{base} — {self.hint}" if self.hint else base


def _strip_title(rest):
    """从 checkbox 后面的文本里去掉 md 链接，得到节点标题。

    链接写在标题前面（`- [x] [v001](...) — 标题`）时不能只取前半段，
    否则标题会被判为空并误报 W2。
    """
    m = LINK_RE.search(rest)
    core = (rest[: m.start()] + " " + rest[m.end():]) if m else rest
    core = core.strip().strip("—-–|").strip()
    core = core.replace("**", "").strip()
    core = re.sub(r"\s+", " ", core)
    return core


def parse_list_format(lines):
    """格式 A：缩进 checkbox 列表。返回 (nodes, issues)。"""
    nodes, issues = [], []
    in_code = False
    depths = []
    raw = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = NODE_LINE_RE.match(line.rstrip("\n"))
        if not m:
            continue
        indent = len(m.group("indent").expandtabs(2))
        if indent:
            depths.append(indent)
        raw.append((i, indent, m))

    unit = min(depths) if depths else 2
    prev_level = 0
    stack = []   # [(level, key)] 当前祖先链
    seq_of = {}  # parent_key -> 已分配的子序号
    for lineno, indent, m in raw:
        if indent == 0:
            level = 1
        else:
            level = indent // unit + 1
            if indent % unit:
                issues.append(
                    Issue("E6", f"缩进 {indent} 空格不是 {unit} 的整数倍", lineno,
                          f"整个文件统一用 {unit} 空格缩进一级")
                )
        if prev_level and level > prev_level + 1:
            issues.append(
                Issue("E6", f"从第 {prev_level} 级跳到第 {level} 级", lineno,
                      "层级必须逐级加深，不能跳级")
            )
        prev_level = level

        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_key = stack[-1][1] if stack else None
        seq = seq_of.get(parent_key, 0) + 1
        seq_of[parent_key] = seq
        key = f"{parent_key}.{seq}" if parent_key else str(seq)
        stack.append((level, key))

        rest = m.group("rest")
        link = LINK_RE.search(rest)
        nodes.append(
            Node(
                level=level,
                done=m.group("state").strip().lower() == "x",
                title=_strip_title(rest),
                label=link.group(1).strip() if link else None,
                path=link.group(2).strip() if link else None,
                lineno=lineno,
                key=key,
                parent_key=parent_key,
            )
        )
    return nodes, issues


def parse_table_format(lines):
    """格式 B：扁平表格 + 点分 ID。返回 (nodes, issues)。"""
    nodes, issues = [], []
    rows = []
    in_code = False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if set(cells[0]) <= set("-: ") or cells[0].lower() in ("id",):
            continue  # 表头 / 分隔行
        mstate = re.search(r"\[([ xX])\]", " ".join(cells))
        if not mstate:
            continue
        rows.append((i, cells[0], mstate.group(1).strip().lower() == "x",
                     LINK_RE.search(line), line))

    # 先建全量 ID 集合再校验父子：表格层级由 ID 前缀决定，与行顺序无关
    known_ids = {r[1] for r in rows}
    seen_id = {}
    for lineno, node_id, _done, _link, _line in rows:
        if node_id in seen_id:
            issues.append(
                Issue("E12", f"节点 ID `{node_id}` 重复（另见第 {seen_id[node_id]} 行）", lineno,
                      CODE_TEXT["E12"])
            )
        else:
            seen_id[node_id] = lineno
    for lineno, node_id, done, link, line in rows:
        level = node_id.count(".") + 1
        parent = node_id.rsplit(".", 1)[0] if "." in node_id else None
        if parent and parent not in known_ids:
            issues.append(
                Issue("E6", f"ID `{node_id}` 的父节点 `{parent}` 不存在", lineno,
                      "父子必须由点分 ID 表达，父节点要在表格里出现")
            )
        nodes.append(
            Node(
                level=level,
                done=done,
                title=_strip_title(cells_title(line)),
                label=link.group(1).strip() if link else None,
                path=link.group(2).strip() if link else None,
                lineno=lineno,
                key=node_id,
                parent_key=parent,
            )
        )
    return nodes, issues


def cells_title(line):
    """表格行里取「节点/标题」那一列（去掉 ID 列和状态列）。"""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 3:
        return ""
    # [ID, 状态, 标题, ...其余]
    idx = 2 if re.fullmatch(r"\[[ xX]\]", cells[1]) else 1
    return cells[idx] if idx < len(cells) else ""


def load_tree(tree_path):
    if not os.path.isfile(tree_path):
        return None, None, []
    with open(tree_path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    fmt = "table" if any(mark in content for mark in ALL_TABLE_MARKS) else "list"
    nodes, issues = (parse_table_format if fmt == "table" else parse_list_format)(lines)
    return content, nodes, issues


def check_content(content, nodes, root_dir):
    """校验全部不变量。返回 (errors, warnings, stats)。"""
    errors, warnings = [], []
    ver_dir = os.path.join(root_dir, VER_DIR_REL)

    # I1：待完成必须是叶子（按 key/parent_key 匹配算子节点数，不依赖行顺序）
    by_key = {n.key: n for n in nodes}
    for n in nodes:
        if n.parent_key and n.parent_key in by_key:
            by_key[n.parent_key].children += 1

    for n in nodes:
        if not n.done and n.children:
            errors.append(
                Issue("E1", f"待完成节点「{n.title}」有 {n.children} 个子节点", n.lineno,
                      CODE_TEXT["E1"])
            )

    # I2：版本链接、文件存在、孤儿、重复标签
    referenced = set()
    seen_label = {}
    for n in nodes:
        if not n.label or not n.path:
            errors.append(Issue("E2", f"节点「{n.title}」没有版本文档链接", n.lineno, CODE_TEXT["E2"]))
            continue
        target = os.path.normpath(os.path.join(root_dir, "dev-tree", n.path))
        if not os.path.isfile(target):
            errors.append(Issue("E3", f"{n.label} → {n.path}", n.lineno, CODE_TEXT["E3"]))
        else:
            rel = os.path.relpath(target, ver_dir)
            if rel.startswith("..") or not n.path.endswith(".md"):
                errors.append(
                    Issue("E11", f"{n.label} → {n.path}", n.lineno, CODE_TEXT["E11"])
                )
        referenced.add(os.path.abspath(target))
        if n.label in seen_label:
            errors.append(Issue("E5", f"标签 {n.label} 被多个节点使用", n.lineno,
                              f"已用于第 {seen_label[n.label]} 行的节点"))
        else:
            seen_label[n.label] = n.lineno

    if os.path.isdir(ver_dir):
        for name in sorted(os.listdir(ver_dir)):
            if not name.endswith(".md"):
                continue
            full = os.path.abspath(os.path.join(ver_dir, name))
            if full not in referenced:
                errors.append(Issue("E4", f"dev-tree/versions/{name}", None, CODE_TEXT["E4"]))

    # I3：头部当前活动节点
    cur_label, cur_path = None, None
    for line in content.splitlines():
        if not CURRENT_RE.search(line):
            continue
        m = LINK_RE.search(line)
        if m:
            cur_label, cur_path = m.group(1).strip(), m.group(2).strip()
        break

    current = None
    if cur_label:
        for n in nodes:
            if n.label == cur_label:
                current = n
                break
    all_done = bool(ALL_DONE_RE.search(content))
    if all_done:
        # 终止态：项目做完了，没有待完成节点可指。但声称全完成就必须真的全完成
        if any(not n.done for n in nodes):
            errors.append(
                Issue("E8", "头部写了「全部完成」，但树上仍有待完成节点", None,
                      "要么把剩下的做完，要么把当前活动节点指回待完成节点")
            )
        current = None
    elif current is None:
        errors.append(Issue("E8", "头部「当前活动节点」未在树中找到对应节点", None,
                          "检查 > 当前活动节点：`标题` → [vNNN](versions/NNN-x.md) 这一行"))
    elif current.done:
        errors.append(Issue("E8", f"当前活动节点「{current.title}」已被标记已完成", None,
                          "当前活动节点必须是待完成的叶子；已完成的话请指向下一个"))
    elif current.children:
        errors.append(Issue("E8", f"当前活动节点「{current.title}」有子节点", None,
                          "违反 I1，先把它的子节点处理掉"))

    # I5 / E7：已完成节点必须有完成证据
    for n in nodes:
        if not n.done or not n.path:
            continue
        target = os.path.join(root_dir, "dev-tree", n.path)
        if not os.path.isfile(target):
            continue
        body = _read(target)
        if "完成证据" not in body:
            errors.append(Issue("E7", f"「{n.title}」的版本文档没有「完成证据」节", n.lineno,
                              "标 [x] 之前必须写：验证命令 + 实际输出"))
        else:
            section = _section(body, "完成证据")
            if not section.strip() or "未验证" in section:
                errors.append(Issue("E7", f"「{n.title}」的完成证据为空或写着「未验证」", n.lineno,
                                  "先真的验证，再标 [x]"))
        if "交付目标" not in body:
            warnings.append(Issue("W1", f"{n.path} 缺少「交付目标」节", n.lineno, CODE_TEXT["W1"]))

    # W2：占位符标题
    for n in nodes:
        if not n.title or PLACEHOLDER_RE.search(n.title):
            warnings.append(Issue("W2", f"第 {n.lineno} 行标题：{n.title or '(空)'}", n.lineno,
                              CODE_TEXT["W2"]))

    # I6：编号引用必须可定位（E9 悬空标签 / W4 裸写 / E10 候选表落地节点）
    docs = [("dev-tree/TREE.md", content)]
    if os.path.isdir(ver_dir):
        for name in sorted(os.listdir(ver_dir)):
            if name.endswith(".md"):
                docs.append((f"dev-tree/versions/{name}", _read(os.path.join(ver_dir, name))))
    known_labels = {_norm_label(n.label) for n in nodes if n.label}
    errors.extend(check_version_refs(docs, known_labels))
    warnings.extend(check_bare_version_refs(docs))
    warnings.extend(check_git_commit_field(docs))
    for docname, body in docs[1:]:
        errors.extend(check_decision_table(docname, body))

    stats = {
        "nodes": len(nodes),
        "done": sum(1 for n in nodes if n.done),
        "todo": sum(1 for n in nodes if not n.done),
        "max_depth": max((n.level for n in nodes), default=0),
        "current": current.title if current else None,
        "current_label": current.label if current else None,
        "current_index": nodes.index(current) if current is not None else None,
    }
    return errors, warnings, stats


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# 允许「## 4. 完成证据」这种带编号前缀的写法：编号对用户友好，不该被脚本禁掉
HEADING_RE = re.compile(r"^#{1,6}\s+(?:\d+(?:\.\d+)*[.、)]?\s*)?(?P<name>.+?)\s*$")


def _heading_name(line):
    m = HEADING_RE.match(line)
    return m.group("name").strip() if m else None


def _section(body, name):
    """取标题 `name` 到下一个标题之间的正文；标题允许「4. 完成证据」这类编号前缀。"""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if _heading_name(line) == name:
            out = []
            for after in lines[i + 1:]:
                if _heading_name(after) is not None:
                    break
                out.append(after)
            return "\n".join(out)
    return ""


def _path_to(nodes, current):
    """从根到当前活动节点的路径（按 parent_key 上溯）。"""
    by_key = {n.key: n for n in nodes}
    path = []
    n = current
    while n is not None:
        path.append(n)
        n = by_key.get(n.parent_key) if n.parent_key else None
    path.reverse()
    return path


def render_progress(nodes, current):
    """能力 C（行动优先模式）进度行：一行拿走就能用，不用手工转写。

    H10 要求进度数字必须来自树，不能自己估——这条命令就是那个来源。
    """
    total = len(nodes)
    done = sum(1 for n in nodes if n.done)
    if current is None:
        return f"[{done}/{total} 已完成] · 全部完成"
    names = " › ".join(n.title for n in _path_to(nodes, current))
    return f"[{done}/{total} 已完成] · 你在：{names}"


def render_map(nodes, current):
    """当前路径面包屑（从根到当前活动节点）。"""
    if current is None:
        return "(无当前活动节点)"
    path = _path_to(nodes, current)
    out = []
    for n in path:
        mark = "[x]" if n.done else "[ ]"
        out.append(f"{'    ' * (n.level - 1)}{mark} {n.title}  →  {n.label}")
    return "\n".join(out)


def render_mermaid(nodes):
    def esc(s):
        # 标题里可能有引号或尖括号（如 /s/<code>），不转义会破坏 mermaid 语法
        return (s or "").replace('"', "'").replace("<", "&lt;").replace(">", "&gt;")

    out = ["```mermaid", "flowchart TD"]
    idx_of = {n.key: i for i, n in enumerate(nodes)}
    for i, n in enumerate(nodes):
        nid = f"N{i}"
        label = f"{esc(n.title)}\\n{esc(n.label)}"  # mermaid 里 \n 才是换行
        shape = f'{nid}["{label}"]' if n.done else f'{nid}("{label}")'
        out.append(f"    {shape}")
        p = idx_of.get(n.parent_key) if n.parent_key else None
        if p is not None:
            out.append(f"    N{p} --> {nid}")
    out.append("```")
    return "\n".join(out)


def evaluate(tree_path, root_dir):
    """唯一的评估入口：解析 + 校验 + 合并。run() 与 selftest() 共用，避免两条汇总路径。"""
    content, nodes, parse_issues = load_tree(tree_path)
    if content is None or not nodes:
        return None
    errors, warnings, stats = check_content(content, nodes, root_dir)
    for it in parse_issues:
        (errors if it.code.startswith("E") else warnings).append(it)
    return nodes, errors, warnings, stats


def run(tree_path, root_dir, want_map=False, want_mermaid=False, want_json=False,
        want_progress=False):
    ev = evaluate(tree_path, root_dir)
    if ev is None:
        if not os.path.isfile(tree_path):
            print(f"[FAIL] 找不到状态树文件：{tree_path}", file=sys.stderr)
            print("  先执行 bootstrap 创建 dev-tree/TREE.md（见 references/tree-protocol.md）", file=sys.stderr)
        else:
            print(f"[FAIL] {tree_path} 里没有解析到任何节点行", file=sys.stderr)
            print("  节点行必须是 `- [x]` / `- [ ]` 开头的 Markdown checkbox", file=sys.stderr)
        return 2
    nodes, errors, warnings, stats = ev
    ci = stats.get("current_index")
    current = nodes[ci] if ci is not None else None

    payload = {
        "ok": not errors,
        "tree": tree_path,
        "stats": stats,
        "errors": [{"code": i.code, "lineno": i.lineno, "msg": i.msg, "hint": i.hint} for i in errors],
        "warnings": [{"code": i.code, "lineno": i.lineno, "msg": i.msg, "hint": i.hint} for i in warnings],
    }
    if want_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if not errors else 1

    if errors:
        print(f"[FAIL] {len(errors)} error(s), {len(warnings)} warning(s)  ·  {tree_path}")
        for i in sorted(errors, key=lambda x: (x.lineno or 0, x.code)):
            print(f"  ERROR {i}")
        for i in sorted(warnings, key=lambda x: (x.lineno or 0, x.code)):
            print(f"  WARN  {i}")
    else:
        s = stats
        print(f"[PASS] {s['nodes']} 节点 · {s['done']} 已完成 · {s['todo']} 待完成 · 最深 {s['max_depth']} 层  ·  {tree_path}")
        print(f"       当前活动节点：{s['current']} → {s['current_label']}")
        for i in warnings:
            print(f"  WARN  {i}")

    if want_map:
        print("\n--- 当前路径 ---")
        print(render_map(nodes, current))
    if want_progress:
        print("\n--- 进度行（能力 C 直接复制这一行）---")
        print(render_progress(nodes, current))
    if want_mermaid:
        print("\n--- mermaid（可视化，生成物；真源始终是 TREE.md） ---")
        print(render_mermaid(nodes))
    return 0 if not errors else 1


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------

BAD_TREE = """# demo · 开发状态树

> 当前活动节点：`已完成的那步` → [v001](versions/001-init.md)

- [x] 已完成的那步 — [v001](versions/001-init.md)
    - [ ] 待完成节点却有子节点 — [v002](versions/002-a.md)
        - [ ] 更深一层 — [v003](versions/003-b.md)
- [ ] 没有链接的节点
- [x] 指向不存在的文档 — [v404](versions/404-missing.md)
- [ ] 标题带 TODO
        - [ ] 缩进跳了两级 — [v005](versions/005-jump.md)
- [x] 重复标签 — [v001](versions/001-init.md)
"""

BAD_VERSION = """# v001 · 已完成的那步

## 交付目标

一行话。

## 项目状态

略。

## 完成证据

未验证
"""

BAD_VERSION_OK = """# v001 · 已完成的那步

## 交付目标

一行话。

## 项目状态

略。

## 完成证据

命令：echo ok
输出：ok
"""

GOOD_TREE = """# demo · 开发状态树

> 当前活动节点：`第二步` → [v002](versions/002-step2.md)

- [x] 第一步 — [v001](versions/001-init.md)
    - [ ] 第二步 — [v002](versions/002-step2.md)
    - [ ] 第三步 — [v003](versions/003-step3.md)
"""

GOOD_VERSION = """# v001 · 第一步

## 交付目标

把这步做完。

## 项目状态

略。

## 完成证据

命令：pytest -q
输出：1 passed
"""

TODO_VERSION = """# v002 · 第二步

## 交付目标

还没做。

## 项目状态

略。

## 完成证据

未验证
"""

# 「已放弃方案」表不是候选对比表，不该吃 E10
TODO_VERSION_3 = TODO_VERSION.replace("# v002 · 第二步", "# v003 · 第三步")

# git commit 字段：合法 hash / none / 非法值
GIT_OK_VERSION = """# v001 · 第一步

- 父节点：—
- 写入时间：2026-10-16 10:00
- git commit：abc1234

## 交付目标

一行话。

## 项目状态

略。

## 完成证据

命令：echo ok
输出：ok
"""

GIT_NONE_VERSION = GIT_OK_VERSION.replace("git commit：abc1234", "git commit：none")
# 模板占位符没填：不算填错
GIT_PLACEHOLDER_VERSION = GIT_OK_VERSION.replace(
    "git commit：abc1234", "git commit：<hash 或 none>")
GIT_BAD_VERSION = GIT_OK_VERSION.replace("git commit：abc1234", "git commit：见 git log")

# 已完成且带完成证据的版本（用于终止态 fixture）
DONE_VERSION = TODO_VERSION.replace("未验证", "命令：echo ok\n输出：ok")

# 终止态：项目全部做完，没有待完成节点可指
ALL_DONE_TREE = """# demo · 开发状态树

> 当前活动节点：—（全部完成）

- [x] 第一步 — [v001](versions/001-init.md)
    - [x] 第二步 — [v002](versions/002-step2.md)
"""

# 节点链接指向 versions/ 之外（TREE.md 确实存在，所以只应命中 E11，不是 E3）
BAD_PATH_TREE = """# demo · 开发状态树

> 当前活动节点：`第二步` → [v002](versions/002-step2.md)

- [x] 第一步 — [v001](TREE.md)
    - [ ] 第二步 — [v002](versions/002-step2.md)
"""

# 「已放弃方案」表不是候选对比表，不该吃 E10
ABANDONED_TABLE_VERSION = """# v001 · 第一步

## 交付目标

一行话。

## 已放弃方案

| 候选 | 理由 | 结论 |
|---|---|---|
| `old-idea` | 太重 | 放弃 |

## 项目状态

略。

## 完成证据

命令：echo ok
输出：ok
"""

# 结论写「未选定」不应被当成推荐行
NOT_SELECTED_VERSION = """# v001 · 第一步

## 交付目标

一行话。

## 决策记录

| 候选 | 做法 | 好处 | 代价 | 结论 | 落地节点 |
|---|---|---|---|---|---|
| `a` | 做法 | 好处 | 代价 | 未选定 | 待定 |

## 项目状态

略。

## 完成证据

命令：echo ok
输出：ok
"""

# code block 里的引用不该被扫到
CODE_BLOCK_VERSION = GOOD_VERSION + "\n```bash\nnode index.js  # 见 v999\n```\n"

# H1 里除自身标识之外的裸引用仍要抓到
H1_REF_VERSION = ("# v001 · 承接 v002 的决定\n\n## 交付目标\n\n一行话。\n\n"
                  "## 项目状态\n\n略。\n\n## 完成证据\n\n命令：echo ok\n输出：ok\n")

# 引用了树上不存在的 v999 → 应命中 E9
DANGLING_REF_VERSION = GOOD_VERSION + "\n细节见 v999。\n"

# 候选表缺「落地节点」列 → 应命中 E10
TABLE_NO_LANDING = """# v001 · 第一步

## 交付目标

一行话。

## 决策记录

| 候选 | 做法 | 好处 | 代价 | 结论 |
|---|---|---|---|---|
| `jump-first` | 先跑通跳转 | 早看到效果 | 重启丢数据 | **推荐** |
| `persist-first` | 先做持久化 | 数据不丢 | 很久看不到效果 | 落选 |

## 项目状态

略。

## 完成证据

命令：echo ok
输出：ok
"""

# 候选表带「落地节点」列且推荐行有链接 → 不应报 E10
TABLE_WITH_LANDING = """# v001 · 第一步

## 交付目标

一行话。

## 决策记录

| 候选 | 做法 | 好处 | 代价 | 结论 | 落地节点 |
|---|---|---|---|---|---|
| `jump-first` | 先跑通跳转 | 早看到效果 | 重启丢数据 | **推荐** | [v002](versions/002-step2.md) |
| `persist-first` | 先做持久化 | 数据不丢 | 很久看不到效果 | 落选 | 不产生节点 |

## 项目状态

略。

## 完成证据

命令：echo ok
输出：ok
"""


def _write(root, tree, versions):
    os.makedirs(os.path.join(root, VER_DIR_REL), exist_ok=True)
    with open(os.path.join(root, TREE_REL), "w", encoding="utf-8") as f:
        f.write(tree)
    for name, body in versions.items():
        with open(os.path.join(root, VER_DIR_REL, name), "w", encoding="utf-8") as f:
            f.write(body)


def selftest():
    results = []

    def begin(name):
        results.append([name, True, ""])

    def expect(cond, msg):
        if not cond:
            results[-1][1] = False
            results[-1][2] = msg

    tmp = tempfile.mkdtemp(prefix="dev-companion-skill-selftest-")
    try:
        # ---- case 1: 缺失树 -> 退出码 2
        begin("缺少 TREE.md 应返回退出码 2")
        empty = os.path.join(tmp, "empty")
        os.makedirs(empty, exist_ok=True)
        rc = run(os.path.join(empty, TREE_REL), empty)
        expect(rc == 2, f"期望 2，实际 {rc}")

        # ---- case 2: 错误树应命中全部预期错误码
        begin("畸形树应命中 E1/E2/E3/E4/E5/E6/E7/E8")
        # 001-init.md 故意写「未验证」，用于命中 E7（I5：没证据不许标完成）
        bad = os.path.join(tmp, "bad")
        _write(bad, BAD_TREE, {
            "001-init.md": BAD_VERSION,
            "002-a.md": BAD_VERSION,
            "003-b.md": BAD_VERSION_OK,
            "005-jump.md": BAD_VERSION_OK,
            "999-orphan.md": GOOD_VERSION,
        })
        rc = run(os.path.join(bad, TREE_REL), bad)
        expect(rc == 1, f"期望 1，实际 {rc}")
        nodes, errors, _, _ = evaluate(os.path.join(bad, TREE_REL), bad)
        codes = {i.code for i in errors}
        for want, why in [
            ("E1", "待完成节点有子节点"),
            ("E2", "缺链接"),
            ("E3", "链接目标不存在"),
            ("E4", "孤儿版本文档"),
            ("E5", "标签重复"),
            ("E6", "跳级"),
            ("E7", "已完成节点没有完成证据"),
            ("E8", "当前活动节点非法"),
        ]:
            expect(want in codes, f"未命中 {want}（{why}）")

        # E7 单独造：已完成 + 完成证据写着未验证
        begin("已完成节点未完成证据应命中 E7")
        e7 = os.path.join(tmp, "e7")
        _write(e7, GOOD_TREE.replace("- [x] 第一步", "- [x] 第一步"), {
            "001-init.md": BAD_VERSION,
            "002-step2.md": TODO_VERSION,
            "003-step3.md": TODO_VERSION_3,
        })
        nodes, errors, _, _ = evaluate(os.path.join(e7, TREE_REL), e7)
        expect("E7" in {i.code for i in errors}, f"未命中 E7，实际错误：{[i.code for i in errors]}")

        # ---- case 3: 表格格式解析
        begin("表格格式（点分 ID）应能解析并校验")
        tbl = os.path.join(tmp, "table")
        tbl_tree = (
            "# demo · 开发状态树\n\n"
            "> 当前活动节点：`子步` → [v002](versions/002-b.md)\n\n"
            f"{TABLE_MARK}\n\n"
            "| ID | 状态 | 节点 | 版本 |\n"
            "|---|---|---|---|\n"
            "| 1 | [x] | 起点 | [v001](versions/001-a.md) |\n"
            "| 1.1 | [ ] | 子步 | [v002](versions/002-b.md) |\n"
            "| 2 | [ ] | 后面 | [v003](versions/003-c.md) |\n"
        )
        _write(tbl, tbl_tree, {
            "001-a.md": GOOD_VERSION,
            "002-b.md": TODO_VERSION,
            "003-c.md": TODO_VERSION,
        })
        nodes, errors, _, stats = evaluate(os.path.join(tbl, TREE_REL), tbl)
        expect(len(nodes) == 3, f"期望 3 个节点，实际 {len(nodes)}")
        # 防止 cells_title 取错行：三个节点标题必须互不相同
        expect(len({n.title for n in nodes}) == 3,
               f"表格节点标题应互不相同，实际：{[n.title for n in nodes]}")
        expect(not errors, f"良性表格不应报错：{[str(i) for i in errors]}")
        expect(stats["max_depth"] == 2, f"期望最深 2 层，实际 {stats['max_depth']}")

        # ---- case 3b: 乱序表格（子行先于父行）
        begin("乱序表格不应误报 E6，父子关系仍正确")
        tbl2 = os.path.join(tmp, "table2")
        tbl2_tree = (
            "# demo · 开发状态树\n\n"
            "> 当前活动节点：`子步` → [v002](versions/002-b.md)\n\n"
            f"{TABLE_MARK}\n\n"
            "| ID | 状态 | 节点 | 版本 |\n"
            "|---|---|---|---|\n"
            "| 1.1 | [ ] | 子步 | [v002](versions/002-b.md) |\n"
            "| 1 | [x] | 起点 | [v001](versions/001-a.md) |\n"
            "| 2 | [ ] | 后面 | [v003](versions/003-c.md) |\n"
        )
        _write(tbl2, tbl2_tree, {
            "001-a.md": GOOD_VERSION,
            "002-b.md": TODO_VERSION,
            "003-c.md": TODO_VERSION,
        })
        nodes2, errors2, _, _ = evaluate(os.path.join(tbl2, TREE_REL), tbl2)
        expect(not errors2, f"乱序表格不应报错：{[str(i) for i in errors2]}")
        by_key = {n.key: n for n in nodes2}
        expect(bool(by_key.get("1")) and by_key["1"].children == 1,
               f"ID 1 应有 1 个子节点，实际 {by_key.get('1').children if by_key.get('1') else 'N/A'}")

        # ---- case 3c: 改名前的旧格式标记仍要识别（否则已有项目会静默退化）
        begin("旧格式标记（noob-dev:tree）仍应识别为表格格式")
        tbl3 = os.path.join(tmp, "table3")
        tbl3_tree = (
            "# demo · 开发状态树\n\n"
            "> 当前活动节点：`子步` → [v002](versions/002-b.md)\n\n"
            "<!-- noob-dev:tree format=table -->\n\n"
            "| ID | 状态 | 节点 | 版本 |\n"
            "|---|---|---|---|\n"
            "| 1 | [x] | 起点 | [v001](versions/001-a.md) |\n"
            "| 1.1 | [ ] | 子步 | [v002](versions/002-b.md) |\n"
        )
        _write(tbl3, tbl3_tree, {"001-a.md": GOOD_VERSION, "002-b.md": TODO_VERSION})
        nodes3, errors3, _, _ = evaluate(os.path.join(tbl3, TREE_REL), tbl3)
        expect(len(nodes3) == 2, f"旧标记应解析出 2 个节点，实际 {len(nodes3)}")
        expect(not errors3, f"旧标记不应报错：{[str(i) for i in errors3]}")

        # ---- case 3d: 上一次改名的标记（dev-companion:tree）仍要识别
        begin("上一版标记（dev-companion:tree）仍应识别为表格格式")
        tbl3d = os.path.join(tmp, "table3d")
        tbl3d_tree = (
            "# demo · 开发状态树\n\n"
            "> 当前活动节点：`子步` → [v002](versions/002-b.md)\n\n"
            "<!-- dev-companion:tree format=table -->\n\n"
            "| ID | 状态 | 节点 | 版本 |\n"
            "|---|---|---|---|\n"
            "| 1 | [x] | 起点 | [v001](versions/001-a.md) |\n"
            "| 1.1 | [ ] | 子步 | [v002](versions/002-b.md) |\n"
        )
        _write(tbl3d, tbl3d_tree, {"001-a.md": GOOD_VERSION, "002-b.md": TODO_VERSION})
        nodes3d, errors3d, _, _ = evaluate(os.path.join(tbl3d, TREE_REL), tbl3d)
        expect(len(nodes3d) == 2, f"上一版标记应解析出 2 个节点，实际 {len(nodes3d)}")
        expect(not errors3d, f"上一版标记不应报错：{[str(i) for i in errors3d]}")

        # ---- case 4: E9 悬空版本标签引用
        begin("引用不存在的 vNNN 应命中 E9")
        e9 = os.path.join(tmp, "e9")
        _write(e9, GOOD_TREE, {
            "001-init.md": DANGLING_REF_VERSION,
            "002-step2.md": TODO_VERSION,
            "003-step3.md": TODO_VERSION_3,
        })
        _, errors, _, _ = evaluate(os.path.join(e9, TREE_REL), e9)
        expect("E9" in {i.code for i in errors}, f"未命中 E9，实际错误：{[i.code for i in errors]}")

        # ---- case 4b: W4 裸写版本标签（存在但没写成链接）
        begin("裸写版本标签应命中 W4")
        bare = os.path.join(tmp, "bare")
        _write(bare, GOOD_TREE, {
            "001-init.md": GOOD_VERSION + "\n参见 v002 的细节。\n",
            "002-step2.md": TODO_VERSION,
            "003-step3.md": TODO_VERSION_3,
        })
        _, _, warnings, _ = evaluate(os.path.join(bare, TREE_REL), bare)
        expect("W4" in {i.code for i in warnings}, f"未命中 W4，实际警告：{[i.code for i in warnings]}")

        begin("写成链接的版本标签不应报 W4")
        linked = os.path.join(tmp, "linked")
        _write(linked, GOOD_TREE, {
            "001-init.md": GOOD_VERSION + "\n参见 [v002](versions/002-step2.md) 的细节。\n",
            "002-step2.md": TODO_VERSION,
            "003-step3.md": TODO_VERSION_3,
        })
        _, _, warnings, _ = evaluate(os.path.join(linked, TREE_REL), linked)
        expect("W4" not in {i.code for i in warnings}, f"误报 W4：{[str(i) for i in warnings]}")

        # ---- case 5: E10 候选表缺落地节点
        begin("候选表缺落地节点应命中 E10")
        e10 = os.path.join(tmp, "e10")
        _write(e10, GOOD_TREE, {
            "001-init.md": TABLE_NO_LANDING,
            "002-step2.md": TODO_VERSION,
            "003-step3.md": TODO_VERSION_3,
        })
        _, errors, _, _ = evaluate(os.path.join(e10, TREE_REL), e10)
        expect("E10" in {i.code for i in errors}, f"未命中 E10，实际错误：{[i.code for i in errors]}")

        begin("候选表带落地节点不应报 E10")
        e10ok = os.path.join(tmp, "e10ok")
        _write(e10ok, GOOD_TREE, {
            "001-init.md": TABLE_WITH_LANDING,
            "002-step2.md": TODO_VERSION,
            "003-step3.md": TODO_VERSION_3,
        })
        _, errors, _, _ = evaluate(os.path.join(e10ok, TREE_REL), e10ok)
        expect("E10" not in {i.code for i in errors}, f"误报 E10：{[str(i) for i in errors]}")

        # ---- case 5b: E10 / W4 不该误伤合法写法
        def _one(name, ver):
            d = os.path.join(tmp, name)
            _write(d, GOOD_TREE, {
                "001-init.md": ver,
                "002-step2.md": TODO_VERSION,
                "003-step3.md": TODO_VERSION_3,
            })
            return evaluate(os.path.join(d, TREE_REL), d)

        begin("「已放弃方案」表不应误报 E10")
        _, errs, _, _ = _one("ab", ABANDONED_TABLE_VERSION)
        expect("E10" not in {i.code for i in errs}, f"误报 E10：{[str(i) for i in errs]}")

        begin("结论写「未选定」不应被当成推荐行")
        _, errs, _, _ = _one("nosel", NOT_SELECTED_VERSION)
        expect("E10" not in {i.code for i in errs}, f"误报 E10：{[str(i) for i in errs]}")

        begin("落地节点只写节点号也应算可定位")
        _, errs, _, _ = _one(
            "nid", TABLE_WITH_LANDING.replace("[v002](versions/002-step2.md)", "v002"))
        expect("E10" not in {i.code for i in errs}, f"误报 E10：{[str(i) for i in errs]}")

        begin("code block 里的引用不应被扫到")
        _, errs, warns, _ = _one("cb", CODE_BLOCK_VERSION)
        codes = {i.code for i in errs} | {i.code for i in warns}
        expect("E9" not in codes and "W4" not in codes, f"误报：{[i.code for i in errs + warns]}")

        begin("H1 里除自身标识外的裸引用仍要抓到")
        _, _, warns, _ = _one("h1ref", H1_REF_VERSION)
        expect("W4" in {i.code for i in warns}, f"漏网，实际警告：{[i.code for i in warns]}")

        # ---- case 5c: 终止态
        begin("全部完成（终止态）不应报 E8")
        done = os.path.join(tmp, "alldone")
        _write(done, ALL_DONE_TREE, {"001-init.md": GOOD_VERSION, "002-step2.md": DONE_VERSION})
        _, errs, _, _ = evaluate(os.path.join(done, TREE_REL), done)
        expect("E8" not in {i.code for i in errs}, f"终止态误报：{[str(i) for i in errs]}")

        begin("声称全部完成但仍有待完成节点应报 E8")
        fake = os.path.join(tmp, "fakedone")
        _write(fake, ALL_DONE_TREE.replace("- [x] 第二步", "- [ ] 第二步"),
               {"001-init.md": GOOD_VERSION, "002-step2.md": TODO_VERSION})
        _, errs, _, _ = evaluate(os.path.join(fake, TREE_REL), fake)
        expect("E8" in {i.code for i in errs}, f"未命中 E8，实际：{[i.code for i in errs]}")

        # ---- case 5d: E11 链接位置 / E12 表格 ID 重复
        begin("版本链接不在 versions/ 下应命中 E11")
        bp = os.path.join(tmp, "badpath")
        _write(bp, BAD_PATH_TREE, {"001-init.md": GOOD_VERSION, "002-step2.md": TODO_VERSION})
        _, errs, _, _ = evaluate(os.path.join(bp, TREE_REL), bp)
        expect("E11" in {i.code for i in errs}, f"未命中 E11，实际：{[i.code for i in errs]}")

        begin("表格 ID 重复应命中 E12")
        dup = os.path.join(tmp, "dupid")
        dup_tree = (
            "# demo · 开发状态树\n\n"
            "> 当前活动节点：`子步` → [v002](versions/002-b.md)\n\n"
            f"{TABLE_MARK}\n\n"
            "| ID | 状态 | 节点 | 版本 |\n"
            "|---|---|---|---|\n"
            "| 1 | [x] | 起点 | [v001](versions/001-a.md) |\n"
            "| 1.1 | [ ] | 子步 | [v002](versions/002-b.md) |\n"
            "| 1.1 | [ ] | 子步重复 | [v003](versions/003-c.md) |\n"
        )
        _write(dup, dup_tree, {
            "001-a.md": GOOD_VERSION,
            "002-b.md": TODO_VERSION,
            "003-c.md": TODO_VERSION_3,
        })
        _, errs, _, _ = evaluate(os.path.join(dup, TREE_REL), dup)
        expect("E12" in {i.code for i in errs}, f"未命中 E12，实际：{[i.code for i in errs]}")

        # ---- case 5e: W5 git commit 字段
        begin("git commit 填 hash / none / 占位符都不应报 W5")
        for name, ver in (("gitok", GIT_OK_VERSION), ("gitnone", GIT_NONE_VERSION),
                          ("gitph", GIT_PLACEHOLDER_VERSION)):
            _, _, warns, _ = _one(name, ver)
            expect("W5" not in {i.code for i in warns}, f"{name} 误报 W5：{[str(i) for i in warns]}")

        begin("git commit 填非法值应命中 W5")
        _, _, warns, _ = _one("gitbad", GIT_BAD_VERSION)
        expect("W5" in {i.code for i in warns}, f"未命中 W5，实际：{[i.code for i in warns]}")

        # ---- case 6: 良好树应 PASS
        begin("良性树应 PASS 且退出码 0")
        good = os.path.join(tmp, "good")
        _write(good, GOOD_TREE, {
            "001-init.md": GOOD_VERSION,
            "002-step2.md": TODO_VERSION,
            "003-step3.md": TODO_VERSION_3,
        })
        rc = run(os.path.join(good, TREE_REL), good)
        expect(rc == 0, f"期望 0，实际 {rc}")

        # ---- case 7: 地图与 mermaid 可渲染
        begin("--map / --mermaid 应可渲染")
        nodes, _, _, stats = evaluate(os.path.join(good, TREE_REL), good)
        cur = nodes[stats["current_index"]]
        expect("第二步" in render_map(nodes, cur), "路径里应含当前节点")
        expect("flowchart TD" in render_mermaid(nodes), "mermaid 输出应含图表头")

        # ---- case 8: 能力 C 的进度行
        begin("--progress 应给出可直接复制的进度行")
        prog = render_progress(nodes, cur)
        expect(prog.startswith("[1/3 已完成]"), f"进度数字不对：{prog}")
        expect("第一步 › 第二步" in prog, f"路径应为 A › B 形式，实际：{prog}")
        expect(render_progress(nodes, None).endswith("全部完成"),
               "终止态进度行应以「全部完成」收尾")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(r[0]) for r in results)
    failed = 0
    for name, ok, msg in results:
        status = "ok  " if ok else "FAIL"
        print(f"  [{status}] {name.ljust(width)}  {msg}")
        failed += 0 if ok else 1
    print(f"\nselftest: {len(results) - failed} passed, {failed} failed")
    return 0 if failed == 0 else 1


def main():
    ap = argparse.ArgumentParser(description="校验 dev-companion-skill 项目开发状态树")
    ap.add_argument("target", nargs="?", help="项目根目录 或 dev-tree/TREE.md 的路径")
    ap.add_argument("--map", action="store_true", help="打印当前路径面包屑")
    ap.add_argument("--mermaid", action="store_true", help="生成 mermaid 图")
    ap.add_argument("--progress", action="store_true",
                    help="输出一行进度（能力 C 用：已完成/总数 + 当前路径）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--selftest", action="store_true", help="校验本脚本自身")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.target:
        ap.error("需要 target，或用 --selftest")

    if os.path.isdir(args.target):
        root = args.target
        tree = os.path.join(root, TREE_REL)
    else:
        tree = args.target
        root = os.path.dirname(os.path.dirname(os.path.abspath(tree)))
    return run(tree, root, args.map, args.mermaid, args.json, args.progress)


if __name__ == "__main__":
    sys.exit(main())
