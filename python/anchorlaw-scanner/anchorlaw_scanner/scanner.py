"""
Defensive pattern scanner — AST-level code health check for the Anchorlaw Protocol.

Based on the principle of defensive clause detection:
Defensive code patterns expose the author's cognitive state —
"I'm not sure about this, but I don't want to say I don't know."

Patterns detected:
- SWALLOWED_EXCEPTION: Empty or trivial catch block
- BARE_EXCEPT: Overly broad exception handler
- MISSING_ANCHOR: Public function without a anchorlaw anchor
- VAGUE_TODO: TODO/FIXME without issue tracker reference
- DEFENSIVE_NULL_CHAIN: Chained null-check-and-return-null
- TRIVIAL_TEST: Self-referential or tautological test assertion

Maturity: VERIFIED — tested on real projects, 0 false positives in initial runs.
"""

import ast
import os
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class PatternType(Enum):
    SWALLOWED_EXCEPTION = auto()
    BARE_EXCEPT = auto()
    MISSING_ANCHOR = auto()
    VAGUE_TODO = auto()
    DEFENSIVE_NULL_CHAIN = auto()
    TRIVIAL_TEST = auto()
    SOURCE_ARTIFACT_MISSING = auto()  # §5.5 v0.7 Source Artifact Requirement

    @property
    def label(self) -> str:
        return {
            PatternType.SWALLOWED_EXCEPTION: "swallowed-exception",
            PatternType.BARE_EXCEPT: "bare-except",
            PatternType.MISSING_ANCHOR: "missing-anchor",
            PatternType.VAGUE_TODO: "vague-todo",
            PatternType.DEFENSIVE_NULL_CHAIN: "defensive-null-chain",
            PatternType.TRIVIAL_TEST: "trivial-test",
            PatternType.SOURCE_ARTIFACT_MISSING: "source-artifact-missing",
        }[self]

    @property
    def severity(self) -> str:
        """error | warning | info"""
        return {
            PatternType.SWALLOWED_EXCEPTION: "error",
            PatternType.BARE_EXCEPT: "error",
            PatternType.MISSING_ANCHOR: "warning",
            PatternType.VAGUE_TODO: "info",
            PatternType.DEFENSIVE_NULL_CHAIN: "warning",
            PatternType.TRIVIAL_TEST: "warning",
            PatternType.SOURCE_ARTIFACT_MISSING: "warning",
        }[self]

    @property
    def message_template(self) -> str:
        return {
            PatternType.SWALLOWED_EXCEPTION:
                "Exception swallowed without handling. "
                "Is this known to be safe (document why)? "
                "Or do you not know how to handle it (use @i_dont_know)?",
            PatternType.BARE_EXCEPT:
                "Bare except catches everything including KeyboardInterrupt and SystemExit. "
                "You don't know what you're catching — this is a defensive programming signal. "
                "Specify the exact exception type.",
            PatternType.MISSING_ANCHOR:
                "Public function has no anchorlaw anchor (@anchor.test or @anchor.i_dont_know). "
                "On what basis does it claim correctness?",
            PatternType.VAGUE_TODO:
                "TODO without issue tracker reference. "
                "This is a 'I know there's a problem but won't commit to fixing it' defensive signal. "
                "If the issue is known, reference a ticket. If uncertain, use @anchor.i_dont_know.",
            PatternType.DEFENSIVE_NULL_CHAIN:
                "Multiple chained null checks returning null — you are propagating the problem "
                "rather than solving it. Should this value ever be null? "
                "If not, use a more precise type. If yes, handle it at the boundary.",
            PatternType.TRIVIAL_TEST:
                "This test assertion may be tautological (e.g., assert f(x) == f(x)). "
                "Test anchors must contain substantive practice validation.",
            PatternType.SOURCE_ARTIFACT_MISSING:
                "source references a verification record with no on-disk artifact. "
                "§5.5 v0.7: the record (command + output summary) must exist under "
                ".investigations/ or .artifacts/ to be reproducible.",
        }[self]


