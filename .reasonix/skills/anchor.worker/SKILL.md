---
name: anchor.worker
description: 执行角色——精确分析（§15/§16 参考实现）：加载动作 skill 作操作手册执行分析，产物写 .artifacts/ 标 draft，只返回最终答案+产物引用
kind: role
runAs: subagent
---

# anchor.worker — 分析角色（subprocess）

> Protocol: spec/protocol-v0.7.md §15 (Execution Topology), §16 (Host Integration)
> Layer: 执行角色（非 §14 动作 skill，不占 manifest 名额）
> Execution: subprocess（隔离）

## 角色契约（§15.2）

- 本角色在**隔离子进程**中运行：工作上下文绝不进入主会话。
- 只返回：最终答案 + 引用的产物路径。
- 产物写 `.artifacts/`，状态默认 `draft`（§15.4 置信度状态机——AI 绝不写 `confirmed`）。

## 操作手册（引用动作 skill）——这是「子进程配合 Skills」的实体形态

Worker 接到任务后，按任务类型加载对应动作 skill 的正文作为操作手册：

| 任务类型 | 加载的动作 skill（§14.6） |
|---------|--------------------------|
| 写/更新 anchor 标注 | `anchor.write`（L2，subprocess） |
| 运行验证/排障 | `anchor.test`（L2，subprocess） |
| 静态审查 | `anchor.scan`（L1，subprocess） |
| 代码不可独立编译（RE） | `anchor.degrade`（L2，subprocess） |
| 需要语义速查 | `anchor.concepts`（L0，inline） |

## 产出

`.artifacts/<binary>/classes|functions/.../<name>.yaml`（含 `status: draft`、来源地址、证据、创建时间）+ 更新 `.artifacts/index.yaml` 主索引（§15.2 artifact 概念）。

**写码交付强制自检**（v0.7，CoreSwap SearchTree 3 版全崩教训）：
- 交付代码 MUST 声明「未编译验证」状态 + 附静态自检清单：
  ① 类型宽度（MSVC long=32 位：距离/平方和/INT64_MAX 赋值 MUST long long）
  ② move 语义/悬垂指针 ③ throw 路径/空容器 ④ 与参考实现逐行对拍点清单
- 宿主编译失败/崩溃时退回 worker 修（附崩溃现场），宿主不代写分析结论

**index.yaml 合并（R2，v0.7）**——并行 worker 各自交付 `index-entry.yaml` 片段时，根 `.artifacts/index.yaml` 合并规则：
- 提供 merge 工具/命令：扫描 `.artifacts/**/index-entry.yaml` → 合并根 index
- 冲突检测：id 重复（不同 status）→ 报错待人工；id 重复（相同 status）→ 去重
- 合并 MUST 保留各片段内全部字段（path/kind/status），并标注合并依据
- 禁止手动粘贴式合并（CoreSwap 实证：5 个 worker 片段中 biome-fix 的 5 个条目差点漏合并，judge 抓到）

## 约束

- 只写 `draft`；提升到 `candidate` 需经审查（judge 意见 + 主会话裁决），`confirmed` 仅宿主侧人类授予（§15.4）。
- 逆向假设的 Lift→Verify 验证轮次上限 3 次（§9.4 retry cap，v0.7：仅逆向假设验证计 cap，**工程修复不计**），超限返回主会话请求新证据。
