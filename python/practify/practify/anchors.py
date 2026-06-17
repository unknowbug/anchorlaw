"""
实践锚定系统：装饰器、注册表、验证执行。

核心概念：
- TestAnchor: 一个可执行的实践检验，是函数声明的一部分
- IDontKnowAnchor: 诚实型防御——"这个边界我尚未明确"
- AnchorRegistry: 全局注册表，追踪所有锚定

第一律在此体现为：每个 @pract.test 都是一个"可在有限步骤内完成并可观测结果
的实践检验方案"。没有锚点的函数产生警告（可编译但不可消除）。

同一律则的反身性：practify 自身的公开函数也需要注册锚点或被标记为 i_dont_know。
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import traceback


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class TestAnchor:
    """一个可执行的实践检验方案。

    test_fn 返回 True/False 或抛出异常。
    True = 通过检验。False = 检验失败。
    抛出异常 = 检验因意外原因无法完成。
    """
    description: str
    test_fn: Callable[[], bool]
    source_file: str = ""
    source_line: int = 0

    def run(self) -> "TestResult":
        """执行检验，返回结构化结果。"""
        try:
            passed = self.test_fn()
            return TestResult(
                description=self.description,
                passed=bool(passed),
                error=None if passed else "断言失败",
            )
        except Exception as e:
            return TestResult(
                description=self.description,
                passed=False,
                error=f"{type(e).__name__}: {e}",
                traceback_text=traceback.format_exc(),
            )


@dataclass
class IDontKnowAnchor:
    """诚实型防御声明。

    "我不知道"不是弱点——它是主动暴露认知边界，邀请实践检验。
    与防御性的"这个问题很复杂，暂不讨论"有本质区别：
    前者开放战场（"你来检验"），后者关闭战场（"你不许问"）。

    第一律唯一允许的防御类型。

    created_at: ISO 8601 timestamp. After 90 days without resolution,
    this anchor escalates from INFO to WARNING (staleness detection).
    """
    what: str
    source_file: str = ""
    source_line: int = 0
    created_at: str = ""  # ISO 8601, set at registration time


@dataclass
class TestResult:
    """单个检验的执行结果。"""
    description: str
    passed: bool
    error: Optional[str] = None
    traceback_text: Optional[str] = None


@dataclass
class FunctionAnchors:
    """一个函数上挂载的所有锚点。"""
    function_name: str
    function: Callable
    tests: List[TestAnchor] = field(default_factory=list)
    unknowns: List[IDontKnowAnchor] = field(default_factory=list)
    source_file: str = ""
    source_line: int = 0

    @property
    def has_practice_anchor(self) -> bool:
        """是否有至少一个实践锚点（test 或 i_dont_know）？"""
        return len(self.tests) > 0 or len(self.unknowns) > 0

    @property
    def is_fully_unknown(self) -> bool:
        """全部为未知声明（探索态，合法但需标注猜想本性）"""
        return len(self.tests) == 0 and len(self.unknowns) > 0

    @property
    def anchor_count(self) -> int:
        return len(self.tests) + len(self.unknowns)

    @property
    def health(self) -> str:
        """锚点健康度评估。

        - "healthy": 有测试且全部通过
        - "unverified": 仅有 i_dont_know，待实践检验
        - "stale_unknown": i_dont_know 超过 90 天未更新（协议 v0.2 5.3）
        - "degrading": 有测试但有失败
        - "skeleton": 无任何锚点（违反第一律）
        """
        if not self.has_practice_anchor:
            return "skeleton"
        if self.is_fully_unknown:
            if self._any_stale_unknown():
                return "stale_unknown"
            return "unverified"
        results = [t.run() for t in self.tests]
        if all(r.passed for r in results):
            if self._any_stale_unknown():
                return "stale_unknown"
            return "healthy"
        return "degrading"

    def _any_stale_unknown(self) -> bool:
        """Check if any i_dont_know anchor is older than 90 days."""
        from datetime import datetime, timezone, timedelta
        try:
            now = datetime.now(timezone.utc)
            threshold = timedelta(days=90)
            for u in self.unknowns:
                if u.created_at:
                    try:
                        created = datetime.fromisoformat(u.created_at)
                        if (now - created) > threshold:
                            return True
                    except (ValueError, TypeError):
                        pass
            return False
        except Exception:
            return False


class AnchorRegistry:
    """全局锚点注册表。

    单例模式。以函数的完全限定名为键。
    """

    def __init__(self):
        self._anchors: Dict[str, FunctionAnchors] = {}

    def register_test(
        self,
        func: Callable,
        description: str,
        test_fn: Callable[[], bool],
    ) -> TestAnchor:
        fa = self._get_or_create(func)
        anchor = TestAnchor(description=description, test_fn=test_fn)
        fa.tests.append(anchor)
        # Notify scanner registry (protocol v0.2 Sec 6.2)
        _notify_scanner(func)
        return anchor

    def register_unknown(self, func: Callable, what: str) -> IDontKnowAnchor:
        from datetime import datetime, timezone
        fa = self._get_or_create(func)
        anchor = IDontKnowAnchor(
            what=what,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        fa.unknowns.append(anchor)
        _notify_scanner(func)
        return anchor

    def get(self, func: Callable) -> Optional[FunctionAnchors]:
        return self._anchors.get(_qualname(func))

    def get_all(self) -> Dict[str, FunctionAnchors]:
        return dict(self._anchors)

    def run_tests(self, func: Optional[Callable] = None) -> List[TestResult]:
        results = []
        if func is not None:
            fa = self.get(func)
            if fa:
                for t in fa.tests:
                    results.append(t.run())
        else:
            for fa in self._anchors.values():
                for t in fa.tests:
                    results.append(t.run())
        return results

    def run_all_and_report(self) -> Dict[str, List[TestResult]]:
        """运行全部锚定测试，按函数分组返回结果。"""
        report = {}
        for key, fa in self._anchors.items():
            results = [t.run() for t in fa.tests]
            if results:
                report[key] = results
        return report

    def get_missing_anchor_functions(self, module) -> List[str]:
        """检查模块中哪些公开函数缺少实践锚点。

        公开 = 模块级定义、不以 _ 开头、在给定模块中定义。
        """
        missing = []
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_"):
                continue
            if obj.__module__ != module.__name__:
                continue
            key = _qualname(obj)
            if key not in self._anchors:
                missing.append(name)
        return missing

    def health_report(self, module) -> Dict:
        """生成模块的锚点健康度报告。

        返回：
        {
            "total_public_functions": N,
            "anchored": [...],
            "missing_anchors": [...],
            "degrading": [...],
            "healthy": [...],
        }
        """
        missing = self.get_missing_anchor_functions(module)
        report = {
            "total_public_functions": len(missing) + len(self._anchors),
            "missing_anchors": missing,
            "anchored": [],
        }
        for key, fa in self._anchors.items():
            h = fa.health
            entry = {
                "function": key,
                "health": h,
                "tests": len(fa.tests),
                "unknowns": len(fa.unknowns),
            }
            report["anchored"].append(entry)
        return report

    def clear(self) -> None:
        self._anchors.clear()

    def _get_or_create(self, func: Callable) -> FunctionAnchors:
        key = _qualname(func)
        if key not in self._anchors:
            try:
                source_file = inspect.getfile(func)
                source_line = inspect.getsourcelines(func)[1]
            except (TypeError, OSError):
                source_file = ""
                source_line = 0
            self._anchors[key] = FunctionAnchors(
                function_name=key,
                function=func,
                source_file=source_file,
                source_line=source_line,
            )
        return self._anchors[key]


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

_registry = AnchorRegistry()


def _notify_scanner(func: Callable) -> None:
    """Notify the scanner that `func` has out-of-line anchors.

    Per protocol v0.2 Sec 6.2: functions registered here are excluded
    from MISSING_ANCHOR warnings when the scanner runs.
    """
    try:
        from practify_scanner.scanner import register_anchored_function
        register_anchored_function(func.__name__)
    except ImportError:
        pass  # Scanner not installed — fine, this is just a notification


def _qualname(func: Callable) -> str:
    module = getattr(func, "__module__", "")
    name = getattr(func, "__qualname__", getattr(func, "__name__", str(func)))
    if module and module != "builtins":
        return f"{module}.{name}"
    return name


# ---------------------------------------------------------------------------
# Public decorators
# ---------------------------------------------------------------------------

def test(description: str, test_fn: Callable[[], bool]):
    """装饰器：为函数附加实践锚定测试。

    用法：
        @pract.test("正数除法", lambda: divide(6, 2) == 3)
        @pract.test("分母为零", lambda: divide(6, 0) == Err("DivByZero"))
        def divide(a, b):
            ...

    测试是被锚定函数声明的一部分，不是外部附属品。
    装饰器本身不修改函数行为——仅注册锚点元数据。

    也支持独立测试函数（不锚定到特定函数）：
        @pract.test("某集成场景", lambda: ...)
        def integration_check():
            ...
    """
    def decorator(fn):
        _registry.register_test(fn, description, test_fn)
        return fn
    return decorator


def i_dont_know(what: str):
    """装饰器：诚实声明"我不知道"。

    用法：
        @pract.i_dont_know("大文件（>1GB）场景的行为边界尚未确定")
        def process_file(path):
            ...

    唯物实践论唯一允许的"防御"。不是关闭战场——
    "这个问题我不讨论"——而是开放战场：
    "这个边界尚未经过实践检验，标记为待验证。"
    """
    def decorator(fn):
        _registry.register_unknown(fn, what)
        return fn
    return decorator


# ---------------------------------------------------------------------------
# Public accessors
# ---------------------------------------------------------------------------

def get_anchors(func: Callable) -> Optional[FunctionAnchors]:
    """获取函数的所有锚点信息。"""
    return _registry.get(func)


def get_all_anchored_functions() -> Dict[str, FunctionAnchors]:
    """获取所有已注册锚点的函数。"""
    return _registry.get_all()


def run_tests(func: Optional[Callable] = None) -> List[TestResult]:
    """运行注册的实践锚定测试。

    如果指定 func，仅运行该函数的测试；否则运行全部。
    """
    return _registry.run_tests(func)


def check_module(module) -> List[str]:
    """检查模块中缺少实践锚点的公开函数。"""
    return _registry.get_missing_anchor_functions(module)


def health_report(module) -> Dict:
    """生成模块的锚点健康度报告。"""
    return _registry.health_report(module)
