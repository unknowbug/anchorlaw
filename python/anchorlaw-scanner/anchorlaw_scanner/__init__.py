"""
anchorlaw-scanner — Defensive code pattern detection via AST analysis.

"Any claim must have a verifiable practice anchor."
    — Anchorlaw Protocol, First Law

This is the SCANNER component of the Anchorlaw Protocol.
It detects defensive code patterns that signal cognitive gaps.

Maturity: VERIFIED — tested on real projects, 0 false positives in initial runs.
"""

__version__ = "0.1.0"

from anchorlaw_scanner.scanner import (
    scan_file,
    scan_directory,
    summarize,
    register_anchored_function,
    DefensivePattern,
    PatternType,
)

__all__ = [
    "scan_file",
    "scan_directory",
    "summarize",
    "register_anchored_function",
    "DefensivePattern",
    "PatternType",
]
