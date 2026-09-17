---
name: anchor-test
description: 运行验证——执行 anchorlaw test 按 §5.4 健康状态解读结果，代码不可独立编译时转 anchor.degrade
whenToUse: 添加 anchor 后验证、CI 失败排查时（L2，主会话内 inline 执行）
---

# anchor.test — 运行验证

> Protocol: spec/protocol-v0.22.md §5.4 (Anchor Health States), §9 (Degraded Verification)
> Layer: L2 (Anchors)
> Execution: inline

## 触发场景

添加 anchor 后验证、CI 失败排查时。

## 操作步骤

1. **运行前置——副作用与逆（v0.22 §9.8）**：跑之前先看本轮会留下什么 in-place 副作用。同标签已有产物 → **先归档或换标签**再跑（#144/#146 的协议化）；会重建 `index.yaml` 之类就地写入的产物 → 先备份（重建式写入会静默丢弃白名单外字段）。derived 类（新命名产物/新临时目录）无需处理。逆指针登记在验证记录自己的字段里，**不要塞进 `source=` 串**。
2. 运行（CLI，§14.4）：`anchorlaw test [module]`（`-v` 显示完整 traceback）。
3. 按健康状态解读（§5.4）：
   - `healthy` → 通过，声称已验证
   - `degrading` → 有测试失败：之前验证过的行为坏了 → 修复或更新 anchor，不得静默
   - `unverified` → 只有 idk：探索区，正常
   - `stale_unknown` → idk 超 90 天且函数改过（§5.3）→ 升级处理
   - `uncompilable` → 代码无法独立编译 → 按 §9 降级验证分类（Full/Partial/Degraded）处理，不硬跑
4. 无法独立编译的代码先按 §9 分类模式，再决定能否运行。
5. **判据前置集（v0.22 §15.4）**：若本轮结果要用于某条验收判据，先核该判据声明的 `preconditions` 当前是否仍满足；失效 → 判据 suspended、结论标注前提已失效待复核——**不改任何 status**。

## 输出

测试结果 + 每函数健康状态 + 本轮 in-place 副作用的逆登记（或不可逆声明）。

## 约束

- 只通过 CLI 运行（§14.4）。
- 失败不掩盖：degrading 如实报告。
- **不自动回退**副作用（§9.8）：失败轮的日志与产物是更有价值的证据。
