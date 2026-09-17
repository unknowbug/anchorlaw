---
name: anchor-write
description: 写 anchor 标注——@anchor.test/@anchor.idk 加合法 source（§5.5 trace/memory 规则），三语言语法（§13），写后必须验证
whenToUse: 实现或重构公开函数后写 anchor 标注时（L2，主会话内 inline 执行）
---

# anchor.write — 写 Anchor 标注

> Protocol: spec/protocol-v0.22.md §5.1/§5.2/§5.5, §13
> Layer: L2 (Anchors)
> Execution: inline

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
5. **跨载体/跨形态的 source 必须声明可比性（v0.22 §9.7.1）**：若该 anchor 的结论建立在对两个**不同执行体/不同形态**的观测上，source 之外 MUST 声明等价档位（E1 同载体单变量 / E2 跨载体 / E3 交错未知）与共同观测 key 集 `S`，并说明 `S` 之外为何无分支。E2 是正常档（跨版本/跨实现长期在此）；E3 只能声称「在已记录交错下未发现差异」。
6. **`S` 之外的量不进等价判断**（v0.22 §9.7.1 无效声明清单）：计数恒等 ≠ 集合恒等；同口径 ≠ 无伪差；合理解释 ≠ 已验证；前提存在 ≠ 前提满足。
7. **副作用的逆单独登记（v0.22 §9.8）**：验证动作的 in-place 副作用（覆盖日志、重建 index、改门控默认值）MUST 在验证记录自己的字段里登记可寻址的逆或显式不可逆声明——**不要写进 `source=` 串**（source 答「哪份记录支撑这个声称」，逆答「副作用如何被收容」，两件事）。

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
