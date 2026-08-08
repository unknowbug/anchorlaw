# Anchorlaw 项目 AGENTS.md（项目级常驻指令）

> Reasonix 在本仓库工作时自动加载本文件。本文件是**索引**——协议知识按需加载（协议 v0.8 §14 Anchor Skill Manifest + §15 Execution Topology），铁律正文在对应 skill 里，不在本文件常驻。

## 〇、开始工作前（每个 session 必做）

1. `git status` 确认工作区状态（远程 = `github.com/unknowbug/anchorlaw`）
2. 跑测试确认基线全绿：`python -m pytest --rootdir=python python/tests -q`（命令行被沙箱拦截时用包装脚本调 `pytest.main()`）
3. 若改动涉及协议文档：同步核对 [§8 Maturity](spec/protocol-v0.8.md#8-maturity) 与 [§11 全称声称审计表](spec/protocol-v0.8.md#11-universal-claim-audit-v04)，证据必须跟着走

## 一、项目定位（一句话）

**Anchorlaw 是语言无关的代码验证协议——唯物实践论三律的代码化：**
- **第一律（可检验）**：`@anchor.test` 把声称绑到可执行验证
- **第二律（可证伪）**：`@anchor.idk` 诚实声明边界 + staleness（90 天自动升级）
- **第三律（可挑战）**：协议 §12 规则挑战流程——FP 证据强制规则降级/删除

## 二、主工作流（收敛门模型，v0.8）

编程是**线性收敛**任务——主 Agent 全程持有上下文并亲自写，不拆 subagent（judge 审查除外）。

**推进段（自由编排，按下方 Skill 索引查表加载）**：理解需求 → 实现/重构 → 写 anchor 标注。

**收敛段（强制线性，不可跳过，v0.8 收敛门）**——任何任务收尾前 MUST 顺序通过：

1. **验证** — 跑测试 + `anchorlaw test`（`anchor.test`，inline）；CI 失败排查
2. **审查** — `anchor.judge`（独立视角防自欺；唯一 subagent 审查角色：主 Agent 写完 → judge 验证。subprocess 型动作 skill 如 `anchor.scan`/`anchor.degrade` 为发散型优化例外）
3. **提交** — 测试全绿 + changelog/§8/§11 同步（`anchor.maintain` 纪律）

**异常分支（不进主循环，按需触发）**：
- scanner 疑似误报 → `anchor.challenge`（§12 规则挑战）
- 运行时失败 → `anchor.noise`（噪声卡）
- 代码无法独立编译 → `anchor.degrade`（§9 降级验证）

## 三、Skill 触发索引（协议 v0.8 §14-§16，参考实现 `.reasonix/skills/`）

> 协议知识不常驻上下文——按场景调用对应 skill，正文按需加载：

| 场景 | 调用 skill | 层 | 执行 |
|------|-----------|-----|------|
| 写/审 anchor 前需要语义速查 | `anchor.concepts` | L0 | inline |
| 改完代码待提交前（静态审查） | `anchor.scan` | L1 | subprocess |
| scanner 疑似误报（挑战规则） | `anchor.challenge` | L1 | inline |
| 实现/重构公开函数后（写标注） | `anchor.write` | L2 | inline |
| 添加 anchor 后 / CI 失败（验证） | `anchor.test` | L2 | inline |
| 运行时失败 / 噪声卡积压 | `anchor.noise` | L3 | inline |
| 代码无法独立编译（降级） | `anchor.degrade` | L2 | subprocess |
| **修改协议/实现本身（本仓库）** | `anchor.maintain` | L4 | inline |

`subprocess` = 派隔离子进程执行（§15.3 skill-execution coupling，发散型任务可选），主会话只收最终答案 + 产物引用；`inline` = 主会话内执行（收敛型任务默认，编程主 Agent 亲自做）。审查角色见 `.reasonix/skills/anchor.judge/`。

铁律正文在 `anchor.maintain`（测试全绿、自指、文档纪律、§11 审计、提交纪律）；C++/source 细节在 `anchor.write`/`anchor.concepts`。

## 四、仓库结构速览

| 路径 | 内容 |
|------|------|
| `spec/protocol-v0.8.md` | **协议当前版**（v0.1/v0.3/v0.4/v0.5/v0.6/v0.7 留档历史，不改） |
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
