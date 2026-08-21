# Anchorlaw — DeepSeek Harness 上的代码验证工具链

**[English](README.md) | [中文](README_zh.md)**

> **"任何声称都必须有可验证的实践锚点。"**
>
> —— 唯物实践论 第一律（实践锚定剃刀）

Anchorlaw 是一套**面向 AI 辅助（vibe）开发的代码验证工具链**，当前以 **DeepSeek Harness（DSH）宿主适配**形态维护：`dsh/` 子树提供 11 个协议技能、4 个模型工具与 `anchorlaw` agent preset——安装一次，每个 DSH 会话都能获得 扫描 / 报告 / 噪声卡 / AI 上下文注入 能力。底层协议（`spec/`、`python/`、`typescript/`）语言无关，是 DSH 工具的执行后端。Reasonix 宿主格式**已归档、不再维护**——见 [Reasonix 版存档](#reasonix-版存档)。

---

## 快速开始（DSH）

```powershell
# 1. 安装一次（宿主级默认）：preset + 用户技能 + 全局工具挂载
pwsh dsh/scripts/install.ps1
# 2. 五项自检：工具链 / 技能 manifest / 自扫 / 安装产物 / 工具 schema
pwsh dsh/scripts/selfcheck.ps1
# 3. 新开 DSH 会话 → 每个会话都有 4 个 anchorlaw_* 工具 + 11 个 anchor-* 技能
```

按项目安装（Reasonix 式）：`pwsh dsh/scripts/install.ps1 -Project /path/to/project`——11 个技能只在那个项目的工作区会话加载。

> 工具在**新会话**出现（会话 composition 创建时固定）。全局挂载前有工具 schema 校验门禁（2026-08-13 事故门禁）——坏 schema 不可能被装进全局。

## 你能获得什么（DSH）

### 4 个模型工具——全局、每个会话可用

| 工具 | 作用 |
|------|------|
| `anchorlaw_scan` | L1 防御模式扫描器（P1-P6；`lang` 可选 cpp/go/java 注释式提取） |
| `anchorlaw_report` | 健康报告（扫描发现 + 噪声卡积压 + 诊断结论） |
| `anchorlaw_ai_context` | 噪声卡 + 课程导出（LLM 上下文注入） |
| `anchorlaw_status` | 工具链版本 + 已发现 `anchor-*` 技能 |

### 11 个协议技能（`anchor-*`，DSH 格式）

L0-L4 动作技能 + 执行角色（scout/worker/judge），按场景加载；技能正文在 `dsh/skills/`（唯一事实源，协议 §14 是宿主无关的技能规范）。触发索引与工具调用约定见 `dsh/AGENTS.md`。

### anchorlaw agent preset

Judge 驱动四段流水线人格（协议 §15.4）：输入契约 → 实施规范 → 计划 → 并行实施 → 交付。判据先行、3 轮硬停止、`confirmed` **只能由人类授予**；scout/worker/judge 经隔离 subagent 委派。

---

## 协议核心（语言无关后端）

协议本体在仓库根、宿主中立——DSH 工具驱动它的 CLI：

| 组件 | 位置 | 状态 |
|------|------|------|
| **协议正文** | `spec/protocol-v0.18.md` | 语言无关代码验证协议（当前版） |
| **Python** | `python/anchorlaw-scanner` + `python/anchorlaw` | 扫描器（已验证）+ 锚点/噪声/CLI（实验性）——DSH 工具后端 |
| **TypeScript** | `typescript/anchorlaw-scanner` | TS/JS 扫描器（开发中） |

### 各组件成熟度

| 组件 | Python | TypeScript | 成熟度 |
|-----------|--------|-----------|--------|
| **扫描器** | ✅ [anchorlaw-scanner](python/anchorlaw-scanner/) | ✅ [anchorlaw-scanner](typescript/anchorlaw-scanner/) | **已验证** — 在真实项目上测试通过 |
| **锚点系统** | ✅ [anchorlaw](python/anchorlaw/) | — | **实验性** — API 稳定，缺乏实践效能数据 |
| **Source Provenance (v0.3/v0.7)** | ✅ `source` 参数 + probe 类型（v0.7） | — | **SCOPED** — Python 已实现；1 个项目（CoreSwap）产出过带 source 的 anchor |
| **噪声卡** | ✅ [anchorlaw](python/anchorlaw/) | — | **未验证** — schema 已定义，无项目积累 |
| **AI 上下文注入** | ✅ [anchorlaw](python/anchorlaw/) | — | **猜想** — 格式已定义，未做 A/B 对照实验 |
| **降级验证 (v0.3)** | — | — | **猜想** — 三种模式已定义，无参考宿主之外的项目走过 |

> **诚实声明**：标记为"实验性""未验证""猜想"的组件是工作假设。它们的价值尚未通过实践检验。邀请你帮助我们检验这些假设——而非因为我们声称它们有效。

### 更新日志

> **v0.18 (2026-08-13):** DSH 宿主适配——DSH 成为首个完整实现 §16 宿主接入契约全部接口点的宿主（11 技能、4 工具、anchorlaw preset、宿主级全局工具挂载、项目级安装）。修复（2026-08-15）：`anchorlaw noise resolve` 接受 `noise list` 打印的短后缀 ID；补 4 个单元测试。**v0.18 同时归档 Reasonix 宿主格式**（`.reasonix/skills/` → `archive/reasonix/`）；`dsh/skills/` 成为技能唯一事实源。
>
> **v0.17 (2026-08-12):** §12 挑战裁决（Reasonix/Go 实测）——parse-error 标记（INFO，绝不归入 P1-P6）；注释式语言声称降级（仅标注提取）；P7-P10 可靠性风险模式定义。
>
> **v0.16 (2026-08-10):** Go/Java 登记为注释式语言；Rust 声明不需要支持。
>
> **v0.15 (2026-08-10):** C 门禁硬停止——同一判据 3 轮未达标 MUST 停止流水线；Judge 提交完整报告交人类判定。
>
> **v0.14 (2026-08-10):** 输入契约分层——契约 = 已确认需求 + 技术约束；架构设计属 stage-1 产出；§16.1 交接判据通用化为协议中立确认判据。
>
> **v0.13 (2026-08-10):** §12 挑战裁决——构造性限定到输入契约域（RE 在域外）；§16.1 RE 交接判据；§9.4 retry cap 升级为证据饱和（3 轮无新数据层证据）。
>
> **v0.12 (2026-08-10):** C 门禁机械防呆恢复——同一判据迭代封顶 3 轮，第 4 轮机械升级人类。
>
> **v0.11 (2026-08-10):** 输入契约边界——需求发掘从 Anchorlaw 摘出（独立需求协议）；四段 Judge 驱动流水线。
>
> **v0.10 (2026-08-10):** Judge 驱动编程——判据先行（§15.4）；AGENTS.md 改为只索引不复制。
>
> **v0.9 (2026-08-08):** judge 制度化——审查门成为决策点强制检查点；验证终止门禁（外部测试集、三层意见分级、3 轮上限）。
>
> **v0.8 (2026-08-08):** 收敛门模型——唯一 subagent 角色为 judge；`anchor.write`/`anchor.test` 改 inline。
>
> **v0.7 (2026-08-08):** 首个宿主实践反馈（CoreSwap 8576-24blocks）——source 落盘 + `probe` 类型（§5.5）、retry cap 范围、执行者分离、judge 三源交叉核对。
>
> **v0.6 (2026-08-08):** Agent Execution Topology（§15）+ Host Integration Contract（§16）。
>
> **v0.5 (2026-08-08):** Agent Skill Manifest（§14）——参考实现当时随 `.reasonix/skills/` 提供（现已归档）。
>
> **v0.3 (2026-06-18):** Source Provenance、降级验证模式、Verify 重试上限。详见 [协议规范 v0.3](spec/protocol-v0.3.md)。

---

## Reasonix 版存档

Reasonix 宿主格式（`.reasonix/skills/`——11 个 `anchor.*` 技能——与 Reasonix 版 AGENTS.md）自 v0.18 起**不再维护**，归档在 `archive/reasonix/`。

如需基于 Reasonix 版本继续迭代：**Fork 本仓库**后运行

```powershell
pwsh archive/reasonix/restore-reasonix.ps1
```

脚本会把 `.reasonix/skills/` + Reasonix 版 `AGENTS.md` 恢复到仓库根——得到完整的 Reasonix 工作副本自行迭代（详见 [`archive/reasonix/RESTORE.md`](archive/reasonix/RESTORE.md)）。上游不再更新它。

---

## 项目结构

```
anchorlaw/
├── dsh/                           # DSH 宿主适配层（当前维护）
│   ├── skills/                    # 11 个 anchor-* 技能（唯一事实源）
│   ├── plugins/                   # anchorlaw-tools.js — 4 个模型工具
│   ├── preset/                    # anchorlaw agent preset（Judge 驱动流水线）
│   ├── scripts/                   # install.ps1 / selfcheck.ps1
│   └── AGENTS.md                  # DSH 维护入口
├── spec/
│   └── protocol-v0.18.md          # 语言无关协议（当前版）
├── python/                        # 协议实现（DSH 工具后端）
│   ├── anchorlaw-scanner/         # 独立扫描器（Level 1, 已验证）
│   └── anchorlaw/                 # 锚点 / 噪声 / CLI（Level 2-4, 实验性）
├── typescript/
│   └── anchorlaw-scanner/         # TS/JS 扫描器（Level 1, 开发中）
└── archive/
    └── reasonix/                  # Reasonix 宿主格式存档（不再维护；Fork 后可恢复）
```

---

## 参与贡献

本项目目前最需要的不是 PR 辩论，而是**实践数据**。

最有价值的贡献方式：
1. **跑扫描器**（DSH 里用 `anchorlaw_scan`，或命令行 `anchorlaw-scanner check`）——在你的项目上跑，报告误报
2. **使用锚点系统**——在真实项目上用 2 周以上，告诉我们它帮助了还是阻碍了
3. **积累噪声卡**——我们需要有 30+ 张噪声卡的项目来测试 AI 上下文注入的效果

在 GitHub Discussions 开启讨论，或在 Issues 提交你的发现。

---

## 参考

- [协议规范 v0.18](spec/protocol-v0.18.md)
- 降级验证：[协议 §9](spec/protocol-v0.18.md#9-degraded-verification-v03-draft)
- 唯物实践论方法论——本协议的哲学基础

---

> "这个项目不承诺永恒的真理。它承诺一套在当前历史条件下锻造的最趁手的工具，并对更好的工具保持开放。它的最高承诺，是让使用者最终有能力质疑、改进、乃至超越它本身。"
>
> —— 第一律，反身性应用