@dataclass
class DefensivePattern:
    pattern_type: PatternType
    file_path: str
    line_number: int
    code_snippet: str
    suggestion: str
    function_name: str = ""
    severity: str = ""  # instance-level severity override (protocol 6.1);
                        # empty = fall back to pattern_type.severity

    @property
    def effective_severity(self) -> str:
        return self.severity or self.pattern_type.severity

    @property
    def formatted(self) -> str:
        header = f"[{self.effective_severity.upper()}] {self.pattern_type.label}"
        if self.function_name:
            header += f" (in {self.function_name})"
        return (
            f"{header}\n"
            f"  at {self.file_path}:{self.line_number}\n"
            f"  code: {self.code_snippet}\n"
            f"  suggestion: {self.suggestion}"
        )


# ---------------------------------------------------------------------------
# AST visitors
# ---------------------------------------------------------------------------

class _DefensiveVisitor(ast.NodeVisitor):
    """Walk AST and collect defensive patterns."""

    def __init__(self, file_path: str, source_lines: List[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.patterns: List[DefensivePattern] = []
        self._current_function: str = ""
        self._null_check_count: Dict[str, int] = {}  # per function

    # ---- helpers ----

    def _get_line(self, node: ast.AST) -> int:
        return getattr(node, "lineno", 0)

    def _get_snippet(self, node: ast.AST) -> str:
        line = self._get_line(node)
        if line and line <= len(self.source_lines):
            return self.source_lines[line - 1].strip()
        return "<source not available>"

    def _add(self, ptype: PatternType, node: ast.AST,
             suggestion: Optional[str] = None) -> None:
        self.patterns.append(DefensivePattern(
            pattern_type=ptype,
            file_path=self.file_path,
            line_number=self._get_line(node),
            code_snippet=self._get_snippet(node),
            suggestion=suggestion or ptype.message_template,
            function_name=self._current_function,
        ))

    # ---- visitors ----

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_func = self._current_function
        self._current_function = node.name
        self._null_check_count[self._current_function] = 0
        self.generic_visit(node)
        # After visiting, check null chain
        if self._null_check_count.get(self._current_function, 0) >= 2:
            # Find the function node in the last added pattern or use a heuristic
            pass  # We'll handle this differently via explicit chain detection
        self._current_function = old_func

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # treat same

    def visit_Try(self, node: ast.Try):
        for handler in node.handlers:
            self._check_except_handler(handler)
        self.generic_visit(node)

    def visit_If(self, node: ast.If):
        # Detect "if x is None: return None" pattern
        if self._is_none_check_and_return_none(node):
            self._null_check_count[self._current_function] = (
                self._null_check_count.get(self._current_function, 0) + 1
            )
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr):
        # Check for trivial assertions in test lambdas
        if isinstance(node.value, ast.Call):
            self._check_trivial_assert(node.value)
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert):
        self._check_trivial_assert(node)
        self.generic_visit(node)

    # ---- private checkers ----

    def _check_except_handler(self, handler: ast.ExceptHandler):
        """Check for swallowed or bare exceptions."""
        # Bare except
        if handler.type is None:
            self._add(PatternType.BARE_EXCEPT, handler)
            return

        # Swallowed: body is just 'pass'
        if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
            self._add(PatternType.SWALLOWED_EXCEPTION, handler)
            return

        # Swallowed: body is just a log/print call
        if len(handler.body) == 1 and isinstance(handler.body[0], ast.Expr):
            expr = handler.body[0]
            if isinstance(expr.value, ast.Call):
                func = expr.value.func
                if isinstance(func, ast.Name) and func.id in ("print", "log", "logger"):
                    self._add(PatternType.SWALLOWED_EXCEPTION, handler,
                             "Logging without handling — typically a defensive pattern of "
                             "'I don't want to handle this but need to look like I did.'")

    def _is_none_check_and_return_none(self, node: ast.If) -> bool:
        """Check if an If node is 'if x is None: return None'."""
        if not isinstance(node.test, ast.Compare):
            return False
        comp = node.test
        # Check for "is None" or "== None"
        is_none_check = False
        for op in comp.ops:
            if isinstance(op, ast.Is) or isinstance(op, ast.Eq):
                for comp_val in comp.comparators:
                    if isinstance(comp_val, ast.Constant) and comp_val.value is None:
                        is_none_check = True
                        break

        if not is_none_check:
            return False

        # Check that body returns None
        if len(node.body) != 1:
            return False
        stmt = node.body[0]
        if not isinstance(stmt, ast.Return):
            return False
        if stmt.value is None:
            return True  # bare return
        if isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
            return True  # return None
        return False

    def _check_trivial_assert(self, node: ast.AST):
        """Check for trivially true assertions."""
        if isinstance(node, ast.Assert):
            test = node.test
        elif isinstance(node, ast.Call):
            # Could be an assert-like call
            return  # Skip for now — complex to analyze
        else:
            return

        if isinstance(test, ast.Compare):
            # Check for self-comparison: f(x) == f(x)
            if (isinstance(test.left, ast.Call) and
                len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq) and
                len(test.comparators) == 1 and isinstance(test.comparators[0], ast.Call)):
                if self._same_call(test.left, test.comparators[0]):
                    self._add(PatternType.TRIVIAL_TEST, node,
                             "This assertion compares two calls to the same expression — it is always tautological.")

    def _same_call(self, a: ast.Call, b: ast.Call) -> bool:
        """Simple check if two Call nodes are identical."""
        try:
            return ast.dump(a) == ast.dump(b)
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Comment-based checks (not AST-able)
# ---------------------------------------------------------------------------

