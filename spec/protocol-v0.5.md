# Anchorlaw Protocol v0.5

> **语言无关的代码验证协议规范**
>
> "任何声称都必须有可验证的实践锚点。"
>
> Status: **Working Draft**. Components are at different maturity levels — see [Maturity](#maturity).
>
> v0.5: added the Anchor Skill Manifest (§14) — a language-agnostic, layered
> skill catalog that moves protocol knowledge from always-loaded context to
> on-demand playbooks, fixing agent-side attention dilution.
>
> v0.4: protocol renamed from Practify to Anchorlaw; added C++ comment-form
> annotations, universal-claim audit (§11), rule challenge process (§12),
> and the language-agnostic anchor abstraction (§13).

---

## Changelog from v0.1

| Change | Trigger | Section |
|--------|---------|---------|
| **Stub-based uninstall** — zero-dependency removal via `anchorlaw_stub.py` | photo_screener trial: "卸载后代码还能跑吗?" | [2. Uninstall Guarantee](#2-uninstall-guarantee) |
| **Missing anchor severity layering** — I/O functions get INFO, not WARNING | photo_screener trial: 21 warnings, many on `load_and_preprocess` etc. | [6.1 Severity Layering](#61-severity-layering) |
| **Anchor registry interop** — scanner recognizes out-of-line anchors | photo_screener trial: `pract_anchors.py` invisible to scanner | [6.2 Registry-Aware Scanning](#62-registry-aware-scanning) |
| **@i_dont_know staleness** — auto-escalate after 90 days | 待补充260607: 噪声即课题; unverified unknowns rot | [5.3 Staleness Detection](#53-staleness-detection) |

## Changelog from v0.4

| Change | Trigger | Section |
|--------|---------|---------|
| **Anchor Skill Manifest** — layered, single-responsibility skills move protocol knowledge from always-loaded context to on-demand playbooks | agent-side attention dilution: protocol efficacy failed not in code but in agent context; full 13-section protocol + project rules diluted attention; users need only subsets (testing only, review only) | [§14](#14-agent-skills-anchor-skill-manifest-v05) |
| **CLI binding contract** — agents MUST operate via CLI, never internal imports | library API surface (~27 exports) would re-dilute attention exactly like the full protocol text | [§14.4](#144-cli-binding-contract) |
| **Version bump** v0.4 → v0.5 | new normative section (§14) added | [§10](#10-versioning) |

## Changelog from v0.3

| Change | Trigger | Section |
|--------|---------|---------|
| **Protocol rename** Practify → Anchorlaw (repo, packages, CLI) | generic-name collision risk; 10 same-name GitHub repos | §0 |
| **C++ support** — comment-form `@anchor.test` / `@anchor.idk` annotations | CoreSwap integration (E:\PYTHON\MC): header-inline worldgen + probe binaries | [§2.4](#24-cross-language-notes), [§13](#13-protocol-generality-anchor-abstraction-v04) |
| **Key Words (RFC 2119)** + universal quantifier discipline | unverified universal claims violate the Second Law | [§0](#0-key-words-and-universal-quantifier-discipline) |
| **Universal claim audit** — every MUST/guarantee carries evidence or is scoped | audit found 'All languages' claim exceeded Rust implementation | [§11](#11-universal-claim-audit-v04) |
| **Rule challenge process (Third Law)** — FP evidence forces rule downgrade/removal | protocol had no path to challenge its own rules | [§12](#12-rule-challenge-process-third-law-v04) |
| **Unit tests for scanner/anchors/noise** (55 tests) + CI self-scan | First Law applied reflexively: a verification protocol must verify itself | [§8](#8-maturity) |
| **Anchor execution tracking** — run_count / never_ran in health report | registered-but-never-run anchors are degraded anchors | [§5.4](#54-anchor-health-states) |
| **Severity layering actually applied** — P3 I/O functions now report INFO | implementation fixed severity to WARNING regardless of classification | [§6.1](#61-severity-layering) |

## Changelog from v0.2

| Change | Trigger | Section |
|--------|---------|---------|
| **Source provenance** — @pt anchors MUST carry source field | RE Framework integration: anchors without trace provenance are unfalsifiable | [5.1 Test Anchor](#51-test-anchor), [5.5 Source Provenance](#55-source-provenance) |
| **Degraded verification** — three operating modes for RE (full/partial/degraded) | RE Framework: lifted .cpp often can't compile standalone | [9. Degraded Verification](#9-degraded-verification) |
| **Uncompilable anchor state** — honest declaration when code can't run | RE Framework: binary-internal deps prevent anchorlaw test | [5.4 Anchor Health States](#54-anchor-health-states) |
| **Verify retry cap** — max 3 Lift→Verify cycles before going back to A-layer | RE Framework: prevent process entropy in unfalsifiable loops | [9. Degraded Verification](#9-degraded-verification) |

---

## 0. Key Words and Universal Quantifier Discipline

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in **RFC 2119**.

**Universal quantifier discipline** (唯物实践论第五版 §6.2): every universal claim
in this protocol ("any", "all", "every", "never") MUST either
(a) carry a verification record in [Maturity](#8-maturity), or
(b) be explicitly scoped to its current implementation.
An unverified universal claim is a closed-framework language form — it violates
the Second Law (framework reflexivity). Every universal claim is audited in
[§11](#11-universal-claim-audit-v04).

---

## 1. Protocol Overview

Anchorlaw is a **three-layer code verification protocol** for vibe coding workflows:

| Layer | What it does | When it runs | Maturity |
|-------|-------------|-------------|----------|
| **Scanner** | Detects defensive code patterns via AST analysis | Compile-time (static) | **Verified** — Python: 38 findings 0 FP. TypeScript: validated on test files. |
| **Anchors** | Binds verifiable tests to function declarations | Compile-time (declarative) + Runtime (validation) | **Experimental** — 18/18 tests passed in photo_screener trial. |
| **Noise Cards** | Accumulates runtime failures as structured knowledge | Runtime (continuous) | **Unverified** — schema defined, no project has accumulated >0 cards. |

### Core Principle (First Law)

> Any claim must be convertible to a verifiable practice test, executable in finite steps with observable results. Otherwise it is invalid for the purpose of pursuing effectiveness.

### "Only Offense, No Defense"

The protocol does not prohibit. It demands proof.
- Traditional: "You cannot divide by zero." (defensive)
- Anchorlaw: "Prove the divisor is non-zero, or handle the zero case." (offensive)

The single allowed defense is `i_dont_know` — an honest declaration that opens the battlefield for practice feedback.

---

## 2. Uninstall Guarantee

> **A protocol must not become a new form of technical debt.**

The Anchorlaw Protocol guarantees that removing it from a project requires deleting at most **two files** and optionally **one line per source file**. Source files with residual anchor lines MUST continue to function correctly after removal.

### 2.1 Mechanism: `anchorlaw_stub.py`

Each anchorlaw-instrumented project contains a single stub file at the project root:

```python
# anchorlaw_stub.py
# Generated by `anchorlaw init`. Delete this file to disable all anchors.
# Keep this file without anchorlaw installed: decorators degrade to no-ops.

try:
    from anchorlaw import test as _pract_test, i_dont_know as _pract_idk
except ImportError:
    # anchorlaw not installed — anchors silently become no-ops.
    # Code continues to run without modification.
    def _pract_test(description, test_fn):
        return lambda f: f

    def _pract_idk(what):
        return lambda f: f

# Public names
test = _pract_test
i_dont_know = _pract_idk
```

Source files import from the stub:

```python
from anchorlaw_stub import test as pt, i_dont_know as idk

# @anchor: anchors auto-degrade if anchorlaw_stub.py or anchorlaw/ is removed.
# @pt lines can remain in source — they become dead imports (harmless).

@pt("empty list", lambda: process([]) == [])
@idk("behavior with large files not yet verified")
def process(data):
    ...
```

### 2.2 Three Operating States

| State | `anchorlaw_stub.py` | `anchorlaw/` | Behavior |
|-------|:---:|:---:|------|
| **Full** | Yes | Yes | Anchors register and validate. `anchorlaw test` works. |
| **Silent** | Yes | No | Decorators are no-ops. Code runs. Anchors don't register. |
| **Clean** | No | No | `from anchorlaw_stub import` fails. Remove that line. Code is pristine. |

### 2.3 Removal Procedure

```
1. Delete anchorlaw_stub.py
2. Delete anchorlaw/ directory (or uninstall anchorlaw pip package)
3. (Optional) Remove `from anchorlaw_stub import ...` lines from source files.
   These lines will cause ImportError if not removed, but:
   - A single sed/grep fixes all files: grep -rl "anchorlaw_stub" . | xargs sed -i '/anchorlaw_stub/d'
   - Or leave them — the ImportError is clean and explicit.
```

**No AST-level code rewriting is required. No scanning the entire project to strip decorators.**

### 2.4 Cross-Language Notes

- **Python**: Decorator-based no-op (as above)
- **TypeScript**: JSDoc annotations (`/** @anchor.test ... */`) are comments — removing anchorlaw requires zero code changes. The annotations become inert documentation. (Verified)
- **C++ (v0.4)**: line comments `// @anchor.test("description", source="...")` and `// @anchor.idk("description")`. Comments are inert by construction — removing anchorlaw requires zero code changes. The validation carrier is typically an independent probe binary (e.g. `block_probe.cpp` comparing against a reference implementation). Validated against a real header-inline project (CoreSwap density.h, 842 lines): annotations extracted correctly, zero false positives.
- **Rust**: Proc macros expand to no-ops when the crate is removed from `Cargo.toml`. (**Specified but NOT yet implemented** — see [§11](#11-universal-claim-audit-v04).)
- **All languages (scoped)**: For implemented languages (Python, TypeScript, C++), anchors MUST be removable by deleting a single dependency declaration, and annotations in source MUST be inert when the dependency is absent. Rust is pending implementation.

---

## 3. Noise Card JSON Schema

(Unchanged from v0.1 — minor field clarifications)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://anchorlaw.dev/noise-card-v0.2.json",
  "type": "object",
  "required": ["noise_id", "timestamp", "trigger", "function_name", "observed", "expected"],
  "properties": {
    "noise_id": {
      "type": "string",
      "description": "Globally unique identifier"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of failure observation"
    },
    "trigger": {
      "type": "string",
      "description": "Exact input or condition that triggered the failure"
    },
    "function_name": {
      "type": "string",
      "description": "Fully qualified function name"
    },
    "observed": {
      "type": "string",
      "description": "What actually happened. Specific — stack traces, return values, error messages."
    },
    "expected": {
      "type": "string",
      "description": "What should have happened per the function's claimed behavior."
    },
    "anchor_violated": {
      "type": "string",
      "description": "Which anchor (test description) was violated, if any."
    },
    "discovery": {
      "type": "string",
      "description": "What new knowledge did this failure produce? What did we not know before?"
    },
    "curriculum": {
      "type": "string",
      "description": "Concise, reusable lesson for AI context injection. Must be actionable."
    },
    "converted_to_test": {
      "type": "string",
      "description": "Description of the regression test created from this noise card."
    },
    "resolved": {
      "type": "boolean",
      "default": false
    },
    "resolved_at": {
      "type": "string",
      "format": "date-time"
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Classification tags"
    },
    "context_snippet": {
      "type": "string",
      "description": "Code snippet surrounding the failure point (max 500 chars)"
    },
    "language": {
      "type": "string",
      "description": "Origin language — enables cross-language curriculum"
    }
  }
}
```

---

## 4. AI Context Format

(Unchanged from v0.1)

---

## 5. Anchor Semantics

### 5.1 Test Anchor

| Property | Description |
|----------|-------------|
| **Purpose** | A verifiable practice test bound to a function declaration |
| **Semantics** | "I claim this function behaves correctly under condition X, and here is a reproducible test." |
| **Required fields** | `description` (human-readable), `test_fn` (executable predicate returning boolean) |
| **Required field (v0.3)** | `source` (provenance string): MUST record where the test vector data came from — trace_id, register/memory snapshot, observation timestamp. See [5.5 Source Provenance](#55-source-provenance). |
| **Compile-time check** | Every public function MUST have at least one test anchor OR one i_dont_know anchor |
| **Runtime check** | Test anchors SHOULD be executable via `anchorlaw test`. If code cannot be independently compiled (e.g., RE-lifted code with internal binary dependencies), see [9. Degraded Verification](#9-degraded-verification). |

### 5.2 I-Don't-Know Anchor

| Property | Description |
|----------|-------------|
| **Purpose** | Honest declaration of a cognitive boundary |
| **Semantics** | "This function has edge cases I haven't verified yet. I am actively inviting practice feedback." |
| **Required fields** | `what` (specific description of what is unknown) |
| **Optional field (v0.3)** | `source` (provenance string): for RE use cases, records what static analysis prompted this unknown — F5 output, missing trace coverage, etc. Helps distinguish "I don't know because I haven't looked" from "I looked and genuinely can't determine." |
| **Difference from TODO** | TODO = "I know what to do but haven't done it." I-don't-know = "I don't yet know what the correct behavior is." |

### 5.3 Staleness Detection

@i_dont_know anchors created more than 90 days ago, on functions that have been modified since the anchor was created, MUST be escalated:
- Scanner severity: INFO → WARNING
- Message: "This cognitive boundary was declared N days ago. Has sufficient practice data accumulated to convert it to a @anchor.test?"

Implementations SHOULD record the creation date of each @i_dont_know anchor. The `anchorlaw_stub.py`-based approach records this in the anchor file itself.

### 5.4 Anchor Health States

| State | Condition | Meaning |
|-------|----------|---------|
| `healthy` | All tests pass | Function's claimed behavior is verified |
| `unverified` | Only i_dont_know anchors, no tests | Exploration zone |
| `degrading` | Has tests but some fail | Previously verified behavior is now broken |
| `stale_unknown` | i_dont_know > 90 days, function modified | Cognitive boundary overdue for resolution |
| `skeleton` | No anchors at all | Violation of First Law |
| `uncompilable` (v0.3) | Has anchors but code cannot be independently compiled | Anchors carry source provenance but anchorlaw test cannot execute. Verification deferred to runtime trace comparison. Common in RE use cases. |

### 5.5 Source Provenance (v0.3)

> **Each test anchor must answer: "Where did this data come from?"**

Without source provenance, a test anchor is unfalsifiable — it could be derived from the same B1 hypothesis it claims to verify (circular reasoning), or fabricated entirely. Source provenance is the A-layer anchor point that breaks this circle.

**Source string format:**

```
source="<source_type>:<binary_or_file>!<function>#<id>, offset=<addr>, <key_observations> observed <ISO8601_timestamp>"
```

**Source types:**

| Type | Meaning | Allowed for @pt | Allowed for @idk |
|------|---------|:--:|:--:|
| `trace` | Dynamic debugging: register/memory snapshot from Frida/x64dbg/etc. | ✅ | ✅ |
| `memory` | Memory dump: extracted constant tables, vtables, string tables | ✅ | ✅ |
| `static` | Static analysis inference (F5 output, IDA disassembly, Ghidra decompiler) | ❌ | ✅ |

**Rule:** @pt MUST use `trace` or `memory` source. @pt with `static` source or without source → INVALID (rejected at review).

**Rule:** @idk MAY use `static` source — honestly stating "this unknown was inferred from static analysis, not observed in trace."

**Examples:**

```
# Valid @pt — trace-based source
@pt("volume=5 → eax=1",
    lambda: speak(Animal(), 5) == 1,
    source="trace:foo.dll!speak#002, offset=0x1A, edx=5 eax=1 observed 2026-06-18T10:00:05Z")

# Valid @idk — static-based source, honest about origin
@idk("volume=100 时是否会溢出？",
     source="static:foo.dll!speak@0x1400077c0, F5 shows cmp edx,64h but trace never hit edx≥100")

# INVALID — @pt has no source
@pt("volume=5 → eax=1", lambda: speak(Animal(), 5) == 1)  # ← rejected
```

**Implementation note:** The `source` parameter is a string. Implementations MAY validate its format but MUST preserve it verbatim. The `anchorlaw_stub.py`-based approach passes `source` as an additional keyword argument to the decorator; when anchorlaw is not installed, the stub silently discards it (the anchor degrades to no-op but the source string remains in source code for audit).

---

## 6. Scanner Pattern Catalog

### 6.1 Severity Layering

The `missing-anchor` pattern (P3) MUST be severity-layered based on function characteristics:

| Function Category | Severity | Rationale |
|-------------------|----------|-----------|
| Pure logic, no I/O calls | **WARNING** | High anchor value — easy to test, high regression risk |
| Contains I/O calls (`open`, `requests`, `Image.open`, etc.) | **INFO** | Low anchor value — test requires mocking or real resources. Suggest `@i_dont_know`. |
| Name starts with `test_` | **SKIP** | Already a test function. Don't flag. |
| Name starts with `_` | **SKIP** | Private/internal. Don't flag. |

I/O detection keywords (language-agnostic):
- File: `open`, `read`, `write`, `Path`, `fs`, `file`
- Network: `requests`, `fetch`, `http`, `curl`, `socket`, `connect`
- Image: `Image`, `PIL`, `imread`, `imwrite`, `decode`, `encode`
- Database: `execute`, `query`, `cursor`, `connect`, `collection`

Functions matching ≥2 I/O keywords are classified as I/O-heavy.

### 6.2 Registry-Aware Scanning

The scanner MUST consult the runtime anchor registry before reporting `missing-anchor`.

When `anchorlaw test` is run, all decorated functions register their anchors. The scanner checks this registry:
- Function found in registry with ≥1 test anchor → **do not report**
- Function found in registry with only `i_dont_know` → **do not report** (it's in honest exploration state)
- Function found in registry with no anchors → **report MISSING_ANCHOR**

This enables **out-of-line anchor files** (`pract_anchors.py`) — anchors registered on wrapper functions whose names follow the convention `_anchor_{function_name}` are associated with the target function.

### 6.3 Pattern Definitions

#### P3: Missing Practice Anchor (REVISED)

| Property | Value |
|----------|-------|
| **Severity** | WARNING (pure logic) / INFO (I/O-heavy) / SKIP (test_ prefix or private) |
| **Definition** | A public function without a test anchor or i_dont_know declaration, **and** not found in the anchor registry |
| **Cross-language** | Same severity layering applies in all implementations |

#### P1, P2, P4-P6

(Unchanged from v0.1: Swallowed Exception, Bare Exception Handler, Defensive Null Propagation, Trivially True Test, Vague TODO)

---

## 7. Implementation Compliance Levels

| Level | Requirements |
|-------|-------------|
| **Level 1 — Scanner** | Implements P1-P6 with severity layering (6.1) and registry awareness (6.2). CLI. |
| **Level 2 — Anchors** | Level 1 + stub-based anchor system (Section 2) with test/i_dont_know decorators. |
| **Level 3 — Noise** | Level 2 + noise card creation and AI context export. Staleness detection (5.3). |
| **Level 4 — Full Protocol** | Level 3 + runtime noise card accumulation integrated with test runner. |

---

## 8. Maturity

| Component | Python | TypeScript | C++ (v0.4) | Maturity | Latest Evidence |
|-----------|--------|-----------|-----------|----------|----------------|
| Scanner | ✅ | ✅ | annotation-extraction | **Verified** | photo_screener: 38 findings 0 FP; 55 unit tests (v0.4); severity layering verified by tests |
| Anchors | ✅ | — | **Experimental** | photo_screener: 18/18 tests passed, 0 bugs found, 0 regressions |
| Source Provenance (v0.3) | — | — | **Conjecture** | Field defined in protocol. 0 RE projects have produced sourced anchors. |
| Noise Cards | ✅ | — | **Unverified** | 0 cards accumulated |
| AI Context | ✅ | — | **Conjecture** | 0 injection cycles run |
| Stub Uninstall | ✅ | ✅ (comment-form) | ✅ (comment-form) | **Verified** | Tested: delete stub + anchorlaw, code still runs via no-op fallback; comment-form inert by construction |
| Degraded Verification (v0.3) | — | — | **Conjecture** | Modes defined. No RE project has exercised Partial/Degraded paths. |
| Agent Skills (v0.5) | — | — | **Conjecture** | §14 manifest defined. Reasonix reference implementation ships with manifest conformance tests (v0.5). No third-party agent trial yet. |

---

## 9. Degraded Verification (v0.3 Draft)

> **Not all anchored code can be independently compiled and run.** This is not a failure of the protocol — it is an honest recognition that A-layer verification has material prerequisites. When those prerequisites are absent, the protocol MUST degrade gracefully rather than pretend.

### 9.1 Three Operating Modes

| Mode | Condition | anchorlaw test | Confidence auto-promotion | Anchor source requirement |
|------|----------|:---:|:---:|:---:|
| **Full** | Anchorlaw installed AND code self-contained (no unresolved external deps) | ✅ Runs | ✅ draft→candidate | @pt MUST have trace/memory source |
| **Partial** | Anchorlaw installed BUT code has unresolved dependencies (common in RE: lifted code depends on internal binary symbols) | ❌ Cannot run | ❌ Manual only | @pt MUST still carry source — the anchor serves as documented hypothesis until runtime verification becomes possible |
| **Degraded** | Anchorlaw not installed | ❌ N/A | ❌ Manual only | Source provenance still required in _anchors.py for audit trail |

### 9.2 Self-Containment Classification

Before `anchorlaw test` is invoked, the function MUST be classified:

**Self-contained:** No calls to external functions, no global variable references, no custom types from outside the translation unit.
→ Eligible for Full mode.

**Has-deps:** Calls other functions OR references global state OR uses custom types.
→ Check dependency resolution:
  - All dependencies are themselves self-contained AND lifted → merge and compile → Full mode
  - Any dependency is unresolved → Partial mode → record in `uncompilable_functions.yaml`

### 9.3 Uncompilable Functions Manifesto

```yaml
# uncompilable_functions.yaml
- function: speak
  source_location: "foo.dll:0x1400077c0"
  uncompilable_reason: "depends on AudioDevice::write (0x140008000) and Animal::vftable"
  unresolved_deps:
    - type: function
      name: AudioDevice::write
      address: "foo.dll:0x140008000"
      lift_status: not_started
    - type: vtable
      name: Animal::vftable
      address: "foo.dll:0x140007000"
  suggested_path: "Lift AudioDevice::write first, then retry speak compilation"
  anchor_count: 4
  anchor_sources_valid: true  # all @pt have trace/memory source
```

### 9.4 Retry Cap (Anti-Entropy)

When Partial or Degraded mode is active, the Lift→Verify cycle has a **hard cap of 3 attempts** per function before the methodology forces a return to A-layer data collection (Scout phase / dynamic tracing).

Rationale: repeatedly tweaking B1 hypotheses (Lift code) without new A-layer data (traces) is the definition of process entropy (实践偏离:过程熵增). The cap breaks this cycle by refusing to let B1 iterate in isolation.

### 9.5 Degraded Mode Honesty Statement

When operating in Partial or Degraded mode, tools and exports MUST prefix their output with:

> "以下验证结果基于降级模式（[部分/降级]）。置信度未自动提升。所有 test anchor 均记录了数据来源，但尚未通过可公共观测的实践检验。confirmed 状态需要人工对照 trace 证据后手动授予。"

This is not defensive — it is an honest declaration of the current verification ceiling. The protocol remains useful: anchors document hypotheses with provenance, noise cards accumulate known failures, and the structure preserves everything needed for full verification when A-layer conditions permit.

---

## 10. Versioning

- Protocol versions are `v{major}.{minor}`.
- Minor version changes MUST be backward-compatible (old noise cards remain readable).
- Current version: **v0.5** — pre-stable. All components subject to change based on practice feedback.

---

> "This specification is a working hypothesis. Its truth will be determined not by argument, but by whether it produces more reliable code in practice. The source provenance requirement (v0.3) is a wager: that requiring test data to carry its A-layer origin will break the circular reasoning that makes AI-generated code verification unfalsifiable. The wager will be settled not in this document, but in real RE projects."
>
> — First Law, Applied Reflexively

---

## 11. Universal Claim Audit (v0.4)

Per [§0](#0-key-words-and-universal-quantifier-discipline), every universal claim is audited here. Claims without verification evidence are qualified to their current scope.

| Claim | Location | Verification | Status |
|-------|----------|-------------|--------|
| "Anchors MUST be removable by deleting a single dependency" | §2.4 | Python stub tested; TS/C++ comment-form inert by construction; Rust **not implemented** | ⚠️ scoped (Rust pending) |
| "Every public function MUST have ≥1 anchor" | §5.1 | P3 enforced in Python scanner (unit-tested); TS/C++ pending | ⚠️ scoped to Python |
| "I/O functions MUST be INFO, pure functions WARNING" | §6.1 | Python scanner severity layering verified by tests (v0.4 fix) | ✅ verified |
| "Scanner: 0 false positives" | §8 | photo_screener: 38 findings 0 FP — **single-run evidence** | ⚠️ single-run |
| "90-day staleness MUST escalate" | §5.3 | `created_at`-based escalation implemented; **"function modified since anchor" detection NOT implemented** | ⚠️ partial |
| "Noise cards remain readable across minor versions" | §10 | `from_dict` backward-compat tested | ✅ verified |
| "Each skill MUST cover exactly one protocol action" | §14.1 | Manifest conformance tests (v0.5) check structural properties; single-responsibility is a normative clause | ⚠️ scoped (reference implementation) |
| "Skills MUST operate via CLI, never internal imports" | §14.4 | Reference implementation bodies contain no `import anchorlaw` guidance (sole exception: `create_noise_card` runtime hook); CLI commands only | ⚠️ scoped (reference implementation) |
| "Skill bodies MUST NOT copy protocol rule text" | §14.1 | Reference implementation bodies reference protocol §N lines instead of quoting rules | ⚠️ scoped (reference implementation) |
| "Severity layering applies in all implementations" | §6.3 | Severity layering unit-tested in Python scanner; TS/C++ mapping pending | ⚠️ scoped (Python verified) |
| "Uninstalled skills MUST have zero effect on agent context" | §14.3 | Manifest conformance tests only load installed files; uninstalled-file check is a structural guarantee of the reference layout | ⚠️ scoped (reference implementation) |
| "Every operational command in a skill body MUST be a CLI subcommand" | §14.4 | Reference implementation command lines are `anchorlaw`/`anchorlaw-scanner` invocations; sole exception `create_noise_card` | ⚠️ scoped (reference implementation) |

---

## 12. Rule Challenge Process (Third Law, v0.4)

A rule (scanner pattern, severity assignment, or protocol clause) that produces **verified false positives** MUST be downgraded or removed. This is the protocol's self-诉讼 channel — the answer to "how do we overturn a rule?"

1. **Report** — File an issue with a minimal reproduction case (code snippet + scanner output).
2. **Verify** — A maintainer reproduces the FP. The repro case is added to the scanner test suite as a regression test (marked as a known-FP exclusion so the pattern is not re-added blindly).
3. **Adjudicate** — The rule is either (a) refined to exclude the case, (b) downgraded in severity, or (c) removed from the catalog. The rationale MUST be recorded in the protocol changelog.
4. **Evidence requirement** — A rule without FP evidence cannot be weakened; a rule with confirmed FPs cannot be kept unchanged.

---

## 13. Protocol Generality: Anchor Abstraction (v0.4)

Anchorlaw is a **language-agnostic protocol**. An anchor is defined by two orthogonal properties, independent of any language's syntax:

| Property | Python | TypeScript | C++ |
|----------|--------|-----------|-----|
| **Declaration site** — where the anchor attaches to code | decorator | JSDoc comment | line comment (`// @anchor.*`) |
| **Validation carrier** — what executes the check | `test_fn` lambda | runtime assert | independent probe binary |
| **Removal** — behavior without the protocol | no-op decorator | inert comment | inert comment |

Implementations MUST follow:
- The declaration site MUST be removable/inert without code modification beyond deleting the dependency (or, for comment form, nothing at all).
- The validation carrier MAY differ per language — what matters is that the claim is executable in finite steps with observable results (First Law).
- `@anchor.test` requires a `source` field (validation carrier reference) in all languages; `@anchor.idk` does not.
- Scanner patterns (P1-P6) are defined language-agnostically; each implementation maps them to its language's syntax (e.g. `except:` in Python ↔ `catch (...)` in C++).

The C++ form was validated against a real header-inline project (CoreSwap, `density.h`, 842 lines): annotations extracted correctly, zero false positives.

---

## 14. Agent Skills: Anchor Skill Manifest (v0.5)

> **Trigger for this section:** Anchorlaw's practical efficacy was limited not by
> its rules but by **agent-side attention dilution** — the full protocol (13
> sections) and project instructions were carried in agent context in full,
> consuming attention that belonged to the code itself. Users also need only
> subsets of the protocol (testing only, review only). The protocol knowledge
> layer is therefore restructured into a **skill manifest**: compact,
> single-responsibility playbooks loaded on demand, invoked only when the agent
> reaches the situation they cover.

### 14.1 Definition

An **Agent Skill** (hereafter "skill") is a playbook that guides an AI agent
through **exactly one** protocol action. It is the behavior-layer counterpart of
an anchor: where [§13](#13-protocol-generality-anchor-abstraction-v04) defines
the *declaration site* and *validation carrier* of a claim, a skill defines the
*trigger* and *procedure* of a protocol action.

A skill MUST be defined by exactly these properties:

| Property | Requirement |
|----------|-------------|
| **name** | `anchor.<verb>` — stable identifier, unique across the manifest |
| **layer** | One of L0–L4 (see [14.2](#142-layer-model)) |
| **single responsibility** | The skill MUST cover exactly one protocol action. A skill covering two actions MUST be split. |
| **trigger** | The concrete situation in which an agent SHOULD invoke the skill |
| **inputs** | What the agent needs to start (paths, function names, CLI flags) |
| **outputs** | What the agent produces (anchors added, scan report, noise card, ...) |
| **body** | Step-by-step procedure. MUST reference protocol sections as the single source of truth and MUST NOT copy rule text into the body (copying creates knowledge drift). |

### 14.2 Layer Model

Skill layers map onto the [Implementation Compliance Levels (§7)](#7-implementation-compliance-levels) for L0–L3, with an additional maintain layer for the protocol's own repository:

| Layer | Maps to | Skills |
|-------|---------|--------|
| **L0 — Concepts** | protocol foundation (§5, §13) | `anchor.concepts` |
| **L1 — Scanner** | Level 1 (P1–P6) | `anchor.scan`, `anchor.challenge` |
| **L2 — Anchors** | Level 2 (anchor system, incl. §9 degraded verification) | `anchor.write`, `anchor.test`, `anchor.degrade` |
| **L3 — Noise** | Level 3 (noise cards) | `anchor.noise` |
| **L4 — Maintain** | protocol maintenance | `anchor.maintain` |

**Dependency direction:** a skill MAY reference skills in the same or a lower
layer; it MUST NOT reference skills in a higher layer. Sole exception: L0
(`anchor.concepts`) is the semantic index referenced by all layers and MAY
point onward to skills in any layer.

### 14.3 Modularity

- Each skill MUST be independently installable and removable. A user who only
  needs testing installs L0 + `anchor.test`; nothing else is loaded. (This
  extends the Uninstall Guarantee (§2) to the agent side: protocol capability
  MUST be removable without leaving behavioral residue.)
- Uninstalled skills MUST have zero effect on agent context (no index line, no body).
- Each skill's one-line index description SHOULD fit the host platform's index
  budget — the Reasonix reference enforces ≤120 characters per index line.

### 14.4 CLI Binding Contract

> **The CLI is the only operational entry point for agents.**

- Skill bodies MUST instruct the agent to operate through the CLI
  (`anchorlaw ...`, `anchorlaw-scanner ...`), never through internal library imports.
- Rationale: the library API surface (`__init__.py` exports ~27 names across
  anchors/scanner/noise) would dilute agent attention exactly as the full
  protocol text did. The argparse subcommand surface is already modular — one
  subcommand per action — and is the minimal attention footprint.
- Consequence: skill bodies MUST NOT contain `import anchorlaw` guidance.
  Every operational command in a skill body MUST be a CLI subcommand.
- **Sole exception:** `create_noise_card` (noise card creation) is a runtime
  hook with no CLI entry — a noise skill body MAY show this one in-code usage
  (e.g. inside an `except` block where the failure is observed), and MUST keep
  all other operations CLI-only.

### 14.5 Relationship to AI Context Format (§4)

[§4](#4-ai-context-format) exports protocol **state** (anchor health, noise
cards) as data for LLM consumption. Skills are **behavior**: they tell the agent
when and how to perform a protocol action. State and behavior are orthogonal —
a skill body MUST NOT embed state exports, and §4 exports MUST NOT embed procedures.

### 14.6 Skill Catalog (v0.5)

| Skill | Layer | Single responsibility | Trigger (SHOULD invoke when) | CLI entry |
|-------|-------|----------------------|------------------------------|-----------|
| `anchor.concepts` | L0 | Anchor semantics quick-reference (test/idk/source/staleness/health) | agent needs anchor semantics before writing or auditing anchors | — (reference only) |
| `anchor.scan` | L1 | Static review: run scanner, triage P1–P6 findings by severity | after modifying code, before commit; or on a defensive-pattern report | `anchorlaw-scanner check <dir>` |
| `anchor.challenge` | L1 | Rule challenge workflow (§12) | scanner produced a suspected false positive | file an issue with repro |
| `anchor.write` | L2 | Write `@anchor.test` / `@anchor.idk` annotations with valid source provenance | after implementing or refactoring a public function | — (source edit) |
| `anchor.test` | L2 | Run anchor validation and triage results | after adding anchors; on CI failure | `anchorlaw test [--module M]` |
| `anchor.noise` | L3 | Noise card creation, resolution, search | a runtime failure was observed; or unresolved-card backlog exists | `anchorlaw noise list/search/resolve` |
| `anchor.degrade` | L2 | Degraded verification (§9): mode classification, uncompilable registry, retry cap | code cannot be independently compiled (RE-lifted code); `anchorlaw test` reports `uncompilable` | `anchorlaw test` + manual classification |
| `anchor.maintain` | L4 | Protocol maintenance workflow (changelog / maturity / audit / tests / commit) | working inside the Anchorlaw repository itself | — (repo workflow) |

`anchor.maintain` MAY be limited to the protocol's own repository. External
users install L0 plus the L1–L3 subset they need; unused skills have zero
context cost.
