# v002 · 搭最小骨架，能本地跑起来

- 父节点：启动：确认目标与技术栈
- 写入时间：2026-10-04 11:05
- git commit：none

## 1. 交付目标

`index.js` 里能区分两种请求：`POST /create` 和 `GET /s/<code>`，各自返回可识别的占位响应。

## 2. 决策记录

本节点由「先做哪件事」这个决定产生。

**问题**：接下来有三件事可做 —— ① 打通跳转 ② 存数据 ③ 加管理页面。先做哪个？

| 候选 | 做法 | 好处 | 代价 | 结论 | 落地节点 |
|---|---|---|---|---|---|
| `jump-first` | 假的短码写死在代码里，先把访问/跳转跑通 | 最先看到「点一下就跳过去」的效果，成就感来得早 | 数据在内存里，重启就丢 | **推荐** | → [v003](versions/003-redirect-choice.md) |
| `persist-first` | 先把 SQLite 的表和读写写好 | 数据不丢 | 跳之前还得先写一堆数据库代码，很久看不到东西跳出来 | 落选 | → [v006](versions/006-sqlite.md) |
| `admin-first` | 先做录入界面 | 有界面可以点 | 没有跳转逻辑的界面等于空壳 | 落选 | → [v007](versions/007-admin.md) |

**用户选择**：`jump-first` — 理由：先看到效果，知道自己没走偏。

于是 `jump-first` 被拆成 [v003](versions/003-redirect-choice.md)（跳转方式定稿）
→ [v004](versions/004-redirect-impl.md) / [v005](versions/005-shortcode.md)；
`persist-first` 与 `admin-first` 没有放弃，只是排在后面（[v006](versions/006-sqlite.md) / [v007](versions/007-admin.md)）。

## 3. 当时项目状态

- 目录 / 文件：`index.js`
- 怎么跑起来：`node index.js`
- 已实现：
  - `POST /create` → 返回 `{"code":"abc123"}`（写死的假短码）
  - `GET /s/abc123` → 返回 `would redirect to <原网址>`（还没真的跳转）

## 4. 完成证据

- 验证命令：`curl -X POST localhost:3000/create` 与 `curl -s localhost:3000/s/abc123`
- 实际输出：分别得到 `{"code":"abc123"}` 和 `would redirect to https://example.com`
- 验证时间：2026-10-04 11:18

## 5. 下一步 / 未决

- 跳转到底用 301 还是 302，需要用户定（[v003](versions/003-redirect-choice.md)）。
