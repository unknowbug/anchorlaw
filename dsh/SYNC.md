# SYNC.md — DSH 适配层与协议核心的同步溯源戳

> 本文件记录 `dsh/` 子树与协议核心（`.reasonix/skills/` 规范正文）的同步状态。
> 采用协议自身的 source-provenance 纪律（§5.5）：每一次同步都记录来源、时间与差异，可审计。

## 初始同步（2026-08-12）

- **来源**：`.reasonix/skills/anchor.*/SKILL.md`（11 个，协议参考实现）
- **动作**：正文 1:1 复制 → frontmatter 适配（`anchor.x` → `anchor-x` kebab-case 改名、新增 `whenToUse`、移除 Reasonix 专有 `kind`/`runAs` 字段）
- **正文漂移**：0（仅行尾符 CRLF→LF 归一化差异，已由 `tests/test_manifest.py` 以正文级比对守护）
- **适配映射**（frontmatter 变更汇总）：

| 技能 | frontmatter 变更 |
|------|------------------|
| 全部 11 个 | `name` 由 `anchor.X` 改为 `anchor-x`；新增 `whenToUse`（触发场景）；移除 `kind`/`runAs` |
| anchor-scan / anchor-degrade / anchor-scout / anchor-worker / anchor-judge | `whenToUse` 注明 DSH 中经 subagent 工具隔离执行（对应 §15.3 skill-execution coupling） |

## 同步规则（维护者必读）

1. **技能正文改动**：只允许发生在 `.reasonix/skills/`（规范正文）。改后更新本文件的差异记录，然后确认 `dsh/tests/test_manifest.py` 通过。
2. **frontmatter 适配改动**：直接改 `dsh/skills/<name>/SKILL.md`，并在此文件登记变更。
3. **协议语义更新**：先改 `../spec/protocol-v0.17.md`（§8 Maturity / §11 审计随行），再同步技能正文与 DSH 适配。

## 变更日志

| 日期 | 来源 commit | 内容 | 正文漂移 |
|------|-------------|------|----------|
| 2026-08-12 | （初始同步，工作区状态） | 11 技能 DSH 化移植 | 0 |
