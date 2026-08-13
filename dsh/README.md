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
# 1. 安装/同步到 DSH 运行时（preset + 用户级技能）
pwsh scripts/install.ps1

# 2. 自检（工具链 / 技能 manifest / 自扫 / 安装产物）
pwsh scripts/selfcheck.ps1
```

装完后新建会话时选择 **anchorlaw** preset，即可使用 4 个 `anchorlaw_*` 工具和 11 个 `anchor-*` 技能。

## 目录结构

```
skills/                # 11 个技能事实源（frontmatter 适配；正文派生自 ../.reasonix/skills/）
plugins/               # 工具插件事实源（anchorlaw-tools.js）
preset/                # agent preset 组合源（agent.cordis.yml + preset.yml）
scripts/               # install.ps1（安装/同步）、selfcheck.ps1（自检）
tests/                 # test_manifest.py（正文级一致性校验）
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
