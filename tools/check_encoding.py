#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_encoding.py — 仓库文件编码/健康检查（治 v0.9 编码误报环境债）。

背景（v0.9 实践复盘）：review 曾把 README_zh.md 误报为「编码损坏」，
主 Agent 因 Windows 终端 GBK/UTF-8 干扰花了多轮手工验证才排除。
本脚本一次运行给出确定性结论：逐文件按 UTF-8 严格解码，报告
失败文件 + 解码失败位置，代替手工多轮验证（协议 §15.4 终止门禁 B：
排除误报的验证不得超过 1 轮——用脚本执行这一轮）。

用法：
    python tools/check_encoding.py                 # 扫描仓库文本文件
    python tools/check_encoding.py <path> ...      # 只检查指定文件/目录

退出码：0 = 全部 UTF-8 正常；1 = 存在无法按 UTF-8 解码的文件。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 仓库内需要按 UTF-8 严格校验的文本扩展名
TEXT_EXTS = {
    ".md", ".py", ".toml", ".json", ".yaml", ".yml", ".ts", ".js",
    ".txt", ".cfg", ".ini", ".gitignore",
}
# 明确跳过的路径（二进制/依赖/构建产物）
SKIP_DIRS = {
    ".git", ".pytest_cache", "__pycache__", "node_modules", "dist", "build",
}


def collect_targets(paths: list[str]) -> list[Path]:
    """解析命令行参数：默认仓库根，可指定文件/目录。"""
    roots = [Path(p) for p in paths] if paths else [REPO_ROOT]
    targets: list[Path] = []
    for root in roots:
        root = root.resolve()
        if root.is_file():
            targets.append(root)
        elif root.is_dir():
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                if any(part in SKIP_DIRS for part in p.parts):
                    continue
                if p.suffix.lower() in TEXT_EXTS:
                    targets.append(p)
        else:
            print(f"skip (not found): {root}")
    return targets


def check_file(path: Path) -> tuple[bool, str]:
    """按 UTF-8 严格解码。返回 (是否正常, 失败详情或空串)。"""
    data = path.read_bytes()
    try:
        data.decode("utf-8")
        return True, ""
    except UnicodeDecodeError as exc:
        # 报告首个失败字节的位置，便于定位
        bad = data[exc.start:exc.end]
        detail = (
            f"{exc.reason} at byte {exc.start} (bad bytes: {bad.hex(' ')}); "
            f"expected UTF-8 — file may be GBK/other encoding"
        )
        return False, detail


def main(argv: list[str]) -> int:
    targets = collect_targets(argv)
    failures: list[tuple[Path, str]] = []
    for p in sorted(targets):
        ok, detail = check_file(p)
        if not ok:
            failures.append((p, detail))
    if failures:
        for p, detail in failures:
            print(f"FAIL {p.relative_to(REPO_ROOT) if p.is_relative_to(REPO_ROOT) else p}: {detail}")
        print(f"\n{len(failures)} file(s) failed strict UTF-8 decoding")
        return 1
    print(f"OK: {len(targets)} text file(s) all valid UTF-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