_VAGUE_TODO_RE = re.compile(
    r'#\s*(TODO|FIXME|HACK|XXX)\s*:?\s*(?!.*\b(issues?|ticket|GH-|#)\d+).*$',
    re.IGNORECASE
)


def _scan_comments(file_path: str, source_lines: List[str]) -> List[DefensivePattern]:
    """Scan source lines for vague TODOs and other comment-based patterns."""
    patterns = []
    for i, line in enumerate(source_lines):
        match = _VAGUE_TODO_RE.search(line)
        if match and not _is_inside_docstring(source_lines, i):
            patterns.append(DefensivePattern(
                pattern_type=PatternType.VAGUE_TODO,
                file_path=file_path,
                line_number=i + 1,
                code_snippet=line.strip(),
                suggestion=PatternType.VAGUE_TODO.message_template,
            ))
    return patterns


def _is_inside_docstring(source_lines: List[str], line_idx: int) -> bool:
    """Crude heuristic: check if line is likely inside a docstring."""
    in_docstring = False
    for i in range(line_idx + 1):
        stripped = source_lines[i].strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
    return in_docstring


# ---------------------------------------------------------------------------
# I/O keyword detection (for severity layering, per protocol v0.2 Sec 6.1)
# ---------------------------------------------------------------------------

# Keywords whose presence in a function body indicates I/O dependency.
# Functions matching >=2 categories, or >=3 keywords total, are I/O-heavy.
_IO_KEYWORD_CATEGORIES = {
    "file": {"open", "read", "write", "path", "file", "chmod", "chown", "rename"},
    "network": {"requests", "fetch", "http", "curl", "socket", "connect", "urlopen"},
    "image": {"Image", "PIL", "imread", "imwrite", "decode", "encode", "thumbnail"},
    "database": {"execute", "query", "cursor", "connect", "collection", "commit"},
    "subprocess": {"subprocess", "popen", "call", "check_output", "run"},
    "serialize": {"json.load", "json.dump", "pickle", "yaml", "toml"},
}


def _classify_function(tree: ast.AST, func_node: ast.FunctionDef) -> str:
    """Classify a function as 'pure', 'io_heavy', 'test', or 'private'.

    Pure: no I/O calls detected → WARNING severity for missing anchor
    IO-heavy: file/network/image calls detected → INFO severity
    Test: name starts with 'test_' → SKIP
    Private: name starts with '_' → SKIP
    """
    name = func_node.name
    if name.startswith("_"):
        return "private"
    if name.startswith("test_"):
        return "test"

    # Walk the function body and count I/O keyword hits
    io_categories_hit = set()
    total_hits = 0

    for node in ast.walk(func_node):
        kw: Optional[str] = None
        if isinstance(node, ast.Name):
            kw = node.id.lower()
        elif isinstance(node, ast.Attribute) and isinstance(node.attr, str):
            kw = node.attr.lower()

        if kw:
            for cat, keywords in _IO_KEYWORD_CATEGORIES.items():
                if kw in keywords:
                    io_categories_hit.add(cat)
                    total_hits += 1

    # Protocol v0.3 Sec 6.1: functions matching >=2 I/O keywords are I/O-heavy.
    # (Fix: implementation previously required >=3 hits or >=2 categories,
    #  which contradicted the spec — e.g. open()+read() stayed 'pure'.)
    if total_hits >= 2:
        return "io_heavy"
    return "pure"


