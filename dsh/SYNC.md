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
3. **协议语义更新**：先改 `../spec/protocol-v0.22.md`（§8 Maturity / §11 审计随行），再同步 DSH 适配。

## 变更日志

| 日期 | 来源 commit | 内容 | 正文漂移 |
|------|-------------|------|----------|
| 2026-08-12 | （初始同步，工作区状态；随 079c717 入库） | 11 技能 DSH 化移植 | 0 |
| 2026-08-13 | 3df7cc3 | anchor.maintain 正文移除易变测试计数（原"当前 78 个"，实测 98，改后不写死数字）；上游 `.reasonix/skills/` 修改 + DSH 镜像同步 | 0 |
| 2026-08-15 | — | Reasonix 宿主格式停止维护：`.reasonix/skills/` 归档至 `archive/reasonix/`（含恢复脚本）；`dsh/skills/` 转正为 DSH 技能唯一事实源；test_manifest.py 改为 manifest 自持校验 | —（镜像机制取消） |
| 2026-09-15 | harness `0d1f50007f`（dsh-v0.1.6-alpha.1）；漂移报告基线 `5dda764ed3`（dsh-0.1.5-alpha.1） | 上游插件包改名 `@deepseek-ai/dsh-workflow-worker-thread` → `@deepseek-ai/dsh-workflow-ptc`（旧包已无 package.json；preset 挂载失败 → 会话无法创建/恢复）：`preset/agent.cordis.yml` 的 `id` + `name` 同步改名，`config`（`provider: spawn`）与官方装配一致；新增 fail-closed 门禁 `tests/audit_preset_rows.mjs` 并接入 `selfcheck.ps1` 第 6 项，防同类上游漂移复发（来源：`.investigations/dsh-upstream-drift-20260909/报告.md`） | —（非技能正文；技能 11 个正文未变） |
| 2026-09-15 | harness `0d1f50007f`（`packages/preset/agent-presets/presets/standard/agent.cordis.yml`） | **能力面对齐上游 standard preset**：补 5 行——`command-goal`（`@deepseek-ai/dsh-command-goal`）、`present`（`@deepseek-ai/dsh-tool-present`）、`tool-ralph`（disabled）、`tool-subagent-codex`（disabled）、`tool-subagent-claude-code`（disabled）；三行可选外部 agent/workflow 按上游默认保持 `disabled: true`（启用需装对应 Bundle，host 可用性本身不授予工具）。逐 id 对齐后 ours 32 = official 31 + 本地 `anchorlaw-tools`，缺失 0。协议升版 v0.20 → v0.21（宿主适配能力变化，§16 范围；协议核心不变） | —（非技能正文） |
| 2026-09-15 | harness `0d1f50007f`（`packages/preset/agent-presets/src/{specifier,mount,discovery}.ts`） | **preset 行 specifier 解析语义对齐上游**：`classifyRowSpecifier()` 四分类——`cordis:` 内置 / 以 `.` 开头=preset 自带文件（相对 composition 目录）/ `file:` 与绝对路径=文件 URL（Windows 盘符路径必须）/ 其余=包名；包名解析基准由 preset 目录改为 **harness base**（已安装 harness 所在目录，checkout 下为 `apps/cli`）——上游理由：本地 preset 位于用户 home 下，Node 向上 node_modules 查找走不到 harness 依赖。`audit_preset_rows.mjs` 已镜像该语义（新增 `file:`/绝对路径分支 + 向上 node_modules 走查；`DSH_HARNESS_BASE` 可覆盖），并保留比上游更严的 exports 子路径校验（exports 外子路径挂载时会真的 import 失败）。**官方 `scanRoot()`（公开 API）体检结论：shipped 4/4 OK、我们的 anchorlaw OK**（基准须传 `apps/cli`；传 checkout 根会全量误报 BROKEN） | —（非技能正文；技能 11 个正文未变） |
| 2026-09-15 | 同上（RE 侧差异反馈，本轮采纳） | **harness base 自动探测 + 错基准守卫**（补上轮遗留的两点，与 RE 侧对齐）：① 基准不再写死 `<checkout>/apps/cli`——按 `--harness-base` / `DSH_HARNESS_BASE` / `<checkout>/apps/cli` / `<checkout>` / `<checkout>/packages/bundle/base` 顺序，取第一个能解析探针包 `@deepseek-ai/dsh-persona` 的候选；② 全部候选都失败 → **SKIP（exit 2）+ tried 清单 + 指定方式提示**，而非把 BAD 刷满屏。另修：`--harness-base` 的值不再泄漏进 positional 参数（否则被当成 composition 文件）。实测：正常 0 退出／错基准但有可用回退→自动恢复 0 退出／全候选失败→SKIP 2／注入旧包名→BAD 1（fail-closed 不回退）；selfcheck 6/6、基线 102 绿 | —（非技能正文） |
| 2026-09-15 | 协议 v0.21 → v0.22（CoreSwap 论文透镜报告 b3 + synthesis，`.investigations/paper-2608-25512-*`） | **协议吸收五条条款**（§9.8 验证的 temporality / 判据前置集 / §9.7.1 等价档位 / §15.4 PI-1 与 PI-2 / §14.7 引用完整性），触发证据全部来自 CoreSwap 一手事故（#156/#160/#161/#162 + M11/M16 + 三起日志灭失）；§8 Maturity 与 §11 audit 各增对应行（多数如实标 `scoped`——条款先立，下游才有唯一权威目标可对齐、可证伪）。**技能正文落点**：`anchor-judge` 审查清单 +4 项（8-11）、`anchor-test` 运行前置（副作用与逆）+ 判据前置核对、`anchor-write` 可比性档位/`S`/无效声明/逆不塞 source、`anchor-degrade` 逆登记 + 前置集核对。版本引用同步 30 文件（含 archive/reasonix 的版本行，正文保持冻结）；`spec/protocol-v0.21.md` 作为历史留档不改 | 技能 4 个正文有实质改动（其余 7 个仅版本行） |
