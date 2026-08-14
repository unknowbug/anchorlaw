# Anchorlaw 协议

**[English](README.md) | [中文](README_zh.md)**

> **"任何声称都必须有可验证的实践锚点。"**
>
> —— 唯物实践论 第一律（实践锚定剃刀）

Anchorlaw 是一套**面向 vibe coding 的代码验证协议**——不是测试框架，不是 lint 工具。

它检测暴露认知盲区的**防御性代码模式**，并为 AI 辅助开发提供**结构化的反馈闭环**。

---

## 各组件成熟度（按第一律反身性标注）

| 组件 | Python | TypeScript | 成熟度 |
|-----------|--------|-----------|--------|
| **扫描器** | ✅ [anchorlaw-scanner](python/anchorlaw-scanner/) | ✅ [anchorlaw-scanner](typescript/anchorlaw-scanner/) | **已验证** — 在真实项目上测试通过 |
| **锚点系统** | ✅ [anchorlaw](python/anchorlaw/) | — | **实验性** — API 稳定，缺乏实践效能数据 |
| **Source Provenance (v0.3/v0.7)** | ✅ `source` 参数 + probe 类型（v0.7） | — | **SCOPED** — Python 已实现（source 参数、缺失/static 对 test 标 INVALID、`probe:` 类型 v0.7）；1 个项目（CoreSwap）产出过带 source 的 anchor |
| **噪声卡** | ✅ [anchorlaw](python/anchorlaw/) | — | **未验证** — schema 已定义，无项目积累超过 10 张卡 |
| **AI 上下文注入** | ✅ [anchorlaw](python/anchorlaw/) | — | **猜想** — 格式已定义，未做 A/B 对照实验 |
| **降级验证 (v0.3)** | — | — | **猜想** — 三种模式已定义，无参考宿主之外的项目走过 Partial/Degraded 路径 |