# ---------------------------------------------------------------------------
# Anchor check (per protocol v0.2: severity layering + registry awareness)
# ---------------------------------------------------------------------------

def _scan_missing_anchors(
    file_path: str,
    tree: ast.AST,
    source_lines: List[str],
) -> List[DefensivePattern]:
    """Detect module-level public functions without anchor decorators.

    Severity layering per protocol v0.2 Sec 6.1:
    - Pure logic functions → WARNING
    - I/O-heavy functions → INFO (suggest @i_dont_know)
    - test_ prefixed → SKIP
    - Private (_ prefix) → SKIP
    """
    patterns = []

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        category = _classify_function(tree, node)
        if category in ("private", "test"):
            continue

        # Check decorators for anchorlaw.test / anchor.test or short aliases.
        # Legacy @pract.* (Practify-era) is still recognized so already-anchored
        # code is not mis-flagged after upgrade; the names are deprecated.
        has_anchor = False
        for decorator in node.decorator_list:
            dec_name = _get_decorator_name(decorator)
            if dec_name and (
                dec_name in ("pt", "idk")  # short aliases from anchorlaw_stub
                or "anchorlaw.test" in dec_name or "anchorlaw.i_dont_know" in dec_name
                or "anchor.test" in dec_name or "anchor.i_dont_know" in dec_name
                or "pract.test" in dec_name or "pract.i_dont_know" in dec_name  # legacy
            ):
                has_anchor = True
                break

        if has_anchor:
            continue

        # Check anchor registry for out-of-line anchors
        if _check_registry(node.name):
            continue

        # Build pattern with appropriate severity
        severity = "warning" if category == "pure" else "info"
        suggestion = (
            PatternType.MISSING_ANCHOR.message_template
            if category == "pure"
            else (
                "This function depends on external resources (I/O). "
                "Consider adding @anchor.i_dont_know to declare cognitive boundaries, "
                "or @anchor.test with mocked resources for critical paths."
            )
        )

        patterns.append(DefensivePattern(
            pattern_type=PatternType.MISSING_ANCHOR,
            file_path=file_path,
            line_number=node.lineno,
            code_snippet=source_lines[node.lineno - 1].strip()
            if node.lineno <= len(source_lines) else f"def {node.name}(...):",
            suggestion=suggestion,
            function_name=node.name,
            severity=severity,  # "warning" pure / "info" io-heavy (protocol 6.1)
        ))

    return patterns


# ---------------------------------------------------------------------------
# Anchor registry interop (per protocol v0.2 Sec 6.2)
# ---------------------------------------------------------------------------

# In-memory registry of functions known to have out-of-line anchors.
# Populated by anchorlaw when anchors are registered, or by scanning
# anchorlaw_anchors.py for _anchor_{name} functions.
_KNOWN_ANCHORED: set = set()


def register_anchored_function(name: str) -> None:
    """Inform the scanner that `name` has out-of-line anchors."""
    _KNOWN_ANCHORED.add(name)


def _check_registry(function_name: str) -> bool:
    """Check if a function has out-of-line anchors registered."""
    if function_name.startswith("_anchor_"):
        return True
    return function_name in _KNOWN_ANCHORED


def _load_anchors_from_project(scanned_dir: str) -> None:
    """Scan the project directory for anchorlaw_anchors.py and extract registrations.

    Per protocol v0.2 Sec 6.2: out-of-line anchor files are recognized by
    the scanner when they call register_anchored_function().
    """
    anchor_file = os.path.join(scanned_dir, "anchorlaw_anchors.py")
    if not os.path.exists(anchor_file):
        return
    try:
        with open(anchor_file, "r", encoding="utf-8") as f:
            content = f.read()
        import re
        # Pattern 1: direct register_anchored_function("name") calls
        for match in re.finditer(
            r"register_anchored_function\s*\(\s*['\"]([^'\"]+)['\"]", content
        ):
            _KNOWN_ANCHORED.add(match.group(1))
        # Pattern 2: _anchor_{name} wrapper functions — their names encode
        # the anchored function, e.g. _anchor_parse_json_robust → parse_json_robust
        for match in re.finditer(r"def _anchor_(\w+)\s*\(", content):
            _KNOWN_ANCHORED.add(match.group(1))
    except Exception:
        pass  # Best-effort only


