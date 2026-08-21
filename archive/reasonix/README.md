# Reasonix 版存档（Archive）

本目录是 Anchorlaw 协议的 **Reasonix 宿主版本存档**（最后维护状态：v0.18，2026-08-15）。

## 状态声明

**Anchorlaw 自 v0.18 起停止维护 Reasonix 宿主格式，仅维护 DSH 宿主适配**（见仓库根 README 与 `dsh/AGENTS.md`）。Reasonix 格式的技能/入口不再随主仓库更新。

## 如果你想基于 Reasonix 版本继续迭代

1. **Fork 本仓库**（`github.com/unknowbug/anchorlaw`）
2. 在 Fork 的仓库根运行恢复脚本：
   ```powershell
   pwsh archive/reasonix/restore-reasonix.ps1
   ```
3. 恢复后得到 Reasonix 工作副本：
   - `.reasonix/skills/` — 11 个 `anchor.*` 技能（Reasonix 格式）
   - 根 `AGENTS.md` — Reasonix 入口
   - `.reasonix/metadata/` — Reasonix 元数据
4. 从该状态自行迭代（本目录不再更新）

## 存档内容 vs 协议核心

| 内容 | 位置 | 说明 |
|------|------|------|
| Reasonix 技能 + 入口 + 元数据 | `archive/reasonix/` | **已归档**，随本目录留存 |
| 协议正文 `spec/protocol-v0.18.md` | 仓库根 `spec/` | **未归档**——语言无关协议核心，DSH 适配与 Reasonix 版共用，Fork 后直接可用 |
| Python/TS 实现 | 仓库根 `python/`、`typescript/` | **未归档**——协议实现，两版共用 |

## 迁移说明

- 原 `.reasonix/skills/`（11 个技能）→ `archive/reasonix/skills/`（git 历史保留）
- 原根 `AGENTS.md`（Reasonix 入口版）→ `archive/reasonix/AGENTS.md`
- 原 `.reasonix/*.json`（desktop-topic 元数据）→ `archive/reasonix/metadata/`
- 恢复脚本会把以上内容**反向恢复到仓库根**，还原成 Reasonix 工作副本