> **诚实声明**：标记为"实验性""未验证""猜想"的组件是工作假设。它们的价值尚未通过实践检验。邀请你帮助我们检验这些假设——而非因为我们声称它们有效。
>
> **v0.17 更新 (2026-08-12):** §12 挑战裁决（Reasonix/Go 实测）——① parse-error 标记：不可解析的源文件是工具层 `parse-error`（INFO），绝不归入 P1-P6 模式（SyntaxError 曾被误分类为吞噬异常）；② 注释式语言声称降级：Go/Java/C++ 注册 = 仅标注提取，P1-P6 缺陷检测未映射；③ 新增 4 个语言无关可靠性风险模式 P7-P10（生命周期/状态机/路径协调/复杂度），实现按语言映射。
>
> **v0.16 更新 (2026-08-10):** Go/Java 登记为注释式语言（行注释 `// @anchor.*`，声明位置同 C++；独立 probe/test binary 为验证载体），参考提取器已接线（annotation-extraction）。Rust 声明不需要支持——其编译器/借用检查/测试框架自带本协议要加的验证；proc-macros 计划废弃（§2.4/§13）。
>
> **v0.15 更新 (2026-08-10):** C 门禁硬停止升级——同一验收判据 3 轮未达标（review 仍在报未解决问题）后，流水线 MUST 整个停止：Judge 提交 Review 情况与问题详细报告交人类判定（判据错 → §12/修正，方向错 → 回规划，或人类另行裁决）。第 4 轮 Judge 预分类被移除——未经人类决定不得继续迭代、修复或再 review（§15.4）。
>
> **v0.14 更新 (2026-08-10):** 输入契约分层——输入契约澄清为「已确认需求 + 技术约束规范」（客户可确认的事实：声称/边界/术语/技术约束）；架构设计（模块化/依赖方向/接口）在流水线 stage-1 产出，不随输入契约带入。§16.1 交接判据通用化为协议中立的 input-contract confirmation criterion（语义收敛）——不点名、不适配任何上游框架；三个协议（需求 / Anchorlaw / 逆向）是相互独立可操作的框架。
>
> **v0.13 更新 (2026-08-10):** §12 挑战裁决——「编程是构造型」限定到输入契约域（登记进 §11 审计；RE 明确在域外——探索型、验证无界，两种模式互补）。§16.1 RE 交接判据：只有 vanilla 行为模型收敛后输入契约才算已确认；混合任务只在确定子部分进入 Anchorlaw。§9.4 retry cap 升级为证据饱和——3 轮无新数据层证据，而非 3 轮。
>
> **v0.12 更新 (2026-08-10):** C 门禁机械防呆恢复——判据先行保留（实现前确定验收判据；每段以 Judge 点头终止），同一验收判据的迭代封顶 3 轮，第 4 轮 MUST 机械升级人类（判据错 → §12 挑战/修正；方向错 → 回规划）。v0.10 的 Judge-nod-only 形式依赖 Judge 识别「持续失败」——正是门禁要防的失败形态（反复轮次而不自知）（§15.4）。
>
> **v0.11 更新 (2026-08-10):** 输入契约边界——需求发掘从 Anchorlaw 摘出：它属于独立的需求协议（Scout 驱动 + 人机对话 + Judge 技术审核），其产出（已确认需求 + 软件规范定义）是 Anchorlaw 的 stage-0 输入契约。Anchorlaw 运行四段 Judge 驱动流水线（输入契约 → 实施规范 → 计划 → 并行实施 → 交付）。三协议闭环：需求协议 → Anchorlaw → RE 框架（§15.1、§16.1）。
>
> **v0.10 更新 (2026-08-10):** Judge 驱动编程——编程是构建型任务（不是逆向的探索型）：工作流以 Judge 驱动 + 判据先行（§15.4）。Scout/Worker 角色重新引入为通用编程角色；AGENTS.md 改为只索引不复制（镜像漂移是 v0.9 review 循环的根因）。
>
> **v0.9 更新 (2026-08-08):** judge 制度化——审查门是决策点的强制检查点，不只是收尾门：`confirmed` 授予前必须有 judge 审查意见；重大转向（结案重开/根因定论/范围决策）必须过 judge；自评不构成审查门；计划阶段预置 judge 步骤（§15.4）。验证终止门禁：收敛以机械判据终止（外部测试集、三层意见分级——blocking 仅限测试/编译/声称矛盾、3 轮上限）——不再有无尽 review 循环（§15.4）。
>
> **v0.8 更新 (2026-08-08):** 收敛门模型——编程是线性收敛：主 Agent 全程持有上下文并亲自写；唯一受认可的 subagent 角色是审查门（judge）。`anchor.write`/`anchor.test` 改为 `inline`。
>
> **v0.7 更新 (2026-08-08):** 首个宿主实践反馈（CoreSwap 8576-24blocks）并入——source 落盘证据 + `probe` source 类型（§5.5）、retry cap 范围澄清（§9.4）、验证执行者分离（§9.6）、order-dependent 语义等价（§13）、judge 三源交叉核对（§15.4）。
>
> **v0.6 更新 (2026-08-08):** Agent Execution Topology（§15）+ Host Integration Contract（§16）——四层接口面完整：声称（§13）/ 知识（§14）/ 执行隔离（§15）/ 宿主接入（§16）。subprocess 型 skill 让主会话保持干净。
>
> **v0.5 更新 (2026-08-08):** Agent Skill Manifest（§14）——分层、单职责的 skills 把协议知识改为按需加载，修复 Agent 侧注意力稀释。参考实现随仓库提供（`.reasonix/skills/`）。
>
> **v0.3 更新 (2026-06-18):** 新增 Source Provenance（数据来源标注）、Degraded Verification（三种验证模式）、Verify 重试上限。详见 [协议规范 v0.3](spec/protocol-v0.3.md)。

---

## 快速开始

### 扫描器（即时可用）

```bash
# Python
pip install anchorlaw-scanner
anchorlaw-scanner check src/

# TypeScript
npm install anchorlaw-scanner
npx anchorlaw-scanner check src/

# C++（@anchor 注释式标注提取验证 — annotation-extraction, Level 1）
anchorlaw-scanner check --lang cpp src/
```

扫描器检测以下防御性模式：

