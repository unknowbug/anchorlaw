# AGENTS.md — Anchorlaw dsh/ 子树（DSH 宿主适配层，大肥鱼维护）

> 本目录（`dsh/`）是 **Anchorlaw 仓库的 DSH 宿主适配层**：协议核心（`spec/`、`python/`、`typescript/`）与 DSH 生态适配（DSH 技能格式、工具插件、agent preset、维护脚本）共存于同一规范仓库 `github.com/unknowbug/anchorlaw`。
> 维护者：大肥鱼（DSH agent）。每次会话开始必读本文件。

## 〇、开始工作前（每个 session 必做）

1. 确认仓库状态：本仓库根即协议事实源，本目录（`dsh/`）即 DSH 适配事实源——**单一仓库，无第二份协议副本**。
2. 跑自检确认基线全绿：`pwsh scripts/selfcheck.ps1`（工具链 / 技能 manifest / 自扫 / 安装产物 / 插件工具 schema / preset 行解析 / 提示词变量 七项）。
3. 若改动涉及协议语义：协议正文在上层 `../spec/protocol-v0.25.md`（§8 Maturity / §11 全称声称审计 / §14 Skill Manifest），证据必须跟着走；技能正文直接改本目录 `skills/`（DSH 技能唯一事实源，协议 §14 是宿主无关的技能规范）。

## 一、本目录定位（一句话）

**Anchorlaw 协议的 DSH（DeepSeek Harness）宿主适配层**——协议 §14 Skill Manifest 是宿主无关的技能规范；本目录持有 DSH 格式技能（kebab-case + whenToUse）、模型工具插件、agent preset 与维护脚本，`dsh/skills/` 是 DSH 技能的唯一事实源。

## 二、目录结构（事实源 vs 安装产物）

| 路径 | 内容 | 角色 |
|------|------|------|
| `skills/` | 11 个 anchor-* 技能（DSH 版 SKILL.md，**唯一事实源**，正文遵守协议 §14 契约） | **事实源**（改这里） |
| `plugins/anchorlaw-tools.js` | 4 个模型工具插件（scan/report/ai-context/status） | **事实源**（改这里） |
| `package.json` | **bundle 清单**——DSH ≥ 0.1.7 的 preset 载体：`dsh.bundle.patch` + `exports["./plugin"]` | **事实源**（改这里） |
| `cordis.patch.yml` | **bundle patch**：声明 `anchorlaw` agent preset（`@deepseek-ai/dsh-agent-preset` 行，内含全部 preset 子行） | **事实源**（改这里） |
| `scripts/install.ps1` | 安装/同步到 DSH 运行时（宿主级：bundle 装进 profile 的 `dsh.profile.bundles` + 用户技能 + **全局工具挂载**到 profiles/ 下所有 profile 的 `cordis.patch.yml`（自动检测；`-Profile <name>` 指定单个）。**无项目级模式**——DSH 没有项目级插件/preset 机制） | 维护工具 |
| `scripts/selfcheck.ps1` | 七项自检（含插件工具 schema 校验，2026-08-13 事故门禁；含 preset 行解析门禁，2026-09-09 上游改名事故门禁；第 4 项检 bundle 是否被 profile 选中，2026-09-23 事故门禁；第 7 项检提示词变量，2026-10-10 上游删除 `cwd` 事故门禁） | 维护工具 |
| `scripts/run_tests_sandbox.py` | 沙箱感知 pytest 包装——DSH Windows 沙箱封存 0o700 目录导致 pytest tmp 机制失效，本脚本改 0o755 后跑基线测试（`python -m pytest --rootdir=python python/tests -q` 的沙箱替代入口） | 维护工具 |
| `tests/check_plugin_schema.mjs` | 插件工具 schema 形态校验（编译后 JSON-Schema parameters） | 维护测试 |
| `tests/audit_preset_rows.mjs` | preset 行解析性门禁（fail-closed）——bundle patch 的 `insert[]`、group 子行、以及 **`config.plugins[]`（preset 的全部行）** 里每个 `name:` 都必须可解析，上游改名/移除即非零退出（2026-09-09 `dsh-workflow-worker-thread` → `dsh-workflow-ptc` 漂移；2026-09-23 preset 载体换成 bundle patch 后旧实现漏检 27/28 行） | 维护测试 |
| `tests/test_manifest.py` | 技能 manifest 校验（DSH 命名 + frontmatter 形态 + 技能集） | 维护测试 |
| `tests/audit_prompt_variables.mjs` | 提示词变量门禁（fail-closed）——preset 模板里每个 `{{变量}}` 必须是 harness **当前注册**的提示词变量（扫描生产代码里的 `systemPrompt.variable(...)`，跳过 tests，避免测试假变量污染白名单）。persona 模板是**渲染期严格解析**的，上游删变量即会话组装失败而**行解析门禁看不见**（2026-10-10 事故：DSH 0.2.x 删除 `cwd` → `unknown prompt variable "{{cwd}}" in section "deployment:persona-prefix"`） | 维护测试 |
| `SYNC.md` | 溯源戳（上次同步的上游 commit + 时间 + 差异） | 溯源记录 |
| `demo/` | 演示代码（防御模式 + 锚定函数） | 演示 |
| `PORT-ASSESSMENT.md` | 移植评估（历史存档） | 历史 |
| **安装产物（勿手改）** | | |
| `~/.dsh/profiles/<name>/package.json` 的 `dsh.profile.bundles` | 已选中的 bundle（preset 由此生效；旧 `~/.dsh/.agent-presets/` 目录已无人读取） | install.ps1 生成 |
| `~/.dsh/skills/anchor-*` | 用户级全局技能 | install.ps1 同步 |
| `~/.dsh/profiles/*/cordis.patch.yml` + `plugins/anchorlaw/` | 全局工具挂载（insert 行 + 插件文件） | install.ps1 生成 |

