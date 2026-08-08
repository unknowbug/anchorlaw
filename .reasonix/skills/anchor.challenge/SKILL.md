---
name: anchor.challenge
description: 规则挑战——scanner 疑似误报时按 §12 四步流程上报，FP 证据强制规则降级/删除，协议必须能被推翻
---

# anchor.challenge — 规则挑战流程

> Protocol: spec/protocol-v0.8.md §12 (Rule Challenge Process)
> Layer: L1 (Scanner)
> Execution: inline

## 触发场景

scanner 输出疑似误报（FP），或想质疑某条协议规则（第三律：协议必须能被推翻）。

## 四步流程（§12）

1. **Report（上报）** — 提交 issue：最小复现（代码片段 + scanner 输出）。
2. **Verify（验证）** — 维护者复现 FP；复现用例加入 scanner 测试套件，标记为已知-FP 排除，防止模式被盲目加回。
3. **Adjudicate（裁决）** — 规则三种出路：细化排除该例 / 降级 severity / 从目录删除；理由必须记录进协议 changelog。
4. **Evidence（证据）** — 无 FP 证据不能削弱规则；有确认 FP 的规则不能保持不变。

## 输出

挑战 issue（含最小复现）或裁决结论记录。

## 约束

- 「疑似」不构成依据——必须带最小复现代码。
- 挑战结果（成败）都要记录在案，供协议演进追溯。