- **吞噬异常** — `except: pass` / `catch {}`
- **宽泛捕获** — `except Exception:` / `catch (e: any)`
- **缺少实践锚点** — 公开函数既无 `@pt` 也无 `@idk`
- **防御性空值传导** — 连续 3 处以上 `if x is None: return None`
- **无意义测试** — `assert f(x) == f(x)`
- **模糊 TODO** — `// TODO: fix` 无问题追踪编号

### 完整协议（实验性）

```bash
pip install anchorlaw
```

```python
from anchorlaw import test as pt, i_dont_know as idk

@pt("空列表返回空",
    lambda: process([]) == [],
    source="trace:process#000, input=[] output=[] observed 2026-06-18")  # v0.3: source 字段记录数据来源
@pt("保留正数",
    lambda: process([-1, 0, 3, -5]) == [3],
    source="trace:process#001, input=[-1,0,3,-5] output=[3] observed 2026-06-18")
@idk("超大列表（>1M）的行为边界尚未确定",
    source="static: 未在trace中覆盖大输入")
def process(data: list[int]) -> list[int]:
    return [x for x in data if x > 0]
```

### 噪声卡（运行时失败积累）

```python
import anchorlaw

try:
    result = divide(6, 0)
except Exception as e:
    anchorlaw.create_noise_card(
        trigger="divide(6, 0)",
        function_name="divide",
        observed=f"抛出 {type(e).__name__}",
        expected="应返回 Err('DivByZero')",
        discovery="除零检查在某条调用路径中被绕过",
        curriculum="在学校所有入参之后再执行运算操作",
    )
    raise
```

### AI 上下文导出

```bash
python -m anchorlaw ai-context --functions "divide,process" --limit 10
```

输出可直接注入 LLM 系统提示词的结构化文本。

### 降级验证模式（v0.3）

Anchorlaw 承认一个工程现实：**不是所有带 anchor 的代码都能独立编译运行。** 生成代码常常依赖二进制内部符号，脱离原始环境无法编译。

因此协议定义了三种运行模式：

| 模式 | 条件 | anchorlaw test | 置信度自动提升 |
|------|------|:---:|:---:|
| **全功能** | 代码自包含 + Anchorlaw 已安装 | ✅ | ✅ |
| **半功能** | 代码有未解析的外部依赖 | ❌ | ❌（anchor 仍记录 source，验证推迟） |
| **降级** | Anchorlaw 未安装 | ❌ | ❌（人工对照 trace 审查） |

