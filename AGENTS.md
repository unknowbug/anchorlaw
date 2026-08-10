# Anchorlaw 项目 AGENTS.md（项目级常驻指令）

> Reasonix 在本仓库工作时自动加载本文件。本文件是**索引**——协议知识按需加载（协议 v0.10 §14 Anchor Skill Manifest + §15 Execution Topology），铁律正文在对应 skill 里，不在本文件常驻。

## 〇、开始工作前（每个 session 必做）

1. `git status` 确认工作区状态（远程 = `github.com/unknowbug/anchorlaw`）
2. 跑测试确认基线全绿：`python -m pytest --rootdir=python python/tests -q`（命令行被沙箱拦截时用包装脚本调 `pytest.main()`）
3. 若改动涉及协议文档：同步核对 [§8 Maturity](spec/protocol-v0.10.md#8-maturity) 与 [§11 全称声称审计表](spec/protocol-v0.10.md#11-universal-claim-audit-v04)，证据必须跟着走

## 一、项目定位（一句话）

**Anchorlaw 是语言无关的代码验证协议——唯物实践论三律的代码化：**
- **第一律（可检验）**：`@anchor.test` 把声称绑到可执行验证
- **第二律（可证伪）**：`@anchor.idk` 诚实声明边界 + staleness（90 天自动升级）
- **第三律（可挑战）**：协议 §12 规则挑战流程——FP 证据强制规则降级/删除

## 二、主工作流（Judge 驱动流水线，v0.10）

编程是**构建型任务**（不是逆向的探索型）——由 **Judge 驱动**：主会话扮演 Judge 角色持有验收判据，派 Scout 侦察、派 Worker 实施，每段以「Judge 点头」收敛。权威正文在 [协议 §15](spec/protocol-v0.10.md#15-agent-execution-topology-v06)（六段流水线 + 角色定义），本文件只索引不复制。

**六段流水线（每段以 Judge 点头终止）**：
1. **需求发掘** — Judge 派 `anchor.scout` 分析需求，判断清晰性/可实现性，不清晰继续派，直到需求文档完整
2. **人类确认门** — Judge 将完整需求文档 + 验收判据提交人类，**人类确认后才可实施**（§16.1 confirm hook）
3. **实施规范** — Judge 派 Scout 起草变量名/模块化/框架边界 → Judge 审过才进规划
4. **实施计划** — Judge 基于规范划模块
5. **并行实施** — 多 `anchor.worker` 按模块并行写码 → 每模块 Judge 审查，点头并入 / 打回修改
6. **交付** — Judge 总审 + 隔离 judge 独立验收（`anchor.judge`）→ 人类授予 `confirmed`

**验收判据先行（v0.10）**：判据（声称 + `@anchor.test` 验证载体 + `@anchor.idk` 边界）在需求阶段由 Judge 确定，随需求文档提交人类确认；实现朝判据收敛，review 意见对照判据。权威正文 [协议 §15.4](spec/protocol-v0.10.md#154-consistency-contract)。

**judge 触发点与验证终止门禁（v0.10）**——只索引不复制：
- Judge 六段触发点（需求确认 / 人类确认门 / 规范审查 / 计划批准 / 模块并入 / 交付验收）+ 意见分级 → 执行清单见 `anchor.judge` skill
- 终止门禁（外部测试集 / 三层意见分级 / **Judge 点头终态**取代 3 轮上限 / §12 通道）→ 协议 §15.4；AGENTS 不复制正文——镜像不同步正是 review 循环的根因
- **关键节点隔离验收**：模块并入前 + 交付前 MUST 派隔离 judge subprocess（自评≠审查）

**异常分支（不进主循环，按需触发）**：
- scanner 疑似误报 → `anchor.challenge`（§12 规则挑战）
- 运行时失败 → `anchor.noise`（噪声卡）
- 代码无法独立编译 → `anchor.degrade`（§9 降级验证）

## 三、Skill 触发索引（协议 v0.10 §14-§16，参考实现 `.reasonix/skills/`）

> 协议知识不常驻上下文——按场景调用对应 skill，正文按需加载：

| 场景 | 调用 skill | 层 | 执行 |
|------|-----------|-----|------|
| 写/审 anchor 前需要语义速查 | `anchor.concepts` | L0 | inline |
| 模块并入审查前（静态审查，stage 5） | `anchor.scan` | L1 | subprocess |
| scanner 疑似误报（挑战规则） | `anchor.challenge` | L1 | inline |
| 实现/重构公开函数后（写标注） | `anchor.write` | L2 | inline |
| 添加 anchor 后 / CI 失败（验证） | `anchor.test` | L2 | inline |
| 运行时失败 / 噪声卡积压 | `anchor.noise` | L3 | inline |
| 代码无法独立编译（降级） | `anchor.degrade` | L2 | subprocess |
| 需求分析 / 规范起草（流水线 1/3 段） | `anchor.scout` | 角色 | subprocess |
| 模块实施（流水线 5 段，Worker） | `anchor.worker` | 角色 | subprocess |
| 审查角色（六段触发点 + 隔离验收） | `anchor.judge` | 角色 | subprocess |
| **修改协议/实现本身（本仓库）** | `anchor.maintain` | L4 | inline |

`subprocess` = 派隔离子进程执行（§15.3 skill-execution coupling）：Scout/Worker 是流水线角色的执行模式（v0.10），主会话只收最终答案 + 产物引用；`inline` = 主会话内执行（轻量收敛动作：语义速查/写标注/验证/维护）。审查角色见 `.reasonix/skills/anchor.judge/`。

铁律正文在 `anchor.maintain`（测试全绿、自指、文档纪律、§11 审计、提交纪律）；C++/source 细节在 `anchor.write`/`anchor.concepts`。

## 四、仓库结构速览

| 路径 | 内容 |
|------|------|
| `spec/protocol-v0.10.md` | **协议当前版**（v0.1-v0.9 留档历史，不改） |
| `python/anchorlaw/` | Python 实现（anchors/noise/cli） |
| `python/anchorlaw-scanner/` | 静态扫描器（P1-P6 + severity layering + cpp.py） |
| `python/tests/` | pytest（anchors/scanner/noise/cpp/skills） |
| `typescript/anchorlaw-scanner/` | TS 版 scanner（JSDoc 注释式 anchor） |
| `.reasonix/skills/anchor.*/` | Skill 参考实现（§14 manifest 一致性由 test_skills.py 守护） |

## 五、通用协议性铁律（最高优先级，细节见 `anchor.maintain`）

> **Anchorlaw 是通用协议，禁止过度 Python 化导致别的语言引用困难。**

anchor 抽象 = 声明位置 + 验证载体（协议 §13），Python 装饰器 / TS JSDoc / C++ 行注释三者等价；跨语言新特性**先在协议里定义语言无关语义，再逐语言实现**；标注术语统一 `@anchor.test` / `@anchor.idk`（`pt`/`idk` 只是 import 别名）。

## 六、全局铁律（来自 Memory）

- **崩溃日志铁律**：任何交付的程序/原生库必须带全局崩溃捕获（异常+调用栈+写 crash 文件+不吞异常）
- **知识库记录**：重要结论带「猜测→验证→排除→发现」完整链条，被排除的假说也记录（标注 ❌）
