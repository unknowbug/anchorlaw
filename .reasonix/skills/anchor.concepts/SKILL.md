---
name: anchor.concepts
description: anchor 语义速查——test/idk、source 格式、staleness、健康状态、三语言等价（§5/§13），写或审 anchor 前调用
---

# anchor.concepts — Anchor 语义速查

> Protocol: spec/protocol-v0.14.md §5 (Anchor Semantics), §13 (Anchor Abstraction)
> Layer: L0 (Concepts) — 仅作语义参考，自身不执行任何操作
> Execution: inline

## 触发场景

写或审查 anchor 标注之前，需要 anchor 语义定义时调用本 skill（供 L1–L4 引用）。

## 核心语义

- **@anchor.test** = 可验证声称：`description`（人类可读）+ `test_fn`（可执行谓词）+ `source`（必填，v0.3+）
- **@anchor.idk** = 诚实边界声明：`what`（具体未知项），`source` 可选
- **source 类型**（§5.5）：`trace` / `memory` 允许 @test；`static` 仅允许 @idk。@test 无 source 或 static → INVALID
- **staleness**（§5.3）：@idk 超 90 天且函数已修改 → 升级为 WARNING
- **健康状态**（§5.4）：`healthy` / `unverified` / `degrading` / `stale_unknown` / `skeleton` / `uncompilable`
- **三语言等价**（§13）：Python 装饰器 / TypeScript JSDoc 注释 / C++ 行注释 `// @anchor.*`，验证载体可不同（test_fn / assert / probe binary）

## 输出

一份语义澄清：回答当前任务涉及的 anchor 语义问题。不写代码、不跑命令。

## 约束

- 写 anchor 用 `anchor.write`；验证用 `anchor.test`；本 skill 只回答「是什么」。
