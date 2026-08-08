---
name: anchor.write
description: 写 anchor 标注——@anchor.test/@anchor.idk 加合法 source（§5.5 trace/memory 规则），三语言语法（§13），写后必须验证
---

# anchor.write — 写 Anchor 标注

> Protocol: spec/protocol-v0.7.md §5.1/§5.2/§5.5, §13
> Layer: L2 (Anchors)
> Execution: subprocess

## 触发场景

实现或重构完一个公开函数后，为该函数声明验证锚点。

## 规则

1. **每个公开函数必须有 ≥1 个 test 或 ≥1 个 idk**（§5.1 compile-time check）。
2. **@anchor.test 必须带 source**（§5.5）：
   `source="<type>:<binary_or_file>!<function>#<id>, offset=<addr>, <key_observations> observed <ISO8601>"`
   - source 类型：`trace`（动态调试快照）/ `memory`（内存转储）→ 允许 @test
   - `static`（静态分析推断）→ 仅允许 @idk；@test 用它或缺失 → INVALID
3. **无法验证的边界 → 诚实写 @anchor.idk**（§5.2），禁止写假 test 凑数。
4. source 字符串实现 MUST 原样保留（审计用途）。

## 三语言语法（§13）

| 语言 | 声明位置 | 验证载体 |
|------|---------|---------|
| Python | 装饰器 | `test_fn` lambda |
| TypeScript | JSDoc 注释（inert） | 运行时 assert |
| C++ | 行注释 `// @anchor.test("desc", source="...")` / `// @anchor.idk("desc")`（inert） | 独立 probe binary |

## 输出

写入的 anchor 标注（含合法 source）。

## 约束

- 语义照 §5，不复制协议原文。
- 写完后跑 `anchor.test` 验证。
