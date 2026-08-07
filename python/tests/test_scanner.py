"""Anchorlaw scanner 单元测试——保证 scanner 自身可验证（第一律自指：scanner 必须能通过自己的检验标准）。

覆盖协议 v0.3 §6 Pattern Catalog：P1 swallowed exception / P2 bare except /
P3 missing anchor（severity layering + registry awareness）/ P4 vague TODO /
P5 defensive null chain / P6 trivial test。
"""
import textwrap

import pytest

from anchorlaw_scanner.scanner import (
    PatternType,
    register_anchored_function,
    scan_directory,
    scan_file,
    summarize,
)


def _write(tmp_path, name, src):
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(src), encoding="utf-8")
    return str(p)


def _types(patterns):
    return {p.pattern_type for p in patterns}


def _missing(patterns):
    return [p for p in patterns if p.pattern_type == PatternType.MISSING_ANCHOR]


class TestSwallowedException:
    def test_empty_except(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def f():
                try:
                    risky()
                except ValueError:
                    pass
        """)
        assert PatternType.SWALLOWED_EXCEPTION in _types(scan_file(f))

    def test_logging_only_except(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def f():
                try:
                    risky()
                except ValueError:
                    print("failed")
        """)
        assert PatternType.SWALLOWED_EXCEPTION in _types(scan_file(f))

    def test_handled_except_not_flagged(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def f():
                try:
                    risky()
                except ValueError:
                    return fallback()
        """)
        assert PatternType.SWALLOWED_EXCEPTION not in _types(scan_file(f))


class TestBareExcept:
    def test_bare_except(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def f():
                try:
                    risky()
                except:
                    return None
        """)
        assert PatternType.BARE_EXCEPT in _types(scan_file(f))


class TestMissingAnchor:
    def test_pure_function_warning(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def compute(x):
                return x * 2
        """)
        anchor = _missing(scan_file(f))
        assert anchor
        assert anchor[0].effective_severity == "warning"
        assert anchor[0].function_name == "compute"

    def test_io_function_info_severity(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def load_file(path):
                with open(path) as fp:
                    return fp.read()
        """)
        anchor = _missing(scan_file(f))
        assert anchor
        assert anchor[0].effective_severity == "info"

    def test_test_prefixed_skipped(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def test_something():
                return True
        """)
        assert not _missing(scan_file(f))

    def test_private_skipped(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def _helper():
                return 1
        """)
        assert not _missing(scan_file(f))

    def test_anchored_function_not_flagged(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            from pract_stub import test as pt

            @pt("double of 2 is 4", lambda: compute(2) == 4)
            def compute(x):
                return x * 2
        """)
        assert not _missing(scan_file(f))

    def test_out_of_line_registry(self, tmp_path):
        register_anchored_function("external_fn")
        f = _write(tmp_path, "a.py", """
            def external_fn():
                return 42
        """)
        assert not _missing(scan_file(f))


class TestVagueTodo:
    def test_vague_todo_flagged(self, tmp_path):
        f = _write(tmp_path, "a.py", "# TODO fix this later\n")
        assert PatternType.VAGUE_TODO in _types(scan_file(f))

    def test_todo_with_ticket_not_flagged(self, tmp_path):
        f = _write(tmp_path, "a.py", "# TODO: handle edge case, see GH-123\n")
        assert PatternType.VAGUE_TODO not in _types(scan_file(f))


class TestNullChain:
    def test_null_chain_flagged(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def parse(data):
                if data is None:
                    return None
                if data.get("a") is None:
                    return None
                if data.get("b") is None:
                    return None
                return data
        """)
        assert PatternType.DEFENSIVE_NULL_CHAIN in _types(scan_file(f))


class TestTrivialTest:
    def test_tautology_flagged(self, tmp_path):
        f = _write(tmp_path, "b.py", "assert f(1) == f(1)\n")
        assert PatternType.TRIVIAL_TEST in _types(scan_file(f))


class TestScanAPI:
    def test_scan_file_rejects_non_python(self, tmp_path):
        f = _write(tmp_path, "a.txt", "hello")
        with pytest.raises(ValueError):
            scan_file(f)

    def test_scan_file_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            scan_file(str(tmp_path / "nope.py"))

    def test_syntax_error_tolerated(self, tmp_path):
        f = _write(tmp_path, "bad.py", "def broken(:\n")
        scan_file(f)  # 不应抛异常

    def test_summarize_counts(self, tmp_path):
        f = _write(tmp_path, "a.py", """
            def f():
                try:
                    risky()
                except:
                    pass
        """)
        s = summarize(scan_file(f))
        assert s["total"] >= 1
        assert s["by_severity"]["error"] >= 1
        assert s["by_type"].get("bare-except") == 1

    def test_scan_directory_recursive(self, tmp_path):
        _write(tmp_path, "a.py", "def f():\n    return 1\n")
        _write(tmp_path, "sub/b.py", "def g():\n    return 2\n")
        results = scan_directory(str(tmp_path))
        assert any("a.py" in k for k in results)
        assert any("sub" in k and "b.py" in k for k in results)

    def test_scan_directory_skips_hidden(self, tmp_path):
        _write(tmp_path, ".hidden.py", "def h():\n    return 1\n")
        results = scan_directory(str(tmp_path))
        assert not any(".hidden" in k for k in results)
