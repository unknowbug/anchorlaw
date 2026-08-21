# RESTORE — 从存档恢复 Reasonix 工作副本

> 适用对象：Fork 了 Anchorlaw 仓库、想基于 **Reasonix 版本**继续迭代的维护者。
> Anchorlaw 主仓库已停止维护 Reasonix 格式（仅维护 DSH），本脚本让你一键回到 Reasonix 工作副本。

## 前置

- 已 Fork `github.com/unknowbug/anchorlaw` 并克隆到本地
- 在**仓库根**执行（脚本内所有路径相对仓库根）

## 恢复步骤

```powershell
# 1. 运行恢复脚本（把 archive/reasonix 内容恢复到仓库根）
pwsh archive/reasonix/restore-reasonix.ps1

# 2. 验证恢复结果（应看到以下内容回到仓库根）
#    .reasonix/skills/anchor.*/SKILL.md   （11 个）
#    AGENTS.md                            （Reasonix 入口）
#    .reasonix/metadata/*.json
```

## 恢复后

- `.reasonix/skills/` 重新成为技能事实源，根 `AGENTS.md` 重新成为 Reasonix 入口
- 协议正文（`spec/`）、Python/TS 实现仍在仓库根，可直接使用
- **从此自行迭代**：本存档目录不再更新，你的迭代基于恢复时的状态进行

## 恢复脚本行为

`restore-reasonix.ps1` 执行：

1. `archive/reasonix/skills/` → 仓库根 `.reasonix/skills/`（若已存在同名内容先备份为 `.reasonix.bak/`）
2. `archive/reasonix/AGENTS.md` → 仓库根 `AGENTS.md`（若已存在先备份为 `AGENTS.md.bak`）
3. `archive/reasonix/metadata/` → 仓库根 `.reasonix/metadata/`

> 幂等：可重复运行；已存在的目标会被备份为 `.bak`，不会静默覆盖。
