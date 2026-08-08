---
name: anchor.maintain
description: 维护 Anchorlaw 协议本身——测试全绿铁律、self-scan、协议文档纪律（changelog/maturity/§11 审计）、提交纪律
---

# anchor.maintain — 协议维护工作流

> Protocol: spec/protocol-v0.6.md §0 (Universal Quantifier Discipline), §8 (Maturity), §10 (Versioning), §11 (Audit)
> Layer: L4 (Maintain) — 仅限 Anchorlaw 仓库内部（§14.6：MAY 限于协议自身仓库）
> Execution: inline

## 触发场景

在本仓库（Anchorlaw）内修改协议或实现时。外部使用者不需要本 skill。

## 铁律

1. **测试全绿**：任何改动必须 `python -m pytest --rootdir=python python/tests -q` 全绿（当前 70 个，新增时保持全绿；命令行被沙箱拦截时用包装脚本调 `pytest.main()`）。
2. **自指铁律**：scanner 必须能扫自己的代码不崩溃（第一律反身应用）。
3. **新功能必须配测试**：协议宣称的每条行为都要有测试证据，否则 §8 Maturity 标 Unverified。
4. **协议文档纪律**：
   - RFC 2119 措辞（MUST/SHOULD/MAY）分级
   - 每个全称声称（any/all/every/never）必须带验证证据或限定实现范围，改协议同步更新 §11 审计表
   - v0.x 升版记录**真实触发原因**，不许无理由升版
   - Maturity 表 Latest Evidence 写实测数据，不写「应该可以」
5. **通用协议铁律**：Anchorlaw 是语言无关协议，禁止过度 Python 化——anchor 抽象 = 声明位置 + 验证载体（§13）；跨语言新特性先在协议定义语言无关语义，再逐语言实现。
6. **提交纪律**：author 固定 `unknowbug`（禁止改 user.name）；commit message 英文、动词开头（`feat(v0.5): ...`）；commit 前测试全绿 + changelog/maturity 同步；push 后 GitHub→GitCode 自动同步。
7. **禁止修改 `E:\PYTHON\MC`（CoreSwap）目录**——需要实测时复制到 `E:\tmp` 副本或只读分析。

## 输出

测试全绿 + 协议文档证据同步 + 规范 commit。

## 约束

- 测试是协议自身的第一律应用，无测试不改协议。
- C++/TS 的 anchor 实现变化需同步 §13 三语言等价表。
