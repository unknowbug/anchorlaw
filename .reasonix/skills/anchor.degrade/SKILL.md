---
name: anchor.degrade
description: 降级验证（§9）——代码不可独立编译时分类 Full/Partial/Degraded，登记 uncompilable_functions，遵守 3 次 retry cap
---

# anchor.degrade — 降级验证

> Protocol: spec/protocol-v0.9.md §9 (Degraded Verification)
> Layer: L2 (Anchors) — 与 anchor.test 同域（CLI 入口同为 anchorlaw test）
> Execution: subprocess

## 触发场景

生成代码依赖二进制内部符号，无法独立编译运行；`anchorlaw test` 无法执行时。

## 操作步骤

1. **分类模式**（§9.1）：
   - **Full** — 自包含 + anchorlaw 已装 → `anchorlaw test` 可跑
   - **Partial** — 有未解析外部依赖 → test 不能跑，@pt 仍须带 source（假设记录，验证推迟）
   - **Degraded** — anchorlaw 未装 → 人工对照 trace 审查
2. **判定自包含性**（§9.2）：无外部函数调用 / 无全局引用 / 无外部自定义类型 → Full；否则查依赖，全部可解析才 Full。
3. **登记**：Partial/Degraded 的函数写入 `uncompilable_functions.yaml`（函数名、源位置、未解析依赖清单、建议路径——§9.3 字段）。
4. **retry cap**（§9.4）：实现→验证循环每函数**硬上限 3 次**——超过必须回到数据层采集（动态 trace），禁止无新数据反复改假设（过程熵增）。
5. **诚实声明**（§9.5）：Partial/Degraded 下所有导出/报告前缀标注降级模式，置信度不自动提升。

## 输出

模式分类结论 / uncompilable_functions.yaml 记录 / 降级声明前缀。

## 约束

- 降级不是防御性逃避——是诚实标注当前验证天花板。
- 无新数据层证据不迭代假设。