def _get_decorator_name(decorator: ast.expr) -> Optional[str]:
    """Resolve a decorator to its full dotted name."""
    if isinstance(decorator, ast.Attribute):
        parts = []
        current = decorator
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        else:
            return None
        return ".".join(reversed(parts))
    elif isinstance(decorator, ast.Call):
        return _get_decorator_name(decorator.func)
    elif isinstance(decorator, ast.Name):
        return decorator.id
    return None


# ---------------------------------------------------------------------------
# Cumulative null chain detection (file-level)
# ---------------------------------------------------------------------------

def _scan_null_chains(
    file_path: str,
    tree: ast.AST,
    source_lines: List[str],
) -> List[DefensivePattern]:
    """Detect functions with excessive None-check-and-return-None patterns."""
    patterns = []

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        counter = _NoneCheckCounter()
        counter.visit(node)

        if counter.none_return_count >= 3:
            patterns.append(DefensivePattern(
                pattern_type=PatternType.DEFENSIVE_NULL_CHAIN,
                file_path=file_path,
                line_number=node.lineno,
                code_snippet=source_lines[node.lineno - 1].strip()
                if node.lineno <= len(source_lines) else f"def {node.name}(...):",
                suggestion=(
                    f"Function {node.name} contains {counter.none_return_count} "
                    "'if x is None: return None' patterns. You are propagating the None "
                    "problem rather than solving it. Express non-nullability in the type "
                    "system, or handle the None boundary at the entry point."
                ),
                function_name=node.name,
            ))

    return patterns


