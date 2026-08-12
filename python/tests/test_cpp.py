"""anchorlaw-scanner C++ 支持单元测试。

验证语言无关的 @anchor 注释式标注：提取、格式校验（test 必须带 source）、
多文件扫描。对应协议 v0.4 C++ cross-language note。
"""
import textwrap

import pytest

from anchorlaw_scanner.cpp import (
    CppAnchor,
    is_cpp_file,
    scan_cpp_file,
    summarize_cpp,
)


def _write(tmp_path, name, src):
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(src), encoding="utf-8")
    return str(p)


class TestIsCppFile:
    def test_extensions(self):
        assert is_cpp_file("a.cpp")
        assert is_cpp_file("b.h")
        assert is_cpp_file("c.hpp")
        assert is_cpp_file("d.cc")
        assert not is_cpp_file("e.py")
        assert not is_cpp_file("f.js")


class TestScanCpp:
    def test_extracts_test_anchor(self, tmp_path):
        f = _write(tmp_path, "density.h", '''
            // @anchor.test("density matches Java", source="probe:block_probe!density")
            int density(int x, int y, int z);
        ''')
        anchors = scan_cpp_file(f)
        assert len(anchors) == 1
        a = anchors[0]
        assert a.kind == "test"
        assert a.description == "density matches Java"
        assert a.source == "probe:block_probe!density"
        assert a.valid

    def test_extracts_idk_anchor(self, tmp_path):
        f = _write(tmp_path, "surface.h", '''
            // @anchor.idk("1.17 surface edge cases unverified")
            void apply_surface(...);
        ''')
        anchors = scan_cpp_file(f)
        assert len(anchors) == 1
        assert anchors[0].kind == "idk"
        assert anchors[0].valid  # idk 不需要 source

    def test_test_anchor_without_source_invalid(self, tmp_path):
        f = _write(tmp_path, "a.h", '''
            // @anchor.test("no source here")
            int f();
        ''')
        anchors = scan_cpp_file(f)
        assert len(anchors) == 1
        assert not anchors[0].valid
        assert any("source" in i for i in anchors[0].issues)

    def test_empty_description_invalid(self, tmp_path):
        f = _write(tmp_path, "a.h", '''
            // @anchor.test("", source="probe:x")
            int f();
        ''')
        anchors = scan_cpp_file(f)
        assert not anchors[0].valid

    def test_comment_detection_not_in_code(self, tmp_path):
        f = _write(tmp_path, "a.h", '''
            int x = 1;  // @anchor.idk("still a comment, ok")
        ''')
        anchors = scan_cpp_file(f)
        assert len(anchors) == 1  # 行注释中的标注应被识别

    def test_single_line_anchor(self, tmp_path):
        f = _write(tmp_path, "a.h", "// @anchor.test(\"one line\", source=\"trace:x\")\n")
        anchors = scan_cpp_file(f)
        assert len(anchors) == 1
        assert anchors[0].valid


class TestSummarize:
    def test_summary(self, tmp_path):
        f = _write(tmp_path, "a.h", '''
            // @anchor.test("a", source="probe:1")
            // @anchor.idk("b")
            int f();
        ''')
        anchors = scan_cpp_file(f)
        s = summarize_cpp(anchors)
        assert s["total"] == 2
        assert s["test"] == 1
        assert s["idk"] == 1
        assert s["invalid"] == []

class TestCliCppWiring:
    """CLI 接线：check 命令对 C++ 文件做 annotation-extraction
    （参考实现改进，协议 §8 C++ = annotation-extraction 声称的实现入口）。"""

    def test_check_cpp_file_valid(self, tmp_path, capsys):
        import argparse
        from anchorlaw_scanner import cli
        f = _write(tmp_path, "foo.cpp", '''
            // @anchor.test("valid anchor", source="trace:probe#001")
            int foo() { return 1; }
        ''')
        ns = argparse.Namespace(command="check", path=f, lang="cpp",
                                no_recursive=False)
        cli._cmd_check(ns)  # valid → 不抛 SystemExit
        out = capsys.readouterr().out
        assert "VALID" in out
        assert "Total: 1 anchors" in out

    def test_check_cpp_file_invalid_exits(self, tmp_path, capsys):
        import argparse
        from anchorlaw_scanner import cli
        f = _write(tmp_path, "bad.cpp", '''
            // @anchor.test("missing source")
            int bad() { return 0; }
        ''')
        ns = argparse.Namespace(command="check", path=f, lang="cpp",
                                no_recursive=False)
        with pytest.raises(SystemExit) as e:
            cli._cmd_check(ns)
        assert e.value.code == 1
        out = capsys.readouterr().out
        assert "INVALID" in out
        assert "must be fixed" in out

    def test_check_cpp_dir_with_lang_cpp(self, tmp_path, capsys):
        import argparse
        from anchorlaw_scanner import cli
        _write(tmp_path, "a.cpp", '''
            // @anchor.test("a ok", source="trace:p#1")
            int a() { return 1; }
        ''')
        _write(tmp_path, "b.h", '''
            // @anchor.idk("b unknown")
            int b();
        ''')
        ns = argparse.Namespace(command="check", path=str(tmp_path), lang="cpp",
                                no_recursive=False)
        cli._cmd_check(ns)
        out = capsys.readouterr().out
        assert "Total: 2 anchors" in out
        assert "test=1 idk=1" in out

    def test_check_cpp_dir_skips_py_files(self, tmp_path, capsys):
        import argparse
        from anchorlaw_scanner import cli
        _write(tmp_path, "x.py", '''
            def f(x):
                return x
        ''')
        ns = argparse.Namespace(command="check", path=str(tmp_path), lang="cpp",
                                no_recursive=False)
        cli._cmd_check(ns)
        out = capsys.readouterr().out
        assert "Total: 0 anchors" in out  # C++ 模式不处理 .py
