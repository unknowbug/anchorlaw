"""
practify-scanner CLI — scan Python code for defensive patterns.

Usage:
    python -m practify_scanner check <path>
    python -m practify_scanner report <path>
"""

import argparse
import sys
from pathlib import Path
from typing import Optional


def _cmd_check(args):
    """Scan files/directories for defensive patterns."""
    from practify_scanner.scanner import scan_file, scan_directory, summarize

    path = Path(args.path)
    if path.is_file():
        patterns = scan_file(str(path))
        results = {str(path): patterns}
    elif path.is_dir():
        results = scan_directory(str(path), recursive=not args.no_recursive)
    else:
        print(f"ERROR: path not found — {args.path}")
        sys.exit(1)

    total_patterns = 0
    for filepath, patterns in results.items():
        if not patterns:
            continue
        print(f"\n{'=' * 70}")
        print(f"FILE: {filepath}")
        print(f"{'=' * 70}")
        for p in patterns:
            print(f"\n{p.formatted}")
            total_patterns += 1

    print(f"\n{'-' * 70}")
    print(f"Total: {total_patterns} defensive patterns (across {len(results)} files)")

    all_patterns = []
    for patterns in results.values():
        all_patterns.extend(patterns)
    summary = summarize(all_patterns)
    sev = summary["by_severity"]
    print(f"By severity: ERR={sev['error']} WARN={sev['warning']} INFO={sev['info']}")

    if sev["error"] > 0:
        sys.exit(1)


def _cmd_report(args):
    """Generate comprehensive health report."""
    from practify_scanner.scanner import scan_file, scan_directory, summarize

    path = Path(args.path)
    if path.is_file():
        patterns = scan_file(str(path))
        results = {str(path): patterns}
    elif path.is_dir():
        results = scan_directory(str(path))
    else:
        print(f"ERROR: path not found — {args.path}")
        sys.exit(1)

    all_patterns = []
    for patterns in results.values():
        all_patterns.extend(patterns)
    scan_summary = summarize(all_patterns)

    print("=" * 60)
    print("  practify-scanner Code Health Report")
    print("=" * 60)

    print(f"\n[Scanner] {scan_summary['total']} findings")
    for sev in ("error", "warning", "info"):
        count = scan_summary["by_severity"].get(sev, 0)
        if count:
            print(f"   {sev}: {count}")

    print(f"\n   Pattern distribution:")
    for ptype, count in sorted(scan_summary["by_type"].items()):
        print(f"   - {ptype}: {count}")

    # Verdict
    print(f"\n[Diagnostic Verdict]:")
    errors = scan_summary["by_severity"].get("error", 0)
    warnings = scan_summary["by_severity"].get("warning", 0)

    if errors == 0 and warnings == 0:
        print(f"   [PASS] Code healthy — no defensive patterns detected.")
    elif errors >= 5:
        print(f"   [WARN] Excessive defensive patterns — significant dishonest-defense signals.")
    else:
        print(f"   [INFO] Some defensive patterns found. Review and add @pract.test or @pract.i_dont_know anchors.")
        print(f"   Learn more: https://github.com/practify/practify")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="practify-scanner",
        description="Defensive code pattern scanner for Python — Practify Protocol Level 1",
    )
    sub = parser.add_subparsers(dest="command", help="subcommand")

    p_check = sub.add_parser("check", help="Scan for defensive patterns")
    p_check.add_argument("path", help="File or directory path")
    p_check.add_argument("--no-recursive", action="store_true",
                         help="Don't recursively scan subdirectories")

    p_report = sub.add_parser("report", help="Generate comprehensive health report")
    p_report.add_argument("path", help="File or directory path")

    return parser


def main(args: Optional[list] = None):
    parser = build_parser()
    args = parser.parse_args(args)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {"check": _cmd_check, "report": _cmd_report}
    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
