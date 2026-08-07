"""Anchorlaw anchors 单元测试。

覆盖协议 v0.3 §5 Anchor Semantics：test anchor / i_dont_know anchor /
anchor health states（healthy/unverified/degrading/stale_unknown/skeleton）/
staleness detection（90 天）/ missing anchor 检测。

注意：import 的 test 装饰器必须别名（pract_test），否则 pytest 会把
模块级裸名 `test` 收集为测试函数。
"""
import sys
from datetime import datetime, timedelta, timezone

from anchorlaw import (
    check_module,
    get_anchors,
    health_report,
    i_dont_know as pract_idk,
    run_tests,
    test as pract_test,
)
from anchorlaw.anchors import _registry


# ---- 模块级被测函数（check_module 用 inspect.getmembers 只找模块级） ----

@pract_test("anchored fn returns 1", lambda: anchor_module_fn() == 1)
def anchor_module_fn():
    return 1


@pract_idk("unknown behavior")
def unknown_module_fn():
    return 2


def missing_module_fn():
    return 3


def _make_stale(anchor, days=91):
    """把 i_dont_know anchor 的 created_at 改到 N 天前。"""
    anchor.unknowns[0].created_at = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).isoformat()


class TestTestAnchor:
    def test_registers_and_runs(self):
        _registry.clear()

        @pract_test("double of 2 is 4", lambda: anchor_compute(2) == 4)
        def anchor_compute(x):
            return x * 2

        fa = get_anchors(anchor_compute)
        assert fa is not None
        assert fa.has_practice_anchor
        assert len(fa.tests) == 1

        results = run_tests(anchor_compute)
        assert len(results) == 1
        assert results[0].passed

    def test_failing_claim(self):
        _registry.clear()

        @pract_test("wrong claim", lambda: anchor_broken() == 99)
        def anchor_broken():
            return 1

        results = run_tests(anchor_broken)
        assert not results[0].passed
        assert results[0].error

    def test_raising_test_fn(self):
        _registry.clear()

        @pract_test("raises", lambda: anchor_boom())
        def anchor_boom():
            raise RuntimeError("kaboom")

        results = run_tests(anchor_boom)
        assert not results[0].passed
        assert "RuntimeError" in results[0].error
        assert results[0].traceback_text

    def test_decorator_preserves_function(self):
        _registry.clear()

        @pract_test("identity", lambda: anchor_ident(5) == 5)
        def anchor_ident(x):
            return x

        assert anchor_ident(5) == 5  # 装饰器不修改函数行为


class TestIDontKnowAnchor:
    def test_registers(self):
        _registry.clear()

        @pract_idk("large file behavior unverified")
        def anchor_process(path):
            return path

        fa = get_anchors(anchor_process)
        assert fa is not None
        assert fa.is_fully_unknown
        assert fa.health == "unverified"

    def test_has_practice_anchor(self):
        _registry.clear()

        @pract_idk("unknown")
        def anchor_unknown_fn2():
            return 1

        assert get_anchors(anchor_unknown_fn2).has_practice_anchor


class TestHealthStates:
    def test_healthy(self):
        _registry.clear()

        @pract_test("ok", lambda: anchor_ok() == 1)
        def anchor_ok():
            return 1

        assert get_anchors(anchor_ok).health == "healthy"

    def test_degrading(self):
        _registry.clear()

        @pract_test("bad", lambda: anchor_bad() == 0)
        def anchor_bad():
            return 1

        assert get_anchors(anchor_bad).health == "degrading"

    def test_stale_unknown_escalates(self):
        _registry.clear()

        @pract_idk("old unknown")
        def anchor_old():
            return 1

        _make_stale(get_anchors(anchor_old))
        assert get_anchors(anchor_old).health == "stale_unknown"

    def test_fresh_unknown_not_stale(self):
        _registry.clear()

        @pract_idk("fresh")
        def anchor_fresh():
            return 1

        assert get_anchors(anchor_fresh).health == "unverified"


class TestModuleChecks:
    def _ensure_module_anchors(self):
        """显式注册模块级函数（import 时的注册会被其它测试的 _registry.clear() 清掉）。"""
        from anchorlaw.anchors import AnchorRegistry
        reg = _registry
        reg.clear()
        reg.register_test(anchor_module_fn, "anchored fn returns 1",
                          lambda: anchor_module_fn() == 1)
        reg.register_unknown(unknown_module_fn, "unknown behavior")

    def test_check_module_detects_missing(self):
        self._ensure_module_anchors()
        missing = check_module(sys.modules[__name__])
        assert "missing_module_fn" in missing
        assert "anchor_module_fn" not in missing
        assert "unknown_module_fn" not in missing

    def test_health_report_structure(self):
        self._ensure_module_anchors()
        report = health_report(sys.modules[__name__])
        assert "total_public_functions" in report
        assert "missing_anchors" in report
        assert "anchored" in report
        assert any(e["function"].endswith("anchor_module_fn") for e in report["anchored"])


class TestExecutionTracking:
    def test_run_count_increments(self):
        _registry.clear()

        @pract_test("tracked", lambda: anchor_tracked() == 1)
        def anchor_tracked():
            return 1

        fa = get_anchors(anchor_tracked)
        assert fa.tests[0].run_count == 0  # 注册未执行

        run_tests(anchor_tracked)
        assert fa.tests[0].run_count == 1
        assert fa.tests[0].last_run_at  # 记录了运行时间

    def test_health_report_execution_metrics(self):
        _registry.clear()

        @pract_test("executed", lambda: anchor_exec(1) == 1)
        def anchor_exec(x):
            return x

        run_tests(anchor_exec)
        report = health_report(sys.modules[__name__])
        entry = next(e for e in report["anchored"] if e["function"].endswith("anchor_exec"))
        assert "anchor_execution" in entry
        assert entry["anchor_execution"]["total_anchors"] >= 1
        # health_report 的 health 属性会执行测试（副作用），因此 executed >= 1
        assert entry["anchor_execution"]["executed"] >= 1


class TestRegistryIsolation:
    def test_clear(self):
        _registry.clear()

        @pract_test("x", lambda: anchor_iso() == 1)
        def anchor_iso():
            return 1

        assert len(_registry.get_all()) >= 1
        _registry.clear()
        assert len(_registry.get_all()) == 0
