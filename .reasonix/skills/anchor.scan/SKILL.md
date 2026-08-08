---
name: anchor.scan
description: 静态审查——跑 scanner 找 P1-P6 防御性模式，按 ERR/WARN/INFO 分级处理 findings（§6），疑似误报转 anchor.challenge
---

# anchor.scan — 静态审查

> Protocol: spec/protocol-v0.7.md §6 (Scanner Pattern Catalog), §7 Level 1
> Layer: L1 (Scanner)
> Execution: subprocess

## 触发场景

改完代码待提交前，或收到防御性模式报告时。

## 操作步骤

1. 运行扫描（CLI，§14.4）：
   - `anchorlaw-scanner check <dir>`（独立 scanner 包）
   - 或 `anchorlaw check <dir>`（完整包内置入口，`--no-recursive` 可关递归）
2. 解读输出分级（§6.1）：
   - **ERROR** → 必须修（吞噬异常、无意义测试等致命模式）
   - **WARNING** → 纯逻辑公开函数缺 anchor 等，高锚定价值 → 补 anchor 或修
   - **INFO** → I/O 类函数缺 anchor，锚定价值低 → 补 @anchor.idk 或忽略
3. 提交前确认 ERROR = 0，且 WARNING 均有处理决定。

## 输出

findings 清单 + 每个 finding 的处理决定（修 / 补 idk / 忽略 / 挑战）。

## 约束

- 只通过 CLI 扫描，不 import 内部 API（§14.4）。
- 疑似误报必须走 `anchor.challenge`（§12），不得静默忽略。
