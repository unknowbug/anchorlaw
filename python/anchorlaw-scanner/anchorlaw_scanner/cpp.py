# -*- coding: utf-8 -*-
"""注释式标注提取器（C++ / Go / Java）：scanner 识别 @anchor 注释式标注（语言无关的标注抽象）。

设计原则（通用协议性）：
- Anchor 是语言无关的概念：声明位置 + 验证载体。
- Python: 装饰器 @test(...)（运行时注册）
- TypeScript: JSDoc 注释（现有实现）
- C++ / Go / Java: 行注释 // @anchor.test(...) / // @anchor.idk(...)（§2.4/§13 v0.16 登记）
- 验证载体独立：通常是 probe/test binary（如 block_probe.cpp 对比参考实现输出）

本模块实现注释式语言文件的标注提取与格式验证（不做完整 AST 分析，
避免把协议 scanner 变成语言编译器）。
"""
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# 注释式标注语言源文件扩展名（C++ / Go / Java）
CPP_EXTENSIONS = {".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".hh", ".hxx", ".go", ".java"}

# // @anchor.test("描述", source="trace:...") 或 // @anchor.idk("描述")
_ANCHOR_RE = re.compile(
    r"@anchor\.(?P<kind>test|idk)\s*\(\s*"
    r"(?P<desc>[\"'])(?P<description>.*?)(?P=desc)"
    r"(?P<rest>.*?)\)",
    re.DOTALL,
)

# source 字段：source="..." （test 必填）
_SOURCE_RE = re.compile(r'source\s*=\s*["\']([^"\']*)["\']')


@dataclass
class CppAnchor:
    """C++ 文件中提取出的一个 anchor 标注。"""
    kind: str            # "test" | "idk"
    description: str
    source: str          # 验证载体引用（probe/trace/文件）；test 必须提供
    file_path: str
    line_number: int
    valid: bool          # 格式是否合规（test 必须有 source）
    issues: List[str] = field(default_factory=list)


def is_cpp_file(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in CPP_EXTENSIONS


def scan_cpp_file(file_path: str, source: Optional[str] = None) -> List[CppAnchor]:
    """扫描一个 C++ 文件，提取并校验 @anchor 标注。

    source 参数（可选）提供文件内容，避免重复读取。
    返回 CppAnchor 列表（含格式校验结果）。
    """
    if source is None:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    lines = source.splitlines()

    anchors: List[CppAnchor] = []
    # 逐行扫描（标注必须完整在一行内，或由调用方保证已合并）
    for i, line in enumerate(lines, 1):
        for m in _ANCHOR_RE.finditer(line):
            kind = m.group("kind")
            description = m.group("description").strip()
            rest = m.group("rest")
            sm = _SOURCE_RE.search(rest)
            src = sm.group(1) if sm else ""

            issues: List[str] = []
            if not description:
                issues.append("description 为空")
            if kind == "test" and not src:
                issues.append("test 标注必须提供 source 字段（验证载体引用）")

            anchors.append(CppAnchor(
                kind=kind,
                description=description,
                source=src,
                file_path=file_path,
                line_number=i,
                valid=not issues,
                issues=issues,
            ))
    return anchors


def summarize_cpp(anchors: List[CppAnchor]) -> Dict:
    """C++ 标注汇总。"""
    summary = {
        "total": len(anchors),
        "test": sum(1 for a in anchors if a.kind == "test"),
        "idk": sum(1 for a in anchors if a.kind == "idk"),
        "invalid": [a for a in anchors if not a.valid],
    }
    return summary
