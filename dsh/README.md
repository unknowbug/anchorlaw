# Anchorlaw — DSH Host Adaptation (`dsh/`)

**Anchorlaw 协议（代码验证协议）的 DSH（DeepSeek Harness）宿主适配层。**

本子树位于规范仓库 `github.com/unknowbug/anchorlaw` 内，与协议核心（`spec/`、`python/`、`typescript/`）共存——**同一协议，单一仓库，宿主适配不分裂**。由 DSH agent「大肥鱼」维护。Reasonix 宿主格式已停止维护并归档（`archive/reasonix/`）。

## 这是什么

把 Anchorlaw 协议的四大能力搬进 DSH 并持续维护：

| 能力 | DSH 形态 |
|------|----------|
| 11 个协议技能（L0-L4 + 执行角色） | `skills/` → 安装到用户级全局根 `~/.dsh/skills`（rank 400，所有会话可见） |
| 防御性模式扫描器（P1-P6） | 模型工具 `anchorlaw_scan` / `anchorlaw_report` |
| 噪声卡 → AI 上下文注入 | 模型工具 `anchorlaw_ai_context` |
| Judge 驱动四段流水线（§15.4） | agent preset `anchorlaw`（人格 + subagent 隔离） |

## 快速开始

```powershell
# 安装：bundle 装进 profile 的 dsh.profile.bundles（preset 由此生效）+ 用户级技能 + 全局工具挂载
pwsh scripts/install.ps1

# 自检（工具链 / 技能 manifest / 自扫 / 安装产物 / 插件工具 schema / preset 行解析）
pwsh scripts/selfcheck.ps1
```

- **bundle（preset 载体）**：DSH ≥ 0.1.7 的 agent preset 是 bundle patch 里的一条 `@deepseek-ai/dsh-agent-preset` 声明行，不再是 `~/.dsh/.agent-presets/<id>/` 目录（旧目录**已无人读取**）。install.ps1 用 `dsh plugin --profile <p> add <本目录>` 把本子树作为 bundle 装进 profile，插件管理器自动把它写进 `dsh.profile.bundles`；`-Profile <name>` 可只装一个，默认自动检测 `profiles/` 下所有含 `package.json` 的 profile。
- **用户级技能**：11 个 `anchor-*` 技能装到 `~/.dsh/skills`（rank 400，所有会话可见）。**技能不内嵌进 bundle**——位置由安装者决定；若要项目级隔离，直接把技能放进 `<项目>/.dsh/skills/`（DSH 原生项目级根，rank 100），任何 preset 都会发现它，无需安装器。
- **全局工具挂载**：4 个 `anchorlaw_*` 工具以 `insert` 行写入每个 profile 的 `cordis.patch.yml`（DSH 唯一读取的用户补丁层，热重载），插件文件落 `<profile>/plugins/anchorlaw/`。挂载前先跑 `tests/check_plugin_schema.mjs` 校验工具 schema 必须是编译后 JSON Schema（2026-08-13 事故门禁：扁平 schema 会让所有会话报 `Invalid schema ... type: null`）。工具注册表是分层的，preset 行与本全局行不冲突；任何会话（任意工作目录、任意 preset）都能用这 4 个工具。
- **无项目级模式**：DSH 没有项目级插件/preset 机制，项目级只能给技能、给不了 preset 与工具。

## 目录结构

```
skills/                # 11 个技能事实源（唯一事实源，正文遵守协议 §14 契约）
plugins/               # 工具插件事实源（anchorlaw-tools.js）
package.json           # bundle 清单（dsh.bundle.patch + exports["./plugin"]）
cordis.patch.yml       # bundle patch：anchorlaw agent preset 声明
scripts/               # install.ps1（安装/同步，含全局工具挂载）、selfcheck.ps1（七项自检）
tests/                 # test_manifest.py（manifest 校验）+ check_plugin_schema.mjs（工具 schema 校验）+ audit_preset_rows.mjs（preset 行解析门禁）+ audit_prompt_variables.mjs（提示词变量门禁）
SYNC.md                # 与协议核心的同步溯源戳
demo/                  # 演示代码
AGENTS.md              # DSH 维护入口（agent 每会话加载）
```

## 维护约定

- **单一事实源**：协议核心只存仓库根；DSH 技能正文规范在 `skills/`（唯一事实源，协议 §14 是宿主无关技能规范）
- **只改事实源**（`skills/`、`plugins/`、`package.json`、`cordis.patch.yml`），然后跑 `scripts/install.ps1` 重装
- 安装产物（profile 的 `dsh.profile.bundles`、`~/.dsh/skills/anchor-*`、`<profile>/plugins/anchorlaw/`）禁止手改
- 改动后必须 `scripts/selfcheck.ps1` 全绿（含 manifest、工具 schema 与 preset 行解析校验）
- 提交纪律沿用仓库（author `unknowbug`、英文动词开头、push 前人类审查）

## 依赖

- Python 3.12+，`pip install anchorlaw-scanner anchorlaw`（本机已装 0.1.0）
