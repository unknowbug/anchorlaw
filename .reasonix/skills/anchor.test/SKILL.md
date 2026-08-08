---
name: anchor.test
description: 运行验证——执行 anchorlaw test 按 §5.4 健康状态解读结果，代码不可独立编译时转 anchor.degrade
---

# anchor.test — 运行验证

> Protocol: spec/protocol-v0.6.md §5.4 (Anchor Health States), §9 (Degraded Verification)
> Layer: L2 (Anchors)
> Execution: subprocess

## 触发场景

添加 anchor 后验证、CI 失败排查时。

## 操作步骤

1. 运行（CLI，§14.4）：`anchorlaw test [module]`（`-v` 显示完整 traceback）。
2. 按健康状态解读（§5.4）：
   - `healthy` → 通过，声称已验证
   - `degrading` → 有测试失败：之前验证过的行为坏了 → 修复或更新 anchor，不得静默
   - `unverified` → 只有 idk：探索区，正常
   - `stale_unknown` → idk 超 90 天且函数改过（§5.3）→ 升级处理
   - `uncompilable` → 代码无法独立编译 → 按 §9 降级验证分类（Full/Partial/Degraded）处理，不硬跑
3. 无法独立编译的代码（RE 场景）先按 §9 分类模式，再决定能否运行。

## 输出

测试结果 + 每函数健康状态。

## 约束

- 只通过 CLI 运行（§14.4）。
- 失败不掩盖：degrading 如实报告。
