# Anchorlaw — DSH Host Adaptation (`dsh/`)

**Anchorlaw 协议（代码验证协议）的 DSH（DeepSeek Harness）宿主适配层。**

本子树位于规范仓库 `github.com/unknowbug/anchorlaw` 内，与协议核心（`spec/`、`python/`、`typescript/`、`.reasonix/skills/`）共存——**同一协议，单一仓库，宿主适配不分裂**。由 DSH agent「大肥鱼」维护。

## 这是什么

把 Anchorlaw 协议的四大能力搬进 DSH 并持续维护：

| 能力 | DSH 形态 |
|------|----------|
| 11 个协议技能（L0-L4 + 执行角色） | `skills/` → 安装到 `~/.dsh/skills` 与 preset 内嵌 |
| 防御性模式扫描器（P1-P6） | 模型工具 `anchorlaw_scan` / `anchorlaw_report` |
| 噪声卡 → AI 上下文注入 | 模型工具 `anchorlaw_ai_context` |
| Judge 驱动四段流水线（§15.4） | agent preset `anchorlaw`（人格 + subagent 隔离） |

## 快速开始

```powershell
# 模式 A：宿主级（默认）——preset + 用户级技能；任何项目会话可选 anchorlaw preset
pwsh scripts/install.ps1

# 模式 B：项目级（Reasonix 式）——技能装进项目，进入该项目工作区才加载、离开即无
pwsh scripts/install.ps1 -Project E:\path\to\project

# 自检（工具链 / 技能 manifest / 自扫 / 安装产物 / 插件工具 schema）
pwsh scripts/selfcheck.ps1
```

- **宿主级（默认）**：11 个 `anchor-*` 技能随用户级技能安装（所有会话可见）；4 个 `anchorlaw_*` 工具**全局挂载**——install.ps1 把插件行以 `insert` 形态写入活动 profile 的 `cordis.patch.yml`（`profiles/<profile>/`，DSH 唯一读取的用户补丁层，热重载），插件文件落 `<profile>/plugins/anchorlaw/`。挂载前先跑 `tests/check_plugin_schema.mjs` 校验工具 schema 必须是编译后 JSON Schema（2026-08-13 事故门禁：扁平 schema 会让所有会话报 `Invalid schema ... type: null`）。任何会话（任意工作目录、任意 preset）都能用这 4 个工具。
- **项目级（`-Project`）**：11 个 `anchor-*` 技能装到 `<项目>/.dsh/skills/`（DSH 原生项目级根，rank 100）——进入该项目工作区的会话加载、离开不加载，与 Reasonix 按项目部署一致。插件文件同步落到 `<项目>/.dsh/plugins/` 备用；DSH 目前尚无项目级插件加载机制（建议已提交上游：deepseek-ai/deepseek-harness discussion #306），`anchorlaw_*` 工具由宿主级全局挂载提供。

## 目录结构

```
skills/                # 11 个技能事实源（frontmatter 适配；正文派生自 ../.reasonix/skills/）
plugins/               # 工具插件事实源（anchorlaw-tools.js）
preset/                # agent preset 组合源（agent.cordis.yml + preset.yml）
scripts/               # install.ps1（安装/同步，含全局工具挂载）、selfcheck.ps1（五项自检）
tests/                 # test_manifest.py（正文级一致性校验）+ check_plugin_schema.mjs（工具 schema 校验）
SYNC.md                # 与协议核心的同步溯源戳
demo/                  # 演示代码
AGENTS.md              # DSH 维护入口（agent 每会话加载）
```

## 维护约定

- **单一事实源**：协议核心只存仓库根；技能正文规范份在 `../.reasonix/skills/`，本目录只允许 frontmatter 适配
- **只改事实源**（`skills/`、`plugins/`、`preset/`），然后跑 `scripts/install.ps1` 重装
- 安装产物（`~/.dsh/.agent-presets/anchorlaw/`、`~/.dsh/skills/anchor-*`）禁止手改
- 改动后必须 `scripts/selfcheck.ps1` 全绿（含正文级一致性校验）
- 提交纪律沿用仓库（author `unknowbug`、英文动词开头、push 前人类审查）

## 依赖

- Python 3.12+，`pip install anchorlaw-scanner anchorlaw`（本机已装 0.1.0）
