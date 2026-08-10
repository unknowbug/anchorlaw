---
name: anchor.noise
description: 噪声卡管理——运行时失败积累为结构化知识：创建（唯一代码内钩子）/列出/搜索/解决转回归测试
---

# anchor.noise — 噪声卡管理

> Protocol: spec/protocol-v0.15.md §3 (Noise Card JSON Schema)
> Layer: L3 (Noise)
> Execution: inline

## 触发场景

运行时观察到失败/异常；或存在未解决噪声卡积压时。

## 操作步骤

1. **创建**（§14.4 唯一代码内钩子，无 CLI 入口）——在捕获失败的 `except` 块中调用：
   ```python
   import anchorlaw as pract  # 需已安装 anchorlaw（stub 仅含 test/idk）
   try:
       result = func(bad_input)
   except Exception as e:
       pract.create_noise_card(
           trigger="func(bad_input)",
           function_name="func",
           observed=f"抛出 {type(e).__name__}: {e}",
           expected="应返回默认值而非崩溃",
           discovery="函数未处理该输入形态",
           curriculum="处理外部输入时先校验形态，再执行运算",
       )
       raise
   ```
   必填字段：`noise_id`(自动) / `timestamp`(自动) / `trigger` / `function_name` / `observed` / `expected`（§3 schema）。
2. **列出**：`anchorlaw noise list`（`--all` 含已解决）
3. **搜索**：`anchorlaw noise search <keyword>`
4. **解决**（转为回归测试）：`anchorlaw noise resolve <noise_id> --converted-test "<测试描述>"`

## 输出

创建的噪声卡 / 积压清单 / 搜索命中 / 解决记录。

## 约束

- `curriculum` 必须可操作（可复用教训），不写空话。
- 除创建外的所有管理操作一律 CLI（§14.4）。