这不是防御性条款——是诚实地标注当前能做到什么。详见 [协议规范 §9](spec/protocol-v0.17.md#9-degraded-verification-v03-draft)。

---

## DeepSeek Harness（DSH）宿主适配层

同一协议、单一仓库：`dsh/` 子树是 DSH（DeepSeek Harness）宿主适配层——协议核心留在仓库根，DSH 生态适配在 `dsh/`（由 DSH agent 大肥鱼维护）：

- **11 个协议技能** — `dsh/skills/` 持有 DSH 格式技能（`anchor-*`，kebab-case + `whenToUse`）；正文派生自 `.reasonix/skills/`，由 `dsh/tests/test_manifest.py` 做正文级一致性守护
- **模型工具** — `dsh/plugins/anchorlaw-tools.js` 注册 4 个工具：`anchorlaw_scan`（L1 扫描器）、`anchorlaw_report`（健康报告）、`anchorlaw_ai_context`（噪声卡 + 课程注入）、`anchorlaw_status`（工具链状态）
- **Agent preset** — `dsh/preset/` 打包 `anchorlaw` preset：Judge 驱动四段流水线人格（规范 §15.4），scout/worker/judge 经隔离 subagent 委派

```powershell
# 宿主级（默认）：用户级 preset + 技能 + 全局工具挂载（写入活动 profile 的 cordis.patch.yml）；可再生成——禁止手改
pwsh dsh/scripts/install.ps1
# 项目级（Reasonix 式）：技能只在 <目录> 工作区的会话加载，离开即无
pwsh dsh/scripts/install.ps1 -Project E:\path\to\project
# 五项自检：工具链 / 技能 manifest / scanner 自扫 / 安装产物 / 插件工具 schema
pwsh dsh/scripts/selfcheck.ps1
```

宿主级安装把 4 个 `anchorlaw_*` 工具**全局挂载**：以 `insert` 形态写入 `<dshHome>/profiles/<profile>/cordis.patch.yml`（DSH 唯一读取的用户补丁层，热重载），插件文件落 `<profile>/plugins/anchorlaw/`。挂载前由 `dsh/tests/check_plugin_schema.mjs` 把关——每个工具的 `parameters` 必须是编译后的 JSON Schema 对象根；扁平 spec 会以无顶层 type 的形态到达模型，导致所有会话报错（2026-08-13 事故门禁）。

项目级安装把 11 个 `anchor-*` 技能装进 `<项目>/.dsh/skills/`（DSH 原生项目级根）——进入该项目工作区的会话加载，其他会话不加载，与 Reasonix 按项目部署一致。DSH 目前尚无项目级插件机制（上游建议：[deepseek-ai/deepseek-harness discussion #306](https://github.com/deepseek-ai/deepseek-harness/discussions/306)）；`anchorlaw_*` 工具由宿主级全局挂载提供。

维护入口：[`dsh/AGENTS.md`](dsh/AGENTS.md) — 单一事实源；正文改动走 `.reasonix/skills/`，`dsh/skills/` 只做 frontmatter 适配。

---

## 核心原理

传统开发把"写代码"和"写测试"分开。Vibe coding 让这种分离变得昂贵——AI 快速生成代码，但验证发生在事后、靠人工，并且反馈在迭代中丢失。

Anchorlaw 反转了这个关系：**测试是声明的一部分，不是附属品。** 一个函数没有 `@pt` 也没有 `@idk`，会在静态扫描时被标记——不是因为它是 buggy 的，而是因为它没有可验证的正确性证据。

当测试在运行时失败，失败被捕获为**噪声卡**——结构化的知识，随时间积累，并可以注入回 AI 的上下文中，影响未来的代码生成。

### "只有进攻，没有防御"

这个协议不禁止，它要求证明：

- 传统方式："你不能除以零。"（防御）
- Anchorlaw："证明你的除数不为零，或处理为零的情况。"（进攻）

唯一允许的"防御"是 `@idk`——一种打开战场、邀请实践检验的诚实声明。

---

## 项目结构

```
anchorlaw/
├── README.md                    # 英文顶层说明
├── README_zh.md                 # 中文顶层说明（你在这里）
├── spec/
│   └── protocol-v0.17.md       # 语言无关的协议规范（当前版）
├── python/
│   ├── anchorlaw-scanner/       # 独立扫描器（Level 1, 已验证）
│   └── anchorlaw/               # 完整协议（Level 2-4, 实验性）
├── typescript/
│   └── anchorlaw-scanner/       # TS/JS 扫描器（Level 1, 开发中）
└── dsh/
    ├── skills/                  # 11 个 DSH 格式 anchor-* 技能（派生自 .reasonix/skills/）
    ├── plugins/                 # anchorlaw-tools.js — 4 个模型工具
    ├── preset/                  # anchorlaw agent preset（Judge 驱动流水线）
    └── AGENTS.md                # DSH 宿主适配维护入口
```

---

## 参与贡献

本项目目前最需要的不是 PR 辩论，而是**实践数据**。

最有价值的贡献方式：

1. **跑扫描器**——在你的项目上跑，报告误报
2. **使用锚点系统**——在真实项目上用 2 周以上，告诉我们它帮助了还是阻碍了
3. **积累噪声卡**——我们需要有 30+ 张噪声卡的项目来测试 AI 上下文注入的效果

在 GitHub Discussions 开启讨论，或在 Issues 提交你的发现。

---

## 参考

- [协议规范 v0.17](spec/protocol-v0.17.md)
- 唯物实践论方法论——本协议的哲学基础

---

> "这个项目不承诺永恒的真理。它承诺一套在当前历史条件下锻造的最趁手的工具，并对更好的工具保持开放。它的最高承诺，是让使用者最终有能力质疑、改进、乃至超越它本身。"
>
> —— 第一律，反身性应用
