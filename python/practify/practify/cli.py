"""
practify CLI — 唯物实践论代码验证的命令行入口。

用法：
    python -m practify check <path>       扫描防御性模式
    python -m practify test [module]      运行锚定测试
    python -m practify noise list         列出未解决的噪声卡
    python -m practify noise resolve <id> 解决噪声卡
    python -m practify noise search <kw>  搜索噪声卡
    python -m practify report <path>      生成综合报告
    python -m practify ai-context         导出 AI 上下文注入文本
    python -m practify curriculum         导出从噪声中提炼的课程
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Encoding-safe output helpers (Windows GBK can't handle emoji)
# ---------------------------------------------------------------------------

def _safe_print(*args, **kwargs):
    """Print with encoding fallback for Windows GBK terminals."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: strip non-ASCII
        safe_args = tuple(
            str(a).encode("ascii", errors="replace").decode("ascii")
            for a in args
        )
        print(*safe_args, **kwargs)


# ASCII-safe status markers
PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"
INFO = "[INFO]"
ERROR = "[ERROR]"


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
        _safe_print(f"ERROR: path not found — {args.path}")
        sys.exit(1)

    total_patterns = 0
    for filepath, patterns in results.items():
        if not patterns:
            continue
        _safe_print(f"\n{'=' * 70}")
        _safe_print(f"FILE: {filepath}")
        _safe_print(f"{'=' * 70}")
        for p in patterns:
            _safe_print(f"\n{p.formatted}")
            total_patterns += 1

    _safe_print(f"\n{'-' * 70}")
    _safe_print(f"Total: {total_patterns} defensive patterns (across {len(results)} files)")

    # Summary
    all_patterns = []
    for patterns in results.values():
        all_patterns.extend(patterns)
    summary = summarize(all_patterns)
    sev = summary["by_severity"]
    _safe_print(f"\nBy severity: ERR={sev['error']} WARN={sev['warning']} INFO={sev['info']}")

    if sev["error"] > 0:
        sys.exit(1)


def _cmd_test(args):
    """Run registered anchor tests."""
    import importlib

    module = None
    if args.module:
        try:
            module = importlib.import_module(args.module)
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location("target", args.module)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                _safe_print(f"ERROR: cannot load module — {args.module}")
                sys.exit(1)

    from practify.anchors import run_tests

    results = run_tests()
    if not results:
        _safe_print(f"{INFO} No registered anchor tests. Use @pract.test to anchor functions.")
        return

    passed = 0
    failed = 0
    for r in results:
        icon = PASS if r.passed else FAIL
        _safe_print(f"{icon} {r.description}")
        if not r.passed:
            failed += 1
            if r.error:
                _safe_print(f"   -> {r.error}")
            if args.verbose and r.traceback_text:
                _safe_print(f"   {r.traceback_text}")
        else:
            passed += 1

    _safe_print(f"\n{'-' * 40}")
    _safe_print(f"Results: {passed} passed, {failed} failed, {len(results)} total")

    if module:
        from practify.anchors import check_module
        missing = check_module(module)
        if missing:
            _safe_print(f"\n{WARN} Public functions missing practice anchors:")
            for name in missing:
                _safe_print(f"   - {name}")

    if failed > 0:
        sys.exit(1)


def _cmd_noise_list(args):
    """List noise cards."""
    from practify.noise import list_unresolved, list_all as list_all_noise

    cards = list_all_noise() if args.all else list_unresolved()
    if not cards:
        _safe_print(f"{INFO} No matching noise cards.")
        return

    for card in cards:
        icon = "[OK]" if card.resolved else "[!!]"
        _safe_print(f"\n{icon} [{card.noise_id[-8:]}] {card.function_name}")
        _safe_print(f"   Trigger: {card.trigger}")
        _safe_print(f"   Observed: {card.observed}")
        _safe_print(f"   Expected: {card.expected}")
        if card.discovery:
            _safe_print(f"   Discovery: {card.discovery}")
        if card.resolved and card.converted_to_test:
            _safe_print(f"   Converted to: {card.converted_to_test}")

    unresolved = sum(1 for c in cards if not c.resolved)
    _safe_print(f"\n{'-' * 40}")
    _safe_print(f"{len(cards)} cards ({unresolved} unresolved)")