**同步纪律（核心铁律）**：所有修改只改本目录事实源，然后跑 `scripts/install.ps1` 重装——安装产物一律视为可再生，禁止手改。装完跑 `scripts/selfcheck.ps1` 验证。技能**正文**直接在本目录 `skills/` 修改；`tests/test_manifest.py` 守护 DSH manifest 合法性（kebab-case、frontmatter、技能集）。

## 三、维护铁律（对应上游 anchor.maintain，DSH 版）

1. **自检全绿**：任何改动必须 `scripts/selfcheck.ps1` 全绿。第 3 项自扫=第一律反身应用；第 5 项插件工具 schema 校验=挂载门禁（2026-08-13 事故：扁平 schema 让所有会话报 `Invalid schema ... type: null`；install.ps1 挂载前也先跑这道校验）；第 6 项 preset 行解析门禁=fail-closed（2026-09-09 事故：上游把 `dsh-workflow-worker-thread` 改名为 `dsh-workflow-ptc`，源码引用未跟，preset 挂载失败导致会话无法创建/恢复。2026-09-23 二次事故：上游把 preset 载体换成 bundle patch，门禁只审旧文件、漏检 preset 全部行，于是**自检全绿而 resume 报 `Unknown agent preset`**——同类漂移必须在自检被拦下，而不是等 resume 报错）。
2. **单一事实源**：协议核心只存仓库根一份；DSH 技能正文规范在 `dsh/skills/`（协议 §14 是宿主无关技能规范），由 test_manifest.py 守护 manifest 合法性。
3. **新能力必须配验证**：新增技能/工具要能通过自检或实测证明，否则标注 Unverified。
4. **命名纪律**：DSH 技能名必须 kebab-case（`anchor-judge` 而非 `anchor.judge`）；插件工具名 `anchorlaw_*`。
5. **插件持久化纪律**：动态插件（cordis_define 定义）只在当前进程存活——**持久能力必须落成 `plugins/` 文件 + preset 行**，禁止把维护性能力留在动态插件里。
6. **preset 纪律**：preset 是 **bundle 的一条 patch 行**（`dsh/cordis.patch.yml`），由 install.ps1 装进 profile 的 `dsh.profile.bundles`；旧目录形态 `~/.dsh/.agent-presets/` 已无人读取，禁止再往那里写。shipped preset（harness 安装目录）一律只读，改动只能以复制派生。
7. **提交纪律**：沿用仓库纪律（author 固定 `unknowbug`；commit message 英文、动词开头）；提交前自检全绿；push 由人类审查后执行。

## 四、与协议核心的分工（同一个仓库内）

- **仓库根（`../`）**：协议正文（`spec/protocol-v0.25.md`）、Python/TS 实现、Reasonix 版存档（`archive/reasonix/`）。
- **本目录（`dsh/`）**：DSH 生态适配层，**同时就是 Anchorlaw 的 DSH bundle 包**（`package.json` + `cordis.patch.yml` + `plugins/` + `skills/`），入口为本文件。
- **一致性机制**：`tests/test_manifest.py` 守护 `dsh/skills/` manifest 合法性；`SYNC.md` 记录同步溯源；协议语义更新先改仓库根，再同步本目录适配。

## 五、Judge 流水线（anchorlaw preset 的人格承诺）

使用 anchorlaw preset 的会话，agent 以 Judge 角色驱动四段流水线（输入契约 → 规范 → 计划 → 并行实施 → 交付），判据先行，3 轮硬停止，`confirmed` 只能由人类授予（§15.4/§16.1）。scout/worker/judge 经 subagent 工具隔离执行（§15.2/§15.3）。

## 六、会话工作目录说明

本仓库 `dsh/` 子树是 DSH 适配的唯一事实源。推荐新会话将工作目录指向本仓库根（加载根 AGENTS.md + 本文件）或本目录。

## 七、DSH 工具调用（模型工具优先，不裸跑 CLI）

4 个 `anchorlaw_*` 模型工具由全局挂载提供，**新会话**的工具列表可见（会话 composition 在创建时固定；工具没出现就重开会话）：

| 工具 | 底层 CLI | 用途 |
|------|----------|------|
| `anchorlaw_scan` | `anchorlaw-scanner check` | L1 防御模式扫描（P1-P6；`lang` 可选 cpp/go/java 注释式提取） |
| `anchorlaw_report` | `anchorlaw-scanner report` | 健康报告（扫描 + 噪声卡积压 + 诊断结论） |
| `anchorlaw_ai_context` | `anchorlaw ai-context` | 噪声卡 + 课程导出（LLM 上下文注入） |
| `anchorlaw_status` | — | 工具链版本 + 已发现 anchor-* 技能 |

**约定**：
- DSH 会话内做协议动作**优先调用这些工具**，不要裸跑 `python -m anchorlaw*` CLI——工具封装了 CLI、会话 cwd 解析与沙箱语义（工具描述即协议 §6/§3 的 DSH 形态）。
- 工具路径参数相对当前会话工作区（cwd），可传绝对路径。
- 维护 dsh/ 自身时同样优先用工具（扫描/报告本目录），与自检第 5 项互为印证。
