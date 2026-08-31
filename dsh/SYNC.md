# SYNC.md — DSH 适配层与协议核心的同步溯源戳

> 本文件记录 `dsh/` 子树与协议核心的同步状态（初始来源：`.reasonix/skills/` 规范正文，已于 2026-08-15 归档；此后 `dsh/skills/` 为 DSH 技能唯一事实源）。
> 采用协议自身的 source-provenance 纪律（§5.5）：每一次同步都记录来源、时间与差异，可审计。

## 初始同步（2026-08-12）

- **来源**：`.reasonix/skills/anchor.*/SKILL.md`（11 个，协议参考实现）；同步内容随 commit `079c717`（2026-08-13 子树落地）入库
- **动作**：正文 1:1 复制 → frontmatter 适配（`anchor.x` → `anchor-x` kebab-case 改名、新增 `whenToUse`、移除 Reasonix 专有 `kind`/`runAs` 字段）
- **正文漂移**：0（仅行尾符 CRLF→LF 归一化差异，已由 `tests/test_manifest.py` 以正文级比对守护）
- **适配映射**（frontmatter 变更汇总）：

| 技能 | frontmatter 变更 |
|------|------------------|
| 全部 11 个 | `name` 由 `anchor.X` 改为 `anchor-x`；新增 `whenToUse`（触发场景）；移除 `kind`/`runAs` |
| anchor-scan / anchor-degrade / anchor-scout / anchor-worker / anchor-judge | `whenToUse` 注明 DSH 中经 subagent 工具隔离执行（对应 §15.3 skill-execution coupling） |

## 同步规则（维护者必读）

1. **技能正文改动**：直接发生在 `dsh/skills/`（DSH 技能唯一事实源；Reasonix 镜像已于 2026-08-15 归档至 `archive/reasonix/`）。改后更新本文件的差异记录，然后确认 `dsh/tests/test_manifest.py` 通过。
2. **frontmatter 改动**：直接改 `dsh/skills/<name>/SKILL.md`，并在此文件登记变更。
3. **协议语义更新**：先改 `../spec/protocol-v0.20.md`（§8 Maturity / §11 审计随行），再同步 DSH 适配。

## 变更日志

| 日期 | 来源 commit | 内容 | 正文漂移 |
|------|-------------|------|----------|
| 2026-08-12 | （初始同步，工作区状态；随 079c717 入库） | 11 技能 DSH 化移植 | 0 |
| 2026-08-13 | 3df7cc3 | anchor.maintain 正文移除易变测试计数（原"当前 78 个"，实测 98，改后不写死数字）；上游 `.reasonix/skills/` 修改 + DSH 镜像同步 | 0 |
| 2026-08-15 | — | Reasonix 宿主格式停止维护：`.reasonix/skills/` 归档至 `archive/reasonix/`（含恢复脚本）；`dsh/skills/` 转正为 DSH 技能唯一事实源；test_manifest.py 改为 manifest 自持校验 | —（镜像机制取消） |