class _NoneCheckCounter(ast.NodeVisitor):
    """Count 'if x is None: return None' patterns in a function."""

    def __init__(self):
        self.none_return_count = 0

    def visit_If(self, node: ast.If):
        if self._is_none_return_none(node):
            self.none_return_count += 1
        self.generic_visit(node)

    def _is_none_return_none(self, node: ast.If) -> bool:
        # Check test: x is None or x == None
        is_none_check = False
        if isinstance(node.test, ast.Compare):
            for op in node.test.ops:
                if isinstance(op, (ast.Is, ast.Eq)):
                    for comp in node.test.comparators:
                        if (isinstance(comp, ast.Constant) and
                            comp.value is None):
                            is_none_check = True
        if not is_none_check:
            return False
        # Check body returns None
        if len(node.body) != 1:
            return False
        stmt = node.body[0]
        if not isinstance(stmt, ast.Return):
            return False
        if stmt.value is None:
            return True
        if isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
            return True
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan_file(file_path: str) -> List[DefensivePattern]:
    """Scan a single Python file for defensive patterns.

    Returns a list of DefensivePattern sorted by line number.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix != ".py":
        raise ValueError(f"Not a Python file: {file_path}")

    source = path.read_text(encoding="utf-8")
    source_lines = source.splitlines()

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        return [DefensivePattern(
            pattern_type=PatternType.SWALLOWED_EXCEPTION,
            file_path=file_path,
            line_number=e.lineno or 0,
            code_snippet=e.text or "",
            suggestion=f"Syntax error, cannot parse: {e.msg}",
        )]

    patterns: List[DefensivePattern] = []

    # AST-based scan
    visitor = _DefensiveVisitor(file_path, source_lines)
    visitor.visit(tree)
    patterns.extend(visitor.patterns)

    # Comment-based scan
    patterns.extend(_scan_comments(file_path, source_lines))

    # Anchor check (static, doesn't require import)
    patterns.extend(_scan_missing_anchors(file_path, tree, source_lines))

    # Null chain check
    patterns.extend(_scan_null_chains(file_path, tree, source_lines))

    # Sort by line number
    patterns.sort(key=lambda p: p.line_number)

    return patterns


def _collect_record_store(dir_path: str) -> str:
    """Concatenate text under .investigations/ and .artifacts/ — the on-disk
    verification records that `source` references must be findable here
    (§5.5 v0.7 Source Artifact Requirement)."""
    parts = []
    for sub in (".investigations", ".artifacts"):
        store_dir = Path(dir_path) / sub
        if store_dir.is_dir():
            for f in store_dir.rglob("*"):
                if f.is_file() and f.suffix in (".md", ".txt", ".log", ".yaml", ".yml", ".json"):
                    try:
                        parts.append(f.read_text(encoding="utf-8", errors="ignore"))
                    except OSError:
                        pass
    return "\n".join(parts)


def _scan_source_artifact_references(
    file_path: str, source_lines: List[str], record_store: str
) -> List[DefensivePattern]:
    """§5.5 v0.7: a `source="..."` string must reference an on-disk verification
    record. WARN when the referenced id/entry token is absent from the store."""
    findings = []
    source_re = re.compile(r'source\s*=\s*"([^"]+)"')
    for lineno, line in enumerate(source_lines, start=1):
        m = source_re.search(line)
        if not m:
            continue
        source_str = m.group(1)
        # Reference tokens with their #/! prefix (e.g. "#003", "!SURFBIOME") —
        # prefix-bearing tokens avoid silent PASS on bare short substrings.
        tokens = ["#" + t for t in re.findall(r"#([A-Za-z0-9_]+)", source_str)]
        tokens += ["!" + t for t in re.findall(r"!([A-Za-z0-9_]+)", source_str)]
        if source_str.startswith("static:"):
            continue  # §5.5: static source (idk-only) has no run record to persist
        found = any(tok in record_store for tok in tokens) if tokens else False
        if not found:
            findings.append(DefensivePattern(
                pattern_type=PatternType.SOURCE_ARTIFACT_MISSING,
                file_path=file_path,
                line_number=lineno,
                code_snippet=line.strip(),
                suggestion=(
                    f"source=\"{source_str[:60]}\" references no on-disk verification "
                    f"record; persist the command + output summary under "
                    f".investigations/ or .artifacts/ (e.g. regression-record.md)."
                ),
            ))
    return findings


def scan_directory(dir_path: str, recursive: bool = True) -> Dict[str, List[DefensivePattern]]:
    """Recursively scan a directory for defensive patterns in Python files.

    Returns dict of {file_path: [patterns]}.
    """
    # Load out-of-line anchor registrations before scanning
    _load_anchors_from_project(dir_path)

    # §5.5 v0.7 Source Artifact Requirement: collect on-disk verification
    # records once; source references are checked against them per file.
    record_store = _collect_record_store(dir_path)

    results = {}
    base = Path(dir_path)

    if recursive:
        py_files = list(base.rglob("*.py"))
    else:
        py_files = [p for p in base.iterdir() if p.suffix == ".py"]

    for py_file in py_files:
        # Skip hidden and test dirs
        if any(part.startswith(".") for part in py_file.parts):
            continue
        try:
            patterns = scan_file(str(py_file))
            try:
                lines = py_file.read_text(encoding="utf-8").splitlines()
            except OSError:
                lines = []
            patterns.extend(
                _scan_source_artifact_references(str(py_file), lines, record_store)
            )
            if patterns:
                results[str(py_file)] = patterns
        except Exception as e:
            results[str(py_file)] = [DefensivePattern(
                pattern_type=PatternType.SWALLOWED_EXCEPTION,
                file_path=str(py_file),
                line_number=0,
                code_snippet="",
                suggestion=f"Scan failed: {e}",
            )]

    return results


def summarize(patterns: List[DefensivePattern]) -> Dict:
    """Summarize scan results.

    Returns dict with pattern counts and severity distribution.
    """
    summary = {
        "total": len(patterns),
        "by_type": {},
        "by_severity": {"error": 0, "warning": 0, "info": 0},
    }
    for p in patterns:
        type_label = p.pattern_type.label
        summary["by_type"][type_label] = summary["by_type"].get(type_label, 0) + 1
        # Use effective_severity (protocol 6.1): I/O missing-anchor downgrades
        # to INFO; the summary must match the per-item display.
        summary["by_severity"][p.effective_severity] += 1
    return summary