def _cmd_noise_resolve(args):
    """Resolve a noise card."""
    from practify.noise import resolve_noise
    ok = resolve_noise(args.noise_id, args.converted_test or "")
    if ok:
        _safe_print(f"{PASS} Noise {args.noise_id} marked as resolved.")
    else:
        _safe_print(f"{FAIL} Noise not found: {args.noise_id}")
        sys.exit(1)


def _cmd_noise_search(args):
    """Search noise cards."""
    from practify.noise import search_noise
    cards = search_noise(args.keyword)
    if not cards:
        _safe_print(f"No noise cards matching '{args.keyword}'.")
        return
    for card in cards:
        status = "[OK]" if card.resolved else "[!!]"
        _safe_print(f"{status} [{card.noise_id[-8:]}] {card.function_name}: {card.trigger[:80]}")


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
        _safe_print(f"ERROR: path not found — {args.path}")
        sys.exit(1)

    from practify.noise import export_summary

    noise_summary = export_summary()
    all_patterns = []
    for patterns in results.values():
        all_patterns.extend(patterns)
    scan_summary = summarize(all_patterns)

    _safe_print("=" * 60)
    _safe_print("  practify Code Health Report")
    _safe_print("=" * 60)

    # Scanner
    _safe_print(f"\n[Scanner] {scan_summary['total']} findings")
    for sev in ("error", "warning", "info"):
        count = scan_summary["by_severity"].get(sev, 0)
        if count:
            _safe_print(f"   {sev}: {count}")
    _safe_print(f"   Pattern distribution:")
    for ptype, count in sorted(scan_summary["by_type"].items()):
        _safe_print(f"   - {ptype}: {count}")

    # Noise
    _safe_print(f"\n[Noise Cards]:")
    _safe_print(f"   Total: {noise_summary['total']}")
    _safe_print(f"   Unresolved: {noise_summary['unresolved']}")
    _safe_print(f"   Resolved: {noise_summary['resolved']}")

    if noise_summary["top_functions"]:
        _safe_print(f"   Top functions:")
        for func, count in noise_summary["top_functions"][:5]:
            _safe_print(f"   - {func}: {count} cards")

    # Verdict
    _safe_print(f"\n[Diagnostic Verdict]:")
    errors = scan_summary["by_severity"].get("error", 0)
    unresolved = noise_summary["unresolved"]

    if errors >= 3:
        _safe_print(f"   {WARN} Excessive defensive patterns — significant dishonest-defense signals")
    if unresolved >= 5:
        _safe_print(f"   {WARN} Accumulated unresolved noise — unhandled cognitive boundaries")
    if errors == 0 and unresolved == 0:
        _safe_print(f"   {PASS} Code healthy — all public functions anchored, no pending noise")
    elif errors < 3 and unresolved < 5:
        _safe_print(f"   {INFO} Code mostly healthy, minor improvements needed")


def _cmd_ai_context(args):
    """Export AI context injection text."""
    from practify.noise import export_for_ai, export_curriculum

    function_names = args.functions.split(",") if args.functions else None
    noise_context = export_for_ai(
        function_names=function_names,
        limit=args.limit,
        unresolved_only=not args.all,
    )
    curriculum = export_curriculum()

    _safe_print(noise_context)
    if curriculum and curriculum != "(No curriculum extracted yet)":
        _safe_print("\n---\n")
        _safe_print(curriculum)


def _cmd_curriculum(args):
    """Export curriculum extracted from noise."""
    from practify.noise import export_curriculum
    _safe_print(export_curriculum())


