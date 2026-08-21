# Anchorlaw 项目 AGENTS.md（项目级常驻指令）

> 本文件是**索引**——协议知识按需加载（协议 v0.18 §14 Anchor Skill Manifest + §15 Execution Topology），铁律正文在对应 skill 里，不在本文件常驻。
> **宿主说明**：DSH（DeepSeek Harness）适配层入口见 `dsh/AGENTS.md`（当前维护）；Reasonix 宿主格式自 v0.18 起停止维护并归档（`archive/reasonix/`，Fork 可恢复自行迭代）。

## 〇、开始工作前（每个 session 必做）

1. `git status` 确认工作区状态（远程 = `github.com/unknowbug/anchorlaw`）
2. 跑测试确认基线全绿：`python -m pytest --rootdir=python python/tests -q`（命令行被沙箱拦截时改用 DSH 沙箱感知包装：`python dsh/scripts/run_tests_sandbox.py --rootdir=python python/tests -q --basetemp=<非点前缀路径>`——DSH Windows 沙箱封存 0o700 目录导致 pytest tmp 机制失效，该脚本改 0o755 后跑基线测试；basetemp 用非点前缀目录避免 scanner 跳过隐藏目录）
3. 若改动涉及协议文档：同步核对 [§8 Maturity](spec/protocol-v0.18.md#8-maturity) 与 [§11 全称声称审计表](spec/protocol-v0.18.md#11-universal-claim-audit-v04)，证据必须跟着走

## 一、项目定位（一句话）

**Anchorlaw 是语言无关的代码验证协议——唯物实践论三律的代码化：**
- **第一律（可检验）**：`@anchor.test` 把声称绑到可执行验证
- **第二律（可证伪）**：`@anchor.idk` 诚实声明边界 + staleness（90 天自动升级）
- **第三律（可挑战）**：协议 §12 规则挑战流程——FP 证据强制规则降级/删除

## 二、主工作流（Judge 驱动流水线，v0.11）

编程是**构建型任务**（域内：输入契约已确认；探索型任务如 RE 在域外，见协议 §15.1/§16.1 input-contract confirmation criterion）——由 **Judge 驱动**：主会话扮演 Judge 角色持有验收判据，派 Scout 起草规范、派 Worker 实施，每段以「Judge 点头」收敛。**需求发掘不在本协议内**——它属于独立的需求协议（Scout 驱动 + 人机对话），其产出（已确认需求文档 + 技术约束规范；架构设计归 stage-1 产出）作为本流水线的**输入契约**。权威正文在 [协议 §15](spec/protocol-v0.18.md#15-agent-execution-topology-v06)（输入契约 + 四段流水线 + 角色定义），本文件只索引不复制。

**输入契约 + 四段流水线（每段以 Judge 点头终止）**：
0. **输入契约** — 已确认需求文档 + 技术约束规范由外部需求协议交接（主机交付即实施授权，§16.1）；Judge 从输入推导验收判据，无输入不得开工
1. **实施规范** — Judge 派 scout 起草变量名/模块化/框架边界 → Judge 审过才进规划
2. **实施计划** — Judge 基于规范划模块
3. **并行实施** — 多 worker 按模块并行写码 → 每模块 Judge 审查，点头并入 / 打回修改
4. **交付** — Judge 总审 + 隔离 judge 独立验收 → 人类授予 `confirmed`

**验收判据先行（v0.11；v0.14 输入契约分层）**：判据（声称 + `@anchor.test` 验证载体 + `@anchor.idk` 边界）由 Judge 从输入契约（外部需求 + 技术约束规范；架构设计属 stage-1 产出）推导，实施前确定；实现朝判据收敛，review 意见对照判据。权威正文 [协议 §15.4](spec/protocol-v0.18.md#154-consistency-contract)。

**judge 触发点与验证终止门禁（v0.12；v0.15 修订）**——只索引不复制：
- Judge 五触发点（输入契约接受 / 规范审查 / 计划批准 / 模块并入 / 交付验收）+ 意见分级 → 执行清单见对应 judge skill
- 终止门禁（外部测试集 / 三层意见分级 / **判据满足即完成 + 同一判据 3 轮不收敛 → 流程硬停止 + Judge 提交 Review 情况与问题详细报告交人类判定** / §12 通道）→ 协议 §15.4；AGENTS 不复制正文——镜像不同步正是 review 循环的根因
- **关键节点隔离验收**：模块并入前 + 交付前 MUST 派隔离 judge subprocess（自评≠审查）

**异常分支（不进主循环，按需触发）**：
- scanner 疑似误报 → challenge（§12 规则挑战）
- 运行时失败 → noise（噪声卡）
- 代码无法独立编译 → degrade（§9 降级验证）

## 三、技能与宿主入口

- **DSH 宿主（当前维护）**：11 个 `anchor-*` 技能（DSH 格式，`dsh/skills/` 为唯一事实源）+ 4 个 `anchorlaw_*` 模型工具 + anchorlaw agent preset。**入口：`dsh/AGENTS.md`**（含技能触发索引、工具调用约定、维护铁律）。
- **Reasonix 宿主（已停止维护，v0.18 起归档）**：原 `.reasonix/skills/`（11 个 `anchor.*` 技能）与 Reasonix 入口已移入 `archive/reasonix/`。需要 Reasonix 版的可 **Fork 本仓库**后运行 `archive/reasonix/restore-reasonix.ps1` 恢复自行迭代（见 `archive/reasonix/RESTORE.md`）。
- 协议正文 §14 Skill Manifest 是**宿主无关**的技能规范；各宿主按自己的技能格式实现，正文不改。

## 四、仓库结构速览

| 路径 | 内容 |
|------|------|
| `spec/protocol-v0.18.md` | **协议当前版**（v0.1-v0.16 留档历史，不改） |
| `python/anchorlaw/` | Python 实现（anchors/noise/cli） |
| `python/anchorlaw-scanner/` | 静态扫描器（P1-P6 + severity layering + cpp.py） |
| `python/tests/` | pytest（anchors/scanner/noise/cpp/skills） |
| `typescript/anchorlaw-scanner/` | TS 版 scanner（JSDoc 注释式 anchor） |
| `dsh/` | **DSH 宿主适配层**（技能/工具/preset/脚本），入口 `dsh/AGENTS.md` |
| `archive/reasonix/` | Reasonix 版存档（已停止维护；Fork 恢复指引见 `archive/reasonix/RESTORE.md`） |

## 五、通用协议性铁律（最高优先级，细节见 `anchor.maintain`）

> **Anchorlaw 是通用协议，禁止过度 Python 化导致别的语言引用困难。**

anchor 抽象 = 声明位置 + 验证载体（协议 §13），Python 装饰器 / TS JSDoc / C++ 行注释三者等价；跨语言新特性**先在协议里定义语言无关语义，再逐语言实现**；标注术语统一 `@anchor.test` / `@anchor.idk`（`pt`/`idk` 只是 import 别名）。

## 六、全局铁律（来自 Memory）

- **崩溃日志铁律**：任何交付的程序/原生库必须带全局崩溃捕获（异常+调用栈+写 crash 文件+不吞异常）
- **知识库记录**：重要结论带「猜测→验证→排除→发现」完整链条，被排除的假说也记录（标注 ❌）

## 七、宿主适配层（dsh/ 子树）

本仓库托管 DSH（DeepSeek Harness）宿主适配层：`dsh/` 子树（DSH 技能格式、anchorlaw 工具插件、agent preset、维护脚本与 SYNC.md 溯源）。**DSH 技能以 `dsh/skills/` 为唯一事实源**（Reasonix 镜像已随 `.reasonix/` 归档移除）。协议核心（spec/python/typescript）仍以仓库根为单一事实源；`dsh/` 维护入口见 `dsh/AGENTS.md`。
