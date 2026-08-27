---
name: anchor-scan
description: 静态审查——跑 scanner 找 P1-P6 防御性模式，按 ERR/WARN/INFO 分级处理 findings（§6），疑似误报转 anchor.challenge
whenToUse: 模块并入审查前（流水线 stage 3）或收到防御性模式报告时（L1；DSH 中经 subagent 工具隔离执行，也可主会话直接跑扫描器工具）
---

# anchor.scan — 静态审查

> Protocol: spec/protocol-v0.19.md §6 (Scanner Pattern Catalog), §7 Level 1
> Layer: L1 (Scanner)
> Execution: subprocess

## 触发场景（触发点，MUST 强度）

以下两个触发点 MUST 运行本 skill（改完代码待提交前，或收到防御性模式报告时）：

1. **模块并入审查前（流水线 stage 3）**（与 §15.4 门禁中 judge 审查配套；v0.10 流水线 stage 5 并入审查）：Worker 完成模块、或主 Agent 完成代码改动后，先跑 scan 获得 findings 清单并逐条处置，再交 Judge 并入审查——scan 的 findings 清单是 Judge 审查的机械证据来源之一（AGENTS.md 将 scan 列为「发散型优化例外」：触发必跑，执行方式 subprocess 可选，二者不冲突）。
2. **收到防御性模式报告时**：CI 报告 / scanner 输出 / 他人反馈疑似防御性模式，MUST 跑 scan 核实后再处置，不得凭感觉判断「没问题」。

**计划预置（§15.4 Plan-time placement 精神）**：工作流计划（todo）在规划阶段预置本 skill 的触发步骤；到达并入审查步骤时发现未预置/未执行 → MUST 停下补跑 scan 再进入审查，不得跳过。

**反模式（触发不完整即进入审查/提交）**：
- 跳过 scan 直接交并入审查或交付，无 findings 处置记录
- 收到防御性模式报告不跑 scan，直接凭感觉判断「没问题」
- 静默忽略 WARNING（无「补 anchor 或修」处理决定，与操作步骤 §6.1 分级一致）

## 操作步骤

1. 运行扫描（CLI，§14.4）：
   - `anchorlaw-scanner check <dir>`（独立 scanner 包，Python 防御模式）
   - `anchorlaw-scanner check --lang cpp <dir>`（C++ @anchor 标注提取验证，§8 annotation-extraction）
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