def _cmd_init(args):
    """Initialize .pract directory and generate pract_stub.py."""
    pract_dir = Path(".pract")
    pract_dir.mkdir(exist_ok=True)
    (pract_dir / "noise_cards.json").touch()

    # Generate pract_stub.py from template
    stub_path = Path("pract_stub.py")
    if not stub_path.exists():
        import shutil
        template = Path(__file__).parent / "pract_stub_template.py"
        if template.exists():
            shutil.copy(template, stub_path)
            _safe_print(f"{PASS} Generated pract_stub.py")
            _safe_print("   Import from this file in your source:")
            _safe_print('   from pract_stub import test as pt, i_dont_know as idk')
            _safe_print("   To uninstall practify: delete this file + practify/ directory.")
            _safe_print("   Anchors will auto-degrade to no-ops if practify is not installed.")
        else:
            _safe_print(f"{WARN} pract_stub template not found — skipping stub generation")
    else:
        _safe_print(f"{INFO} pract_stub.py already exists — skipping")

    _safe_print(f"{PASS} Initialized practify at {pract_dir.absolute()}")
    _safe_print("   Noise cards: .pract/noise_cards.json")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="practify",
        description="Materialist Practice code verification protocol",
    )
    sub = parser.add_subparsers(dest="command", help="subcommand")

    p_check = sub.add_parser("check", help="Scan for defensive patterns")
    p_check.add_argument("path", help="File or directory path")
    p_check.add_argument("--no-recursive", action="store_true",
                         help="Don't recursively scan subdirectories")

    p_test = sub.add_parser("test", help="Run anchor tests")
    p_test.add_argument("module", nargs="?", help="Module to load (optional)")
    p_test.add_argument("-v", "--verbose", action="store_true",
                        help="Show full tracebacks")

    p_noise = sub.add_parser("noise", help="Noise card management")
    p_noise_sub = p_noise.add_subparsers(dest="noise_action")

    p_nlist = p_noise_sub.add_parser("list", help="List noise cards")
    p_nlist.add_argument("--all", action="store_true", help="Include resolved")

    p_nresolve = p_noise_sub.add_parser("resolve", help="Resolve a noise card")
    p_nresolve.add_argument("noise_id", help="Noise ID (or suffix)")
    p_nresolve.add_argument("--converted-test", help="Regression test created")

    p_nsearch = p_noise_sub.add_parser("search", help="Search noise cards")
    p_nsearch.add_argument("keyword", help="Search keyword")

    p_report = sub.add_parser("report", help="Generate comprehensive health report")
    p_report.add_argument("path", help="File or directory path")

    p_ai = sub.add_parser("ai-context", help="Export AI context injection text")
    p_ai.add_argument("--functions", help="Comma-separated function names")
    p_ai.add_argument("--limit", type=int, default=20, help="Max cards")
    p_ai.add_argument("--all", action="store_true", help="Include resolved cards")

    sub.add_parser("curriculum", help="Export curriculum from noise")
    sub.add_parser("init", help="Initialize .pract working directory")

    return parser


def main(args: Optional[list] = None):
    parser = build_parser()
    args = parser.parse_args(args)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "check": _cmd_check,
        "test": _cmd_test,
        "noise": _cmd_noise_dispatch,
        "report": _cmd_report,
        "ai-context": _cmd_ai_context,
        "curriculum": _cmd_curriculum,
        "init": _cmd_init,
    }

    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(args)
    else:
        parser.print_help()
        sys.exit(1)


def _cmd_noise_dispatch(args):
    """Dispatch noise subcommand."""
    if not args.noise_action:
        _safe_print("Specify noise operation: list | resolve | search")
        sys.exit(1)

    dispatch = {
        "list": _cmd_noise_list,
        "resolve": _cmd_noise_resolve,
        "search": _cmd_noise_search,
    }
    fn = dispatch.get(args.noise_action)
    if fn:
        fn(args)
    else:
        _safe_print(f"Unknown operation: {args.noise_action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
