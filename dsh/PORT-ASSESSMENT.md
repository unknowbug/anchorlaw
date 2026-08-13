# Anchorlaw → DSH 移植评估与路线图

> 评估日期：2026-08-12 · 评估人：DSH Agent（大肥鱼会话）
> 源项目：`E:\PYTHON\Anchorlaw`（Anchorlaw 协议 v0.17，vibe coding 代码验证协议）
> 结论：**可移植性高**——11/11 技能直接落地，扫描器已包装为可用工具，完整流水线可通过 agent preset 打包。

---

## 一、Anchorlaw 资产清单（要搬什么）

| 资产 | 位置 | 形态 |
|------|------|------|
| 协议规范 v0.17 | `spec/protocol-v0.17.md`（~120KB） | 语言无关协议文本（§1-§16） |
| 11 个协议技能 | `.reasonix/skills/anchor.*/SKILL.md` | 分层动作技能（L0-L4）+ 执行角色（scout/worker/judge） |
| 扫描器 | `python/anchorlaw-scanner`（已 pip 安装 0.1.0） | Python CLI：`check`（P1-P6 防御模式 / C++ 标注提取）、`report` |
| 锚点系统 | `python/anchorlaw`（已 pip 安装 0.1.0） | `@anchor.test`/`@anchor.idk` 装饰器 + `test` 命令 |
| 噪声卡 | `python/anchorlaw` noise 模块 | `.anchorlaw/noise_cards.json` + CLI（list/search/resolve） |
| AI 上下文导出 | `anchorlaw ai-context` | 噪声卡 → LLM 注入文本（§4） |
| Judge 流水线 | 协议 §15/§16 + `anchor.judge` 等角色技能 | 输入契约 → 规范 → 计划 → 并行实施 → 交付（人授 confirmed） |

## 二、DSH 侧映射（搬到哪里）

| Anchorlaw 资产 | DSH 机制 | 落地位置 | 状态 |
|----------------|----------|----------|------|
| 11 个 SKILL.md | **DSH 技能**（`SKILL.md` + frontmatter，kebab-case 命名） | `C:\Users\NDark\.dsh\skills\anchor-*`（用户级根，全局可见） | ✅ 已验证 |
| `anchorlaw-scanner check/report` | **Host 插件工具**（`harness.defineTool` + `subprocess.spawn` 跑 Python CLI） | 动态插件 `ancl-1`（4 个工具） | ✅ 已验证 |
| `anchorlaw ai-context`（噪声卡 → 上下文） | Host 插件工具 | `ancl-1` 内 `anchorlaw_ai_context` | ✅ 已验证 |
| 环境就绪检查 | Host 插件工具（版本 + 技能发现） | `ancl-1` 内 `anchorlaw_status` | ✅ 已验证 |
| Judge 流水线（§15.4） | **agent preset**（`~/.dsh/.agent-presets/anchorlaw/`）+ subagent 工具（scout/worker/judge 隔离执行）+ goal 机制 | 待创建（见路线图 B） | ⏳ 待做 |
| §16 宿主接入（confirm hook 人类授 confirmed） | DSH 审批/确认机制（approval / ask_user_question / 用户确认） | preset 内工作流约定 | ⏳ 待做 |

## 三、已验证的实测结果

1. **技能移植**：11 个 `anchor-*` 技能安装到用户级根后，DSH 注册表**实时发现**（session 技能目录当场刷新），插件内 `skills.list({ cwd, scope })` 可完整列出——两种路径都通。
2. **扫描器工具**：`anchorlaw_scan demo` 正确输出 11 条 findings（ERR=1 WARN=8 INFO=2），exit code 1（有 ERR 模式）语义保留。
3. **报告工具**：`anchorlaw_report demo` 输出健康报告（含模式分布 + 诊断结论）。
4. **噪声闭环**：`anchorlaw init` → `create_noise_card` → `anchorlaw_ai_context` 全链路可用。
5. **skill 语义完整性**：`anchor-law` 系列保持协议原文正文（L0-L4 分层、触发点 MUST、§12 挑战、§15.4 门禁），仅改 frontmatter。

## 四、移植必须做的适配（坑）

1. **命名冲突**：DSH 技能名必须是 kebab-case（`/^[a-z0-9]+(?:-[a-z0-9]+)*$/`），`anchor.judge` 带点命名**不合法** → 改名 `anchor-judge` 等（frontmatter 与目录名同步）。
2. **`runAs: subagent` 语义丢失**：Reasonix 的 frontmatter 字段 DSH 忽略 → 通过 `whenToUse`/正文保留「subprocess 隔离执行」提示；实际隔离由 DSH subagent 工具实现（DSH 原生就有 subagent/subagent_fork 工具，天然对应 §15.3 skill-execution coupling）。
3. **Python 运行时依赖**：扫描器是 Python CLI，插件通过 `subprocess` 服务 spawn（本机 python 3.12 + 两包已装，无需额外安装；换机器需 `pip install anchorlaw-scanner anchorlaw`）。
4. **路径基准**：工具以**会话 cwd**（`exec.agent.session.header.cwd`）为基准解析路径，不是 harness 进程 cwd（实测 `sandboxPolicy.workspaceRoot` 指向部署目录，不能用作会话工作区）。
5. **噪声卡存储位置**：`.anchorlaw/` 在项目根（cwd 相关），跨项目不共享——如需全局噪声库可升级为 Host 服务（路线图 C）。
6. **§16 宿主接入契约**：Anchorlaw 的 confirm hook（人类授 confirmed）在 DSH 用审批/确认流程承接；judge 只出意见不改 status 的纪律保留在技能正文里，靠 agent 遵守。

## 五、路线图（三档，按需推进）

### A. 现状档（已完成 ✅）
用户级 11 技能 + 动态插件 4 工具。任何项目会话可见技能、可用扫描/报告/上下文导出工具。

### B. 完整档：agent preset「anchorlaw」（推荐下一步）
`~/.dsh/.agent-presets/anchorlaw/`（从 `standard` copy 派生）：
- 挂载 `dsh-tool-anchorlaw` 工具行（把本插件工具固化为 preset 行，重启后仍在）
- preset 自带 `skills/` 目录（11 个 anchor-* 技能随 preset 走，或继续用用户级根）
- persona/提示词：Judge 驱动四段流水线工作流说明（§15.4 门禁：判据先行、3 轮硬停止、人授 confirmed）
- 派 scout/worker/judge 走 DSH subagent 工具（隔离执行，§15.3 对应）
- 验收：`standingKeyFor('anchorlaw')` mount-validate 通过后，新开会话实测

### C. 深度档：Host 侧服务（跨会话能力）
把 anchorlaw 上升为 Host 插件（进宿主 `cordis.yml`，非会话级）：
- `anchorlaw` 服务：噪声卡全局存储（storageDomain）、扫描结果持久化
- §16 宿主接入：confirm/candidate 状态机与 DSH approval 打通
- 需要改部署配置，影响所有会话——建议在 B 档跑通后再做

## 六、交付物位置

- 技能移植版：`E:\PYTHON\Anchorlaw\dsh\skills\`（11 个 `SKILL.md`，可随时重装到任意根）
- 已安装：`C:\Users\NDark\.dsh\skills\anchor-*`
- 演示代码：`E:\PYTHON\Anchorlaw\dsh\demo\`（demo_defensive.py / demo_anchored.py）
- 插件：动态插件 `ancl-1`（当前运行中，`cordis_stop ancl-1` 停用、`cordis_undefine ancl-1` 移除）
