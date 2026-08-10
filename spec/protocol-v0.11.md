# Anchorlaw Protocol v0.11

> **语言无关的代码验证协议规范**
>
> "任何声称都必须有可验证的实践锚点。"
>
> Status: **Working Draft**. Components are at different maturity levels — see [Maturity](#maturity).
>
> v0.11: input-contract boundary — requirements discovery is REMOVED from
> Anchorlaw. The protocol now covers only the programming-execution part:
> a four-stage Judge-driven pipeline (input contract → implementation spec →
> plan → parallel implementation → delivery). Requirements discovery belongs
> to a separate requirements protocol (Scout-driven, human-dialogue based,
> Judge does technical review); its output — confirmed requirements +
> software specification — is Anchorlaw's stage-0 input contract. The human
> authorization gate moved out with it (§16.1: one confirm point left, the
> delivery `confirmed` grant; the host handover IS the implementation
> authorization). Scout narrows to spec drafting. Three-protocol closure:
> requirements protocol → Anchorlaw → RE framework (reverse-engineering
> exploration calls Anchorlaw for its determined implementation work).
>
> v0.10: Judge-driven programming — programming is not reverse engineering:
> the workflow is restructured from "write first, review at the end" (v0.8
> convergence-gate) into a six-stage Judge-driven pipeline (§15.1):
> requirements discovery (Judge↔Scout) → human authorization gate →
> implementation spec → plan → parallel Worker implementation (Judge nod per
> module) → delivery (isolated judge acceptance). Acceptance criteria are
> determined before implementation and submitted to the human with the
> requirements (§15.4). The v0.9 "3-round cap" is replaced by Judge-nod
> termination: criteria satisfied = done; unmet criteria escalate to the human
> (§12 or amendment). Scout/Worker roles, removed in v0.8, are reinstated as
> general-protocol programming roles (not RE-derived). The main session
> embodies the Judge role; isolated judge subprocesses perform key-checkpoint
> acceptance.
>
> v0.9: judge institutionalization + verification termination gates —
> the review gate is a mandatory checkpoint at specific decision points,
> not only a closing gate. `confirmed` requires a prior judge opinion;
> major redirections (case reopening, root-cause determination, scope
> decisions) require judge review; self-review does not constitute the
> review gate; plans must pre-place judge steps at trigger points;
> the convergence gate terminates on mechanical criteria — external test
> set, three-tier review opinions (blocking limited to mechanical
> criteria), and a verification round cap (§15.4).
>
> v0.8: convergence-gate model — programming is linear convergence: the main
> agent holds full context and writes; the only sanctioned subagent role is
> the review gate (judge). Execution-mode selection principle added (§15.3):
> convergent tasks default to `inline`, divergent tasks MAY use `subprocess`.
> `anchor.write`/`anchor.test` are `inline`. Reverse-engineering terminology
> removed from the current-version surface (Lift→Verify, A-layer/B1, RE-only
> roles); CoreSwap is kept as first-host practice evidence, described in
> language-agnostic terms.
>
> v0.7: first-host practice feedback absorbed — CoreSwap 8576-24blocks task
> (2026-08-08) exercised the execution topology and produced five protocol
> patches: source artifact requirement (§5.5, incl. new `probe` source type),
> retry-cap scope clarification (§9.4), verification executor separation
> (§9.6), order-dependent semantic equivalence (§13), and judge three-source
> review baseline (§15.4).
>
> v0.6: completed the four-layer interface surface — added Agent Execution
> Topology (§15, execution isolation with skill coupling) and the Host
> Integration Contract (§16, hosts implement interface points without
> restructuring their own framework). Interface-surface audit (§15.5).
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

## Changelog from v0.10

| Change | Trigger | Section |
|--------|---------|---------|
| **Requirements discovery removed — input contract added** — the six-stage pipeline is cut to four stages (input contract → spec → plan → parallel implementation → delivery); Anchorlaw consumes already-confirmed requirements + software specification from an external requirements protocol and never re-discovers requirements | user structural insight: requirements discovery is exploratory and human-dialogue based — a subagent Scout cannot talk to the human, so it must live in a separate protocol (Scout-driven, Judge technical review); forcing it into the Judge-driven execution pipeline inverted the structure | [§15.1](#151-definition) |
| **Human authorization gate moved out** — requirements confirmation happens in the requirements protocol; the host handover of confirmed requirements IS the implementation authorization; confirm hook is single-point inside Anchorlaw (delivery `confirmed`) | same insight: the gate was an artifact of in-protocol requirements discovery | [§16.1](#161-definition) |
| **Acceptance criteria derived from input contract** — criteria-first retained, but criteria derive from the external input, not from in-protocol discovery | corollary of the input contract | [§15.4](#154-consistency-contract) |
| **Scout narrowed to spec drafting** — requirements analysis is no longer a Scout duty | input contract removes the requirements-analysis role | [§15.1](#151-definition), [§15.3](#153-skill-execution-coupling) |
| **Three-protocol closure** — requirements protocol → Anchorlaw → RE framework; Anchorlaw is the programming-execution layer callable by both | business-logic closure: each framework owns one phase (discover → implement/verify → reverse-explore) | [§15](#15-agent-execution-topology-v06), [§16](#16-host-integration-contract-v06) |
| **Version bump** v0.10 → v0.11 | input-contract boundary | [§10](#10-versioning) |

## Changelog from v0.9

| Change | Trigger | Section |
|--------|---------|---------|
| **Judge-driven pipeline** — programming restructured into a six-stage pipeline (requirements discovery → human authorization gate → implementation spec → plan → parallel implementation → delivery); every stage terminates on the Judge's nod | user paradigm insight: the v0.9 review loop was patched (round cap) instead of fixed — review-at-the-end is the reverse of how programming converges; programming is constructive and Judge-driven, not exploratory like reverse engineering | [§15.1](#151-definition) |
| **Human authorization gate** — the Judge MUST submit the complete requirements document + acceptance criteria to the human; implementation MUST NOT begin before human confirmation | user decision: the requirements→implementation boundary is an authorization point, not a recommendation | [§15.1](#151-definition), [§16.1](#161-definition) |
| **Acceptance criteria first** — criteria determined during requirements discovery, before implementation; review opinions judged against them | TDD-style corollary of the Judge-driven model | [§15.4](#154-consistency-contract) |
| **Judge-nod termination replaces the 3-round cap** — criteria satisfied = done; unmet criteria escalate to the human (§12 or amendment) | the round cap patched a symptom; criteria-first removes the cause | [§15.4](#154-consistency-contract) |
| **Scout/Worker reinstated as general-protocol roles** — removed in v0.8 as RE-derived, reinstated in v0.10 as programming-pipeline roles (requirements analysis / module implementation) | the v0.8 removal conflated RE-scoped exploration with general programming execution; the six-stage pipeline needs them | [§15.1](#151-definition) |
| **Key-checkpoint isolated acceptance** — module integration and delivery MUST be preceded by an isolated judge subprocess verdict | "self-review ≠ review gate" instantiated at the two highest-risk checkpoints | [§15.4](#154-consistency-contract) |
| **Version bump** v0.9 → v0.10 | Judge-driven programming model | [§10](#10-versioning) |

## Changelog from v0.8

| Change | Trigger | Section |
|--------|---------|---------|
| **Judge trigger points** — review gate is a mandatory checkpoint: `confirmed` requires a prior judge opinion; major redirections (case reopening, root-cause determination, scope decisions) MUST be judge-reviewed; stage-conclusion promotion to `candidate` SHOULD be judge-reviewed | cross-project practice review: judge was absent because nothing forced it — the main agent self-assessed, presented to the human, and `confirmed` was granted without any independent review; the review gate only existed as a closing step and was skipped | [§15.4](#154-consistency-contract) |
| **Self-review ≠ review gate** — producer self-check is evidence, not review; the review gate MUST be performed by an independent reviewer (isolated subprocess or external human) | same review: "the main agent wrote and verified it" was being treated as the review itself | [§15.4](#154-consistency-contract) |
| **Plan-time judge placement** — workflow plans MUST pre-place judge steps at trigger points, not add them after the fact | same review: judge was only added when the user reminded the agent — it must be a planned step, not a reactive one | [§15.4](#154-consistency-contract) |
| **Version bump** v0.8 → v0.9 | judge institutionalization (normative review-gate obligations) | [§10](#10-versioning) |
| **Verification termination gates** — convergence gate terminates on mechanical criteria: external test set (no in-place test additions), three-tier review opinions (blocking limited to test failure / compile failure / claim-vs-implementation contradiction), verification round cap (3 rounds, counted in the plan), evidence-conflict channel via §12 | v0.9 practice review: the main agent ran endless review rounds on non-blocking opinions, added a self-imposed assertion outside the approved plan, and burned 30+ minutes on a single encoding false positive — the very failure mode the gates exist to prevent | [§15.4](#154-consistency-contract) |

## Changelog from v0.7

| Change | Trigger | Section |
|--------|---------|---------|
| **Convergence-gate model** — programming is linear convergence; the main agent writes with full context; the only sanctioned subagent role is the review gate | practice finding: subagent-izing writing/verification fragments context and breaks linear convergence — programming needs convergence, subagents diverge | [§14.6](#146-skill-catalog-v06), [§15.3](#153-skill-execution-coupling) |
| **Execution-mode selection principle** — convergent tasks (writing, verification, single-threaded progress) default to `inline`; divergent tasks (survey, multi-hypothesis, large scans) MAY use `subprocess` | same finding: subprocess was being treated as the default for all actions; it is a divergent-work optimization, not a programming default | [§15.3](#153-skill-execution-coupling) |
| **`anchor.write` / `anchor.test` are `inline`** — the main agent writes annotations and runs verification itself | same finding: writing and verifying are convergent actions | [§14.6](#146-skill-catalog-v06) |
| **Reference roles reduced to judge** — `anchor.scout`/`anchor.worker` removed from the reference implementation; hosts MAY supply their own executors per §16 | RE-derived roles are not general-protocol content; hosts implement interface points instead of inheriting workflow roles | [§15](#15-agent-execution-topology-v06) |
| **Reverse-engineering terminology removed from the current-version surface** — `Lift→Verify` → implement→verify, `A-layer`/`B1` → data-layer/hypothesis, RE-only roles/scenes removed; CoreSwap kept as first-host evidence in language-agnostic terms | Anchorlaw borrows mechanisms, not identity: the protocol is language-agnostic, not RE-scoped | throughout |
| **Version bump** v0.7 → v0.8 | convergence-gate model + de-RE surface | [§10](#10-versioning) |

## Changelog from v0.6

| Change | Trigger | Section |
|--------|---------|---------|
| **Source artifact requirement + `probe` source type** — `source` MUST have an on-disk evidence artifact (command + output summary in `.investigations/`/`.artifacts/`); scan gate checks existence (WARN); `probe:<binary>!<entry>#<id>` added as a source type | CoreSwap 8576-24blocks: judge challenged "did the probe actually run?" — source was format-valid but no mechanism required the verification record to be findable; `probe:` was in practice but undefined in §5.5 | [§5.5](#55-source-provenance-v03) |
| **Retry-cap scope clarification** — the 3-attempt cap counts *hypothesis verification rounds*, NOT engineering bug fixes | CoreSwap SearchTree port: 3 iterations all crashed (null pointer → C++ exception → MSVC long 32-bit truncation), all engineering fixes — miscounting the cap would force abandoning a fixable port | [§9.4](#94-retry-cap-anti-entropy) |
| **Verification executor separation** — analysis (static) and verification (runtime, tool-requiring) may be performed by different executors; layered labels reflect actual execution; handoff = command template + criteria → executor runs + persists raw output → analyst interprets | CoreSwap: analysis subagent sandbox could not run block_probe/gradle; runtime verification was done by the main session | [§9.6](#96-verification-executor-separation-v07) |
| **Order-dependent semantic equivalence** — result equivalence is insufficient for order-dependent semantics (tie-break, cache order, traversal order, query-sequence dependence) | CoreSwap biome tie-break: C++ linear find `<` picks forest, vanilla SearchTree tree-order picks badlands; Java `previousResultNode` cache makes tie results depend on query sequence — static result-equivalence check cannot detect it | [§13](#13-protocol-generality-anchor-abstraction-v04) |
| **Judge three-source review baseline** — review MUST cross-check artifact snapshot vs git HEAD/working-tree diff vs verification records; working tree wins | CoreSwap judge read only the `.artifacts` snapshot and mis-reported "32-bit unfixed" after the 64-bit fix was applied by the main session | [§15.4](#154-consistency-contract) |
| **Version bump** v0.6 → v0.7 | five normative patches from first-host practice | [§10](#10-versioning) |

## Changelog from v0.6 (post-release fixes)

| Change | Trigger | Section |
|--------|---------|---------|
| **Source provenance implemented** — `@anchor.test`/`@anchor.idk` accept `source`; test anchors with missing/static source are INVALID (queryable, not crashing) | third-party engineering assessment: §5.5 was paper-only — README example crashed (`TypeError: test() got an unexpected keyword argument 'source'`) | [§5.5](#55-source-provenance-v03) |
| **Stub generation fixed + naming unified** — `init` generates `anchorlaw_stub.py` from `anchorlaw_stub_template.py`; default store `.anchorlaw/`; scanner recognizes `anchorlaw_anchors.py`; docs/examples updated to `@anchor.*` | assessment: `init` silently failed (looked for `pract_stub_template.py`, Practify-rename residue); `pract_*` naming split across CLI/scanner/docs | [§2](#2-uninstall-guarantee), [§6.2](#62-registry-aware-scanning) |
| **Summarize severity fix** — `by_severity` uses `effective_severity` | assessment: I/O missing-anchor displayed INFO but was summed as WARNING | [§6.1](#61-severity-layering) |

## Changelog from v0.5

| Change | Trigger | Section |
|--------|---------|---------|
| **Agent Execution Topology** — main-session/subprocess split, artifact contract, consistency contract, skill-execution coupling | agent-side execution pollution: skills (v0.5) fix knowledge dilution but not execution-process dilution; subprocess isolation keeps the main session clean and consistent | [§15](#15-agent-execution-topology-v06) |
| **Host Integration Contract** — hosts implement interface points (execution point, artifact paths, confirm hook, trigger point) without restructuring their framework | two-way adapter friction: every host (e.g. RE-Framework) re-invented integration glue; protocol must be an installable interface, not a framework to adapt to | [§16](#16-host-integration-contract-v06) |
| **Interface-surface audit** — every protocol-facing contract classified as interface definition vs implementation detail | protocol was a spec + scattered tools, not a coherent interface surface | [§15.5](#155-interface-surface-audit) |
| **Version bump** v0.5 → v0.6 | two new normative sections (§15, §16) | [§10](#10-versioning) |

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
| **C++ support** — comment-form `@anchor.test` / `@anchor.idk` annotations | CoreSwap integration: header-inline worldgen + probe binaries | [§2.4](#24-cross-language-notes), [§13](#13-protocol-generality-anchor-abstraction-v04) |
| **Key Words (RFC 2119)** + universal quantifier discipline | unverified universal claims violate the Second Law | [§0](#0-key-words-and-universal-quantifier-discipline) |
| **Universal claim audit** — every MUST/guarantee carries evidence or is scoped | audit found 'All languages' claim exceeded Rust implementation | [§11](#11-universal-claim-audit-v04) |
| **Rule challenge process (Third Law)** — FP evidence forces rule downgrade/removal | protocol had no path to challenge its own rules | [§12](#12-rule-challenge-process-third-law-v04) |
| **Unit tests for scanner/anchors/noise** (55 tests) + CI self-scan | First Law applied reflexively: a verification protocol must verify itself | [§8](#8-maturity) |
| **Anchor execution tracking** — run_count / never_ran in health report | registered-but-never-run anchors are degraded anchors | [§5.4](#54-anchor-health-states) |
| **Severity layering actually applied** — P3 I/O functions now report INFO | implementation fixed severity to WARNING regardless of classification | [§6.1](#61-severity-layering) |

## Changelog from v0.2

| Change | Trigger | Section |
|--------|---------|---------|
| **Source provenance** — @pt anchors MUST carry source field | Practice feedback: anchors without trace provenance are unfalsifiable | [5.1 Test Anchor](#51-test-anchor), [5.5 Source Provenance](#55-source-provenance) |
| **Degraded verification** — three operating modes (full/partial/degraded) | Practice feedback: generated code often can't compile standalone | [9. Degraded Verification](#9-degraded-verification) |
| **Uncompilable anchor state** — honest declaration when code can't run | Practice feedback: binary-internal deps prevent anchorlaw test | [5.4 Anchor Health States](#54-anchor-health-states) |
| **Verify retry cap** — max 3 implement→verify cycles before going back to data collection | Practice feedback: prevent process entropy in unfalsifiable loops | [9. Degraded Verification](#9-degraded-verification) |

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
    from anchorlaw import test as _anchor_test, i_dont_know as _anchor_idk
except ImportError:
    # anchorlaw not installed — anchors silently become no-ops.
    # Code continues to run without modification.
    def _anchor_test(description, test_fn, source=""):
        return lambda f: f

    def _anchor_idk(what, source=""):
        return lambda f: f

# Public names
test = _anchor_test
i_dont_know = _anchor_idk
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
| **Runtime check** | Test anchors SHOULD be executable via `anchorlaw test`. If code cannot be independently compiled (e.g., generated code with internal binary dependencies), see [9. Degraded Verification](#9-degraded-verification). |

### 5.2 I-Don't-Know Anchor

| Property | Description |
|----------|-------------|
| **Purpose** | Honest declaration of a cognitive boundary |
| **Semantics** | "This function has edge cases I haven't verified yet. I am actively inviting practice feedback." |
| **Required fields** | `what` (specific description of what is unknown) |
| **Optional field (v0.3)** | `source` (provenance string): for deferred-verification use cases, records what static analysis prompted this unknown — F5 output, missing trace coverage, etc. Helps distinguish "I don't know because I haven't looked" from "I looked and genuinely can't determine." |
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
| `uncompilable` (v0.3) | Has anchors but code cannot be independently compiled | Anchors carry source provenance but anchorlaw test cannot execute. Verification deferred to runtime trace comparison. Common when code depends on internal binary symbols. |

### 5.5 Source Provenance (v0.3)

> **Each test anchor must answer: "Where did this data come from?"**

Without source provenance, a test anchor is unfalsifiable — it could be derived from the same hypothesis it claims to verify (circular reasoning), or fabricated entirely. Source provenance is the data-layer anchor point that breaks this circle.

**Source string format:**

```
source="<source_type>:<binary_or_file>!<function>#<id>, offset=<addr>, <key_observations> observed <ISO8601_timestamp>"
```

**Source types:**

| Type | Meaning | Allowed for @pt | Allowed for @idk |
|------|---------|:--:|:--:|
| `trace` | Dynamic debugging: register/memory snapshot from Frida/x64dbg/etc. | ✅ | ✅ |
| `memory` | Memory dump: extracted constant tables, vtables, string tables | ✅ | ✅ |
| `probe` (v0.7) | Independent probe binary: compiled test harness whose parseable output asserts the behavior (e.g. `block_probe` for biome checks) | ✅ | ✅ |
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

**Rule (v0.7): Source Artifact Requirement.** `source` MUST be more than format-valid — the verification record it references MUST be findable on disk: the command that produced it and an output summary, stored under `.investigations/` or `.artifacts/` (e.g. a `regression-record.md` entry). The scan gate MUST check existence of the referenced record (at least WARN level: when a `source` references a probe/record with no on-disk artifact, warn — do not allow a silent PASS). Scope: this requirement applies to runtime-derived sources (`trace`, `memory`, `probe`); a `static` source (allowed only for `@anchor.idk`) is an inference without a run record and is exempt.

Rationale (CoreSwap 8576-24blocks): after adding `@anchor.test(..., source="probe:block_probe!SURFBIOME#003")`, the scan validated only the format; the judge challenged "did the probe actually run?" — it had run (`-biomeDump 812 73 -337 = badlands`) but the protocol had no mechanism requiring the verification record to be persisted, so `regression-record.md` had to be written afterwards. The value of `source` is reproducibility, and reproducibility presupposes the verification record can be found.

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

This enables **out-of-line anchor files** (`anchorlaw_anchors.py`) — anchors registered on wrapper functions whose names follow the convention `_anchor_{function_name}` are associated with the target function.

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
| Anchors | ✅ | — | — | **Experimental** | photo_screener: 18/18 tests passed, 0 bugs found, 0 regressions |
| Source Provenance (v0.3) | — | — | — | **Scoped (first-host practice)** | Implemented in Python (v0.6 post-release + v0.7): `source` param accepted, INVALID when missing/static for `@anchor.test`; `probe:` type added v0.7. CoreSwap 8576-24blocks produced `probe:block_probe!SURFBIOME#003` anchors + regression records. |
| Noise Cards | ✅ | — | — | **Unverified** | 0 cards accumulated |
| AI Context | ✅ | — | — | **Conjecture** | 0 injection cycles run |
| Stub Uninstall | ✅ | ✅ (comment-form) | ✅ (comment-form) | **Verified** | Tested: delete stub + anchorlaw, code still runs via no-op fallback; comment-form inert by construction |
| Degraded Verification (v0.3) | — | — | — | **Conjecture** | Modes defined. No project beyond the reference host has exercised Partial/Degraded paths. |
| Agent Skills (v0.5) | — | — | — | **Conjecture** | §14 manifest defined. Reasonix reference implementation ships with manifest conformance tests (v0.5). No third-party agent trial yet. |
| Execution Topology (v0.6) | — | — | — | **Scoped (first-host trial)** | §15 contracts defined. CoreSwap 8576-24blocks (2026-08-08) exercised subprocess executor/judge/artifact chain; produced 5 patches (absorbed v0.7: §9.6 executor separation, §15.4 judge baseline). Reference conformance tests ship. |
| Host Integration Contract (v0.6) | — | — | — | **Scoped (first-host trial)** | §16 interface points defined. CoreSwap acted as first host; boundary clauses held (no framework restructuring). R3 (host-platform todo matching) logged for the Reasonix maintainers, outside the protocol. |
| Review Gate Institutionalization (v0.9) | — | — | — | **Conjecture** | §15.4 trigger points defined (confirmed gating, major redirections, plan-time placement) + verification termination gates (external test set, three-tier opinions, round cap); cross-project practice review evidence (judge absence cost; v0.9's own review loop consumed 30+ minutes on a non-blocking encoding false positive). No host has exercised the mandatory checkpoint yet. Conformance tests ship with v0.9. |
| Judge-Driven Pipeline (v0.10; v0.11 amended) | — | — | — | **Conjecture** | §15.1 four-stage pipeline defined (input contract → implementation spec → plan → parallel Workers → delivery); requirements discovery moved to a separate requirements protocol (Scout-driven, human-dialogue), Anchorlaw consumes its output; §15.4 acceptance-criteria-first (derived from input) + Judge-nod termination. Protocol-level design; no host has exercised the pipeline yet. Conformance tests ship with v0.11. |

---

## 9. Degraded Verification (v0.3 Draft)

> **Not all anchored code can be independently compiled and run.** This is not a failure of the protocol — it is an honest recognition that data-layer verification has material prerequisites. When those prerequisites are absent, the protocol MUST degrade gracefully rather than pretend.

### 9.1 Three Operating Modes

| Mode | Condition | anchorlaw test | Confidence auto-promotion | Anchor source requirement |
|------|----------|:---:|:---:|:---:|
| **Full** | Anchorlaw installed AND code self-contained (no unresolved external deps) | ✅ Runs | ✅ draft→candidate (see §15.4: auto-promotion MUST note the absence of independent review) | @pt MUST have trace/memory source |
| **Partial** | Anchorlaw installed BUT code has unresolved dependencies (common: generated code depends on internal binary symbols) | ❌ Cannot run | ❌ Manual only | @pt MUST still carry source — the anchor serves as documented hypothesis until runtime verification becomes possible |
| **Degraded** | Anchorlaw not installed | ❌ N/A | ❌ Manual only | Source provenance still required in _anchors.py for audit trail |

### 9.2 Self-Containment Classification

Before `anchorlaw test` is invoked, the function MUST be classified:

**Self-contained:** No calls to external functions, no global variable references, no custom types from outside the translation unit.
→ Eligible for Full mode.

**Has-deps:** Calls other functions OR references global state OR uses custom types.
→ Check dependency resolution:
  - All dependencies are themselves self-contained AND generated → merge and compile → Full mode
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
      implement_status: not_started
    - type: vtable
      name: Animal::vftable
      address: "foo.dll:0x140007000"
  suggested_path: "Implement AudioDevice::write first, then retry speak compilation"
  anchor_count: 4
  anchor_sources_valid: true  # all @pt have trace/memory source
```

### 9.4 Retry Cap (Anti-Entropy)

When Partial or Degraded mode is active, the implement→verify cycle has a **hard cap of 3 attempts** per function before the methodology forces a return to data-layer collection (dynamic tracing).

Rationale: repeatedly tweaking hypotheses (implemented code) without new data-layer evidence (traces) is the definition of process entropy (实践偏离:过程熵增). The cap breaks this cycle by refusing to let the implementation iterate in isolation.

**Scope Clarification (v0.7):** the 3-attempt cap counts **hypothesis verification rounds** — repeatedly adjusting a hypothesis (a model of *how the mechanism works*) with no new data-layer evidence (trace/probe) is process entropy and consumes the cap. **Engineering fixes do NOT consume the cap**: fixing implementation defects (compilation failures, crashes, runtime errors) may iterate indefinitely until correct. Distinguishing criterion:
- Hypothesis verification: changes the *understanding* of the mechanism; verifies whether the understanding is correct → counts toward the cap
- Engineering fix: changes an *implementation defect*; verifies whether the program runs as already-confirmed semantics → does not count

Rationale (CoreSwap 8576-24blocks): the SearchTree port (MultiNoiseUtil.SearchTree C++ version) iterated 3 versions, all crashing (null pointer → C++ exception → MSVC long 32-bit truncating INT64_MAX to -1) — every iteration was an engineering defect fix, unrelated to hypothesis verification; miscounting the cap would have forced abandoning a fixable correct port. The host human adjudicated.

### 9.5 Degraded Mode Honesty Statement

When operating in Partial or Degraded mode, tools and exports MUST prefix their output with:

> "以下验证结果基于降级模式（[部分/降级]）。置信度未自动提升。所有 test anchor 均记录了数据来源，但尚未通过可公共观测的实践检验。confirmed 状态需要人工对照 trace 证据后手动授予。"

This is not defensive — it is an honest declaration of the current verification ceiling. The protocol remains useful: anchors document hypotheses with provenance, noise cards accumulate known failures, and the structure preserves everything needed for full verification when data-layer conditions permit.

### 9.6 Verification Executor Separation (v0.7)

Analysis (static, no runtime) and verification (runtime, tool-requiring) MAY be performed by different executors — especially when an analysis subprocess sandbox has no shell or blocks executables.

1. **Layered labels reflect actual execution**: Full/Partial/Degraded describe the *actual means at verification execution time*, not the analyst's intent. An analysis artifact MUST NOT advance to `candidate` on static result-matching alone without runtime verification evidence (unless explicitly declared Degraded with an honest statement).
2. **Verification handoff**: the analyst produces a "command template + expected criteria"; the executor runs it and persists the raw output; the raw output returns to the analyst for interpretation. The executor executes but does not interpret; the analyst interprets but does not fabricate execution.
3. **Artifact chain completeness**: the handed-off command, the raw output, and the interpretation MUST reference each other under `.investigations/` / `.artifacts/`; a missing link means verification is incomplete.

Rationale (CoreSwap 8576-24blocks): the analysis subagent sandbox could not run block_probe/gradle, so all runtime verification was run by the main session. The manual flow worked (analyst produces command template → executor runs without interpreting → analyst interprets), but it relied on self-discipline and needed to be protocolized.

---

## 10. Versioning

- Protocol versions are `v{major}.{minor}`.
- Minor version changes MUST be backward-compatible (old noise cards remain readable).
- Current version: **v0.11** — pre-stable. All components subject to change based on practice feedback.

---

> "This specification is a working hypothesis. Its truth will be determined not by argument, but by whether it produces more reliable code in practice. The source provenance requirement (v0.3) is a wager: that requiring test data to carry its data-layer origin will break the circular reasoning that makes AI-generated code verification unfalsifiable. The wager will be settled not in this document, but in real projects."
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
| "Subprocess working context MUST NOT enter the main session" | §15.2 | Host-platform isolation semantics (Reasonix task/fleet); protocol normative clause | ⚠️ scoped (host capability) |
| "Subprocess MUST persist artifacts before returning" | §15.2 | Reference subprocess profiles write artifacts per contract; conformance tests check artifact schema | ⚠️ scoped (reference implementation) |
| "`confirmed` MUST be granted only by a human" | §15.4 | Consistency contract normative; reference profiles never write `confirmed` | ⚠️ scoped (reference implementation) |
| "A Host MUST NOT restructure its framework to integrate" | §16.2 | Boundary clause; no host has implemented the contract yet (Conjecture) | ⚠️ scoped (unverified) |
| "A Host MUST NOT fork Anchorlaw; use §12 challenge or new interface point" | §16.2 | Boundary clause; no challenge filed via this path yet | ⚠️ scoped (unverified) |
| "Subprocess MUST return only final answer + artifact references" | §15.2 | Reference role profiles follow this; isolation itself is host capability | ⚠️ scoped (reference implementation) |
| "Review gate MUST NOT change status directly" | §15.4 | `test_review_gate_is_opinion_only` covers the judge reference profile | ⚠️ scoped (reference implementation) |
| "Host MUST implement the four interface points" | §16.1/§16.3 | No host has implemented the contract yet (Conjecture) | ⚠️ scoped (unverified) |
| "`source` references MUST have an on-disk artifact; scan gate WARNs on missing" | §5.5 (v0.7) | Reference scanner implements the existence check; CoreSwap workflow persisted regression records | ⚠️ scoped (reference implementation + first-host practice) |
| "Retry cap counts hypothesis rounds, not engineering fixes" | §9.4 (v0.7) | CoreSwap SearchTree port (3 crash iterations, all engineering) adjudicated by host human | ⚠️ scoped (first-host practice) |
| "Verification executor separation: layered labels reflect actual execution" | §9.6 (v0.7) | CoreSwap analysis subagent sandbox lacked shell; main session executed | ⚠️ scoped (first-host practice) |
| "Order-dependent semantics MUST be explicitly annotated/verified" | §13 (v0.7) | CoreSwap biome tie-break: static result-equivalence missed forest-vs-badlands | ⚠️ scoped (first-host practice) |
| "Convergent tasks (writing, verification) default to `inline`; the main agent writes with full context" | §15.3 (v0.8) | Execution-mode selection principle; **superseded in v0.10** — the main session holds the acceptance criteria and adjudicates, while module code is produced by parallel Workers under an approved spec | ⚠️ superseded (v0.10) |
| "The only sanctioned reference subagent role is the review gate (judge)" | §15 (v0.8) | `anchor.scout`/`anchor.worker` removed in v0.8 as RE-derived; **reinstated in v0.10** as general-protocol programming roles (Scout = requirements analysis/spec drafting, Worker = module implementation); `anchor.judge` remains kind:role, now dual-use (driver + isolated acceptance) | ⚠️ superseded (v0.10) |
| "Judge MUST cross-check artifact snapshot vs git diff vs verification records" | §15.4 (v0.7) | CoreSwap stale-snapshot mis-report ("32-bit unfixed") after main-session fix | ⚠️ scoped (first-host practice) |
| "`confirmed` MUST be granted only after a judge review opinion exists for the artifact" | §15.4 (v0.9) | Normative clause (trigger points); reference profile never writes `confirmed`; no host exercised the gating yet | ⚠️ scoped (unverified) |
| "Major redirections (case reopening, root-cause determination, significant scope decisions) MUST be judge-reviewed" | §15.4 (v0.9) | Normative clause (trigger points); triggered by cross-project practice review — judge absence let a wrong direction persist to phase 13 | ⚠️ scoped (unverified) |
| "Producer self-review does NOT constitute the review gate; the review gate MUST be independent" | §15.4 (v0.9) | Normative clause; "the main agent wrote and verified it" was being treated as review itself | ⚠️ scoped (unverified) |
| "Auto-promoted `candidate` (Full mode) MUST note the absence of independent review" | §15.4/§9.1 (v0.9) | Normative clause (self-review ≠ review gate, path b); consistent with the state machine's two-path `candidate` row | ⚠️ scoped (unverified) |
| "Workflow plans MUST pre-place judge steps at trigger points" | §15.4 (v0.9) | Normative clause; judge was only added when the user reminded the agent — must be a planned step | ⚠️ scoped (unverified) |
| "Verification terminates on the external test set; producers MUST NOT add tests in place during verification" | §15.4 (v0.9) | Normative clause (termination gates, A); practiced in the v0.9 patch itself — the self-imposed §11 assertion was dropped instead of kept as an expanded gate | ⚠️ scoped (unverified) |
| "Review opinions have exactly three tiers; only blocking (test failure / compile failure / claim-vs-implementation contradiction) blocks commit" | §15.4 (v0.9) | Normative clause (termination gates, B); encoding false positive was classified info and excluded after byte-level check | ⚠️ scoped (unverified) |
| "Verification rounds on one issue are capped at 3, counted in the plan; round 4 MUST escalate to the human" | §15.4 (v0.9) | Normative clause (termination gates, C); **superseded in v0.10 by Judge-nod termination** — criteria satisfied = done; unmet criteria escalate to the human via §12 or amendment | ⚠️ superseded (v0.10) |
| "Evidence conflicts resolve via §12 or recorded exclusion — never by re-entering the verification loop" | §15.4 (v0.9) | Normative clause (termination gates, E); reuses the existing §12 channel, no parallel rule created | ⚠️ scoped (unverified) |
| "Programming is Judge-driven: a four-stage pipeline (spec → plan → parallel implementation → delivery) terminates per stage on the Judge's nod" | §15.1 (v0.10; v0.11 amended) | Normative clause (pipeline model); v0.11 cut the six-stage model — requirements discovery moved to a separate requirements protocol, Anchorlaw consumes its output as input contract; no host has exercised it yet | ⚠️ scoped (unverified) |
| "Implementation MUST NOT begin before the human confirms the requirements at the human authorization gate" | §15.1/§16.1 (v0.10) | **Superseded in v0.11** — the human authorization gate moved into the external requirements protocol; Anchorlaw's stage 0 input contract is already-confirmed requirements, no re-confirmation inside Anchorlaw | ⚠️ superseded (v0.11) |
| "The Judge derives acceptance criteria from the input contract (confirmed requirements + software specification) before implementation begins" | §15.4 (v0.10; v0.11 amended) | Normative clause (acceptance criteria first); v0.11 amended — criteria derive from the external input, not from in-protocol requirements discovery | ⚠️ scoped (unverified) |
| "The pipeline terminates on the Judge's nod (criteria satisfied), not on round counting; a criterion unmet across iterations MUST escalate to the human (§12 challenge or amendment)" | §15.4 (v0.10) | Normative clause (Judge-nod termination, C; replaces the v0.9 3-round cap) | ⚠️ scoped (unverified) |
| "Module integration (stage 3) and delivery (stage 4) MUST be preceded by an isolated judge subprocess acceptance" | §15.4 (v0.10; v0.11 amended) | Normative clause (key-checkpoint isolated acceptance); stage numbers updated for the four-stage pipeline | ⚠️ scoped (unverified) |
| "Scout (spec drafting) and Worker (module implementation) are subprocess roles; their working context MUST NOT enter the main session" | §15.1/§15.2 (v0.10; v0.11 amended) | Normative clause (role definition); v0.11 narrowed Scout to spec drafting — requirements analysis is external | ⚠️ scoped (host capability) |
| "Anchorlaw consumes a confirmed requirements document + software specification as its input contract; requirements discovery is external (a separate requirements protocol)" | §15.1 (v0.11) | Normative clause (input contract, stage 0); no host has exercised the handover yet | ⚠️ scoped (unverified) |

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

**Order-dependent semantic equivalence (v0.7):** three-language equivalence by default verifies *result equivalence* (same input → same output). For **order-dependent semantics** (tie-break, cache-hit order, traversal order, query-sequence dependence), result equivalence is insufficient to prove semantic equivalence.

Restored points (P1 or above) involving ordering/caching/tie-break/traversal MUST:

1. Explicitly annotate the order-dependence in the `@anchor` description (e.g. "tie-break takes the tree-order-first entry")
2. Verify **determinism**: repeated runs with the same input produce stable results
3. Verify **query-sequence alignment**: if the reference implementation's result depends on the call sequence (e.g. Java `ThreadLocal` `previousResultNode` cache, fixed traversal order in `populateBiomes`), the C++ implementation MUST replicate that sequence or prove the result is sequence-independent

Rationale (CoreSwap 8576-24blocks): the biome tie-break — C++ linear `find` with strict `<` picks the first entry (forest), while vanilla `MultiNoiseUtil.SearchTree` tree-order traversal picks badlands (and the Java `previousResultNode` cache makes the tie result depend on the query sequence). Static result-equivalence matching (same point, 6-dimension bit-identical) could not detect this difference; tie semantics and query sequence must be verified explicitly.

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
| **execution mode** (v0.6) | `inline` or `subprocess` (default `inline`). `inline`: the skill is loaded and executed in the main session (convergent actions, lightweight knowledge/management). `subprocess`: the skill body is the operating manual for an isolated subprocess — the main session receives only the final answer and artifact references (see [§15.3](#153-skill-execution-coupling)). Selection principle (v0.8): convergent tasks default to `inline`; divergent tasks MAY use `subprocess`. |

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

### 14.6 Skill Catalog (v0.6)

| Skill | Layer | Execution | Single responsibility | Trigger (SHOULD invoke when) | CLI entry |
|-------|-------|-----------|----------------------|------------------------------|-----------|
| `anchor.concepts` | L0 | inline | Anchor semantics quick-reference (test/idk/source/staleness/health) | agent needs anchor semantics before writing or auditing anchors | — (reference only) |
| `anchor.scan` | L1 | subprocess | Static review: run scanner, triage P1–P6 findings by severity | after modifying code, before commit; or on a defensive-pattern report | `anchorlaw-scanner check <dir>` |
| `anchor.challenge` | L1 | inline | Rule challenge workflow (§12) | scanner produced a suspected false positive | file an issue with repro |
| `anchor.write` | L2 | inline | Write `@anchor.test` / `@anchor.idk` annotations with valid source provenance | after implementing or refactoring a public function | — (source edit) |
| `anchor.test` | L2 | inline | Run anchor validation and triage results | after adding anchors; on CI failure | `anchorlaw test [--module M]` |
| `anchor.noise` | L3 | inline | Noise card creation, resolution, search | a runtime failure was observed; or unresolved-card backlog exists | `anchorlaw noise list/search/resolve` |
| `anchor.degrade` | L2 | subprocess | Degraded verification (§9): mode classification, uncompilable registry, retry cap | code cannot be independently compiled (generated code with internal binary deps); `anchorlaw test` reports `uncompilable` | `anchorlaw test` + manual classification |
| `anchor.maintain` | L4 | inline | Protocol maintenance workflow (changelog / maturity / audit / tests / commit) | working inside the Anchorlaw repository itself | — (repo workflow) |

`anchor.maintain` MAY be limited to the protocol's own repository. External
users install L0 plus the L1–L3 subset they need; unused skills have zero
context cost. `subprocess` execution is a SHOULD (run it in an isolated
subprocess when the host supports one); `inline` is always permitted.

---

## 15. Agent Execution Topology (v0.6)

> **Trigger for this section:** skills (v0.5) solved *knowledge* dilution —
> the agent no longer carries the full protocol in context. But *execution*
> dilution remained: heavyweight work (scanning, analysis, verification)
> ran inside the main session, polluting its context with process detail.
> This section defines the **execution isolation contract**: the main session
> decides, subprocesses execute, artifacts persist, and a consistency
> contract keeps the whole pipeline trustworthy. Skills pair with execution:
> a `subprocess` skill is the operating manual loaded *inside* the subprocess.

### 15.1 Definition

| Concept | Role | Isolation property |
|---------|------|-------------------|
| **Main session (orchestrator)** | Decides, dispatches, adjudicates; embodies the **Judge** role (v0.10) | Receives only final answers + artifact references, never the subprocess's working context |
| **Judge** (role of the main session) | Holds the acceptance criteria; drives the pipeline (input contract → spec → plan → integration → delivery); dispatches Scouts/Workers; adjudicates their outputs; grants or denies integration | Main-session context; at key checkpoints (module integration, delivery) MUST delegate independent verification to an isolated judge subprocess — self-review is not review ([§15.4](#154-consistency-contract)) |
| **Scout** (subprocess) | Spec drafting: drafts implementation specs (naming conventions, modularization, framework boundaries) per the confirmed requirements input; requirements discovery is external (a separate requirements protocol), NOT a Scout duty here | Its full working context MUST NOT enter the main session; only the final answer and artifact references return |
| **Worker** (subprocess) | Module implementation: writes code for one module per the approved spec and plan; self-tests; persists artifacts; submits an integration request to the Judge | Same isolation as Scout; working context stays in the subprocess; code lands in the declared module path, verification records land in `.artifacts/` |
| **Artifact** | Persisted, structured output of a subprocess | Written to the artifact store (default `.artifacts/`), addressable via the main index; never kept only in conversation |
| **Consistency contract** | Trust mechanism for subprocess output | Confidence state machine + judge review + acceptance criteria (see [§15.4](#154-consistency-contract)) |

**Judge-driven pipeline (v0.10; v0.11 amended)** — programming is not reverse
engineering: reverse engineering is exploratory (survey → discovery →
convergence, unbounded verification is its nature), while programming is
constructive — it converges on pre-defined acceptance criteria. The workflow
is therefore **Judge-driven**. Requirements discovery is NOT part of this
protocol: it belongs to a separate requirements protocol (Scout-driven,
human-dialogue based), whose output — a confirmed requirements document and
software specification — is this pipeline's **input contract**. Anchorlaw
consumes the external input and never re-discovers requirements. The pipeline
has four stages, each terminating on a "Judge nod", not on round counting:

0. **Input contract** — the confirmed requirements document + software
   specification arrive from the external requirements protocol (host
   handover, [§16.1](#161-definition)); the Judge derives the acceptance
   criteria from this input before implementation begins ([§15.4](#154-consistency-contract)
   Acceptance criteria first). No implementation work may start without this
   input.
1. **Implementation spec** — the Judge dispatches Scouts (or Workers) to
   draft the implementation spec: naming conventions, modularization,
   framework boundaries. The Judge reviews the spec; only an approved spec
   enters planning.
2. **Implementation plan** — the Judge derives the module breakdown and the
   execution plan from the approved spec.
3. **Parallel implementation** — multiple Workers implement modules in
   parallel per the plan (spec lock-in makes parallelism safe). Each Worker's
   output is submitted back to the Judge: approved → integrated; rejected →
   returned to the Worker with the review opinion until the Judge approves.
4. **Delivery** — when all modules are integrated, the Judge performs the
   final review; delivery happens only after the Judge confirms no issues
   remain. An isolated judge subprocess MUST perform independent acceptance
   before delivery; the human grants `confirmed` ([§15.4](#154-consistency-contract)).

### 15.2 Isolation Semantics

- A subprocess's working context (tool calls, intermediate reasoning, partial
  outputs) MUST NOT enter the main session context.
- A subprocess MUST return its final answer plus references to the artifacts it
  wrote — nothing else.
- A subprocess MUST persist its outputs as artifacts before returning
  (artifacts are the cross-session memory of execution).
- Artifact paths SHOULD be configurable by the host; the default layout is
  `.artifacts/` (results), `.investigations/` (reasoning trails), and the
  noise-card store (see [§3](#3-noise-card-json-schema)).
- A Scout MUST persist its spec draft as an artifact
  before returning; the Judge integrates it via the three-source cross-check
  ([§15.4](#154-consistency-contract)).
- A Worker MUST persist its self-test record (command + output summary) under
  `.artifacts/` alongside the code it wrote in its declared module path. The
  Judge reviews a module's integration from three sources — the artifact
  snapshot, the working-tree diff, and the verification records — never from
  the Worker's working context alone.

### 15.3 Skill-Execution Coupling

Skills and subprocesses are two halves of one mechanism — **the skill is the
subprocess's operating manual**:

| Execution mode | Behavior | Example |
|----------------|----------|---------|
| `inline` | Skill loaded and executed in the main session. Suitable for convergent actions (writing, verification) and lightweight knowledge/management actions. | `anchor.concepts`, `anchor.challenge`, `anchor.write`, `anchor.test`, `anchor.noise`, `anchor.maintain` |
| `subprocess` | Main session dispatches an isolated subprocess; the subprocess loads the skill body as its operating manual, executes, persists artifacts, and returns only the final answer + artifact references. Suitable for divergent actions (survey, large scans). | `anchor.scan`, `anchor.degrade` |

**Role-skill binding (v0.10)** — the pipeline roles load skills as their
operating manuals ([§14](#14-agent-skills-anchor-skill-manifest-v05)):

| Role | Loads | Purpose |
|------|-------|---------|
| Judge (main session) | `anchor.judge` (role), `anchor.concepts`, `anchor.test`, `anchor.maintain` | judging, semantics, verification, protocol maintenance |
| Scout (subprocess) | `anchor.scout` | spec drafting (requirements discovery is external) |
| Worker (subprocess) | `anchor.worker`, `anchor.write`, `anchor.test` | module implementation, anchoring, self-testing |

**Execution-mode selection principle (v0.10; v0.11 amended)** — convergent
lightweight actions (semantics lookup, single-file anchoring, verification
runs, protocol maintenance) default to `inline` in the main session.
Divergent or heavy work — surveys, large scans, module implementation — runs
as subprocesses: Scouts and Workers execute isolated per
[§15.1](#151-definition) and [§15.2](#152-isolation-semantics). The v0.8
principle ("the main agent writes code itself; no subagents for programming")
is **superseded in v0.10 by the Judge-driven pipeline**: the main session
holds the acceptance criteria and adjudicates, while module code is produced
by parallel Workers under an approved implementation spec — the spec lock-in
is what makes parallelism safe. `subprocess` is no longer "an optimization for
divergent work"; it is the execution mode of the Scout/Worker roles.

The coupling flow (SHOULD):

1. The main session consults the skill index and resolves the skill's execution mode.
2. For `subprocess` skills, the main session dispatches an isolated subprocess
   with the skill's name as the task contract.
3. The subprocess loads the skill body (the operating manual), executes the
   action, and persists artifacts per [§15.2](#152-isolation-semantics).
4. The subprocess returns its final answer + artifact references.
5. The main session (or the host's human) adjudicates per the confidence state
   machine ([§15.4](#154-consistency-contract)).

`subprocess` is a SHOULD (run it isolated when the host supports subprocesses);
`inline` is always permitted.

### 15.4 Consistency Contract

**Confidence state machine** — every artifact carries a confidence status:

| Status | Meaning | Set by |
|--------|---------|--------|
| `draft` | Freshly produced, unverified | producer (default) |
| `candidate` | Reviewed, has supporting evidence | review gate, or auto-promotion in Full mode ([§9.1](#91-three-operating-modes)) |
| `confirmed` | Human-approved as trustworthy | **the host's human user ONLY — AI MUST NOT set `confirmed`** |

- Transitions are one-way: `draft → candidate → confirmed`. No downgrade below
  the evidence held.
- A review gate (Judge) MAY examine artifacts and issue review opinions, but
  MUST NOT change a status directly — the human approves promotion.
- The retry cap from [§9.4](#94-retry-cap-anti-entropy) applies per function.

**Judge review baseline (v0.7)** — the judge MUST cross-check three sources to
prevent stale delivery snapshots:

1. The `.artifacts` delivery snapshot (produced output)
2. git HEAD + working-tree diff (the code as actually applied — a subagent
   delivery may have been modified/merged by the host afterwards)
3. Verification/regression records (regression-type documents under
   `.investigations/`)

When the three disagree (e.g. snapshot older than the working tree), the
working tree is authoritative and the discrepancy MUST be noted.

Rationale (CoreSwap 8576-24blocks): the judge reviewed only the `.artifacts`
snapshot, while the SearchTree `Node::getSquaredDistance` 64-bit fix was
applied by the main session — the judge mis-reported "32-bit unfixed" based on
the stale snapshot.

**Judge trigger points (v0.9; extended v0.10)** — the review gate is not only a closing gate;
it is a mandatory checkpoint at specific decision points, and in v0.10 it is the
driving mechanism of the Judge-driven pipeline ([§15.1](#151-definition)). A judge review:

- MUST precede any human grant of `confirmed`. A human MAY grant `confirmed`
  only after a judge review opinion exists for the artifact; without a judge
  opinion, `candidate` is the highest reachable status.
- MUST precede major redirections. Before a session (or agent) acts on any of
  the following, a judge review of the conclusion being overturned/asserted is
  required:
  1. **Case reopening** — overturning a previously closed/confirmed conclusion
     on new evidence;
  2. **Root-cause determination** — asserting a definitive root cause (e.g. "no
     bug in the implementation", "the framework is responsible");
  3. **Significant scope decisions** — expanding or cutting the scope of a
     verification campaign (e.g. adding/removing a subsystem under test).
- SHOULD accompany stage-conclusion promotion to `candidate`: whenever a
  producer promotes a stage result to `candidate`, a judge review is
  recommended (a missing judge opinion MUST be noted in the artifact).
- (v0.10; v0.11 amended) MUST fire at every pipeline stage boundary — the
  Judge's nod is the stage's terminal action:
  1. **Input contract acceptance** — Judge accepts the external requirements
     document + software specification and derives the acceptance criteria
     from it ([§15.1](#151-definition) stage 0); no implementation work may
     start without this nod;
  2. **Spec approval** — Judge approves the implementation spec (stage 1 end);
  3. **Plan approval** — Judge approves the module breakdown (stage 2 end);
  4. **Module integration** — Judge reviews each Worker's module and grants or
     denies integration (stage 3, per module);
  5. **Delivery acceptance** — Judge performs the final review and, with the
     isolated acceptance verdict, authorizes delivery (stage 4).

**Acceptance criteria first (v0.10; v0.11 amended)** — the Judge derives the
acceptance criteria from the input contract (confirmed requirements document
+ software specification, [§15.1](#151-definition) stage 0) before
implementation begins: the claims the deliverable MUST satisfy, the
validation carriers that bind them (`@anchor.test` per
[§5](#5-anchor-test-and-idk-decorators)), and the boundary declarations
(`@anchor.idk`) for what is out of scope. Criteria derivation is an Anchorlaw
duty; the requirements themselves are external. Implementation converges on
these criteria; a review opinion is judged against them, never invented during
review. Criteria-first is what makes the termination gates below
self-bounded — the criteria are the boundary, so verification cannot run out
of control.

**Self-review ≠ review gate (v0.9)** — a producer's own verification and
self-check MUST NOT be presented as the §15.4 review gate. "The main agent
wrote and verified it" is evidence, not review. The review gate MUST be
performed by an independent reviewer — an isolated subprocess (per §15.3) or an
external human — who did not produce the artifact under review. A status of
`confirmed` therefore implies an independent reviewer issued an opinion.
`candidate` has two promotion paths: (a) review-gate promotion — implies an
independent reviewer; (b) automatic promotion in Full mode
([§9.1](#91-three-operating-modes)) — such an artifact MUST note the absence
of independent review, and does not satisfy the stage-conclusion
SHOULD-review recommendation above.

**Plan-time judge placement (v0.9)** — workflow plans (task lists, todo plans)
MUST pre-place judge steps at the trigger points above, at planning time — not
tack them on after the fact. A plan that reaches a trigger point without a
pre-placed judge step MUST stop and add one before proceeding.

**Verification termination gates (v0.9; amended v0.10)** — the convergence gate
(verification → review → commit) MUST terminate on mechanical criteria, not on
the exhaustion of review opinions. (v0.10: in the Judge-driven pipeline the
gates apply per stage, and the terminal state is the Judge's nod —
criteria-first makes the gates self-bounded, see **Acceptance criteria first**
above.) This section exists because a review-driven
loop without termination criteria became the failure mode it was designed to
prevent (Anchorlaw v0.9 practice review: the main agent ran repeated review
rounds on non-blocking opinions, added a self-imposed assertion outside the
approved plan, and consumed 30+ minutes on a single encoding false positive).
(Labels A/B/C/E: the plan-time judge placement section above is the D-tier
guard — producer self-review and in-place standard expansion are covered by A.3
below, so no separate D is needed.)

- **A. Termination criteria (external test set)** — the verification phase
  terminates when all of the following hold:
  1. The external test set passes — the tests defined by the approved plan and
     the repository's existing test suite are green (NOT tests added by the
     producer during verification);
  2. No unresolved blocking-level opinion remains (per B below);
  3. Every remaining opinion has a recorded disposition (adopted / deferred as
     debt / excluded with reason).
  The producer MUST NOT add tests during the verification phase to expand the
  gate. A verification-time discovery that needs a new test or a new rule MUST
  be recorded as debt or returned to the planning phase for explicit approval —
  the deliverable standard may not be expanded in place.
- **B. Review opinion severity tiers** — review/judge opinions fall into
  exactly three tiers; only tier 1 blocks:
  1. **blocking** — only three mechanical criteria: (i) test failure,
     (ii) build/compile failure, (iii) a protocol claim contradicted by the
     implementation. No other opinion may be classified blocking;
  2. **should-fix** — recommended changes; recorded with a disposition, do not
     block commit;
  3. **info** — notes and observations; recorded, may be ignored. An opinion
     that conflicts with locally verifiable evidence (e.g. an encoding false
     positive) is classified info and excluded with the reason recorded;
     excluding a false positive MUST NOT require more than one verification
     round.
- **C. Judge-nod termination (v0.10, replacing the v0.9 round cap)** — the
  pipeline terminates per stage on the Judge's nod: criteria satisfied
  (external test set green, no unresolved blocking opinion, dispositions
  recorded — A and B above), not on round counting. Return-and-fix is normal
  pipeline iteration: every return carries a review opinion the Worker acts
  on, so each iteration converges on the same pre-defined criteria. When a
  criterion stays unmet across iterations, the Judge MUST NOT keep looping —
  it MUST escalate to the human: either the criterion itself is wrong
  (challenge via [§12](#12-rule-challenge-process-v04) or human amendment) or
  the approach is wrong (return to planning). The v0.9 "3-round cap" was a
  patch for unbounded review loops caused by criteria defined after the fact;
  v0.10 criteria-first removes the cause, so the cap is unnecessary — the
  criteria are the boundary. The per-function retry cap of
  [§9.4](#94-retry-cap-anti-entropy) is unchanged.
- **E. Evidence-conflict channel** — a conflict between a review opinion and
  locally verifiable evidence is resolved via the §12 rule challenge process
  (for rules) or recorded exclusion as tier-3 info (for opinions), never by
  entering the verification loop to re-litigate an excluded finding.

**Key-checkpoint isolated acceptance (v0.10; v0.11 amended)** — the Judge
(main session) adjudicates continuously, but at two checkpoints independent
acceptance is MANDATORY: (1) before a Worker's module is integrated (stage 3),
and (2) before delivery (stage 4), the Judge MUST delegate a review to an
isolated
judge subprocess, which cross-checks the artifact snapshot, the working-tree
diff, and the verification records (Judge review baseline above). This
instantiates "self-review ≠ review gate": the Judge's own nod is the driver,
the isolated subprocess's verdict is the gate.

### 15.5 Interface-Surface Audit (v0.6)

The protocol's external contracts, classified as **interface definitions**
(language-agnostic, MUST stay stable) vs **implementation details**
(replaceable by any host):

| Contract | Classification | Notes |
|----------|---------------|-------|
| Anchor semantics: `@anchor.test` / `@anchor.idk` (§5) | interface | Declaration site + validation carrier (§13) |
| Source provenance format (§5.5) | interface | `source="<type>:<bin>!<fn>#<id>, ..."` |
| Scanner patterns P1–P6 + severity layering (§6) | interface | Language-agnostic definitions |
| Noise card JSON schema (§3) | interface | Schema is normative; **store path is implementation detail** |
| Stub-based uninstall (§2) | interface | Removal contract |
| CLI subcommand surface (check/test/noise/...) | interface | The operational entry point (§14.4) |
| Skill manifest (§14) | interface | Name/layer/single-responsibility/trigger/inputs/outputs/body/execution mode |
| Execution topology (§15) | interface | Isolation + artifact + consistency contracts |
| Concrete artifact file layout (`.artifacts/index.yaml` etc.) | implementation | Default layout; hosts MAY remap paths |
| Concrete model/effort choices | implementation | Host-specific |

The audit principle: **an interface definition MUST be implementable without
host restructuring; an implementation detail MUST be replaceable without
protocol change.**

### 15.6 Relationship to §4, §13, §14, §16

Four-layer interface surface — two axes from v0.4/v0.5 plus two new in v0.6:

| Axis | Contract | Solves |
|------|----------|--------|
| Claim | anchor abstraction (§13) | declaration site + validation carrier |
| Knowledge | skill manifest (§14) | knowledge loaded on demand (static) |
| Execution | execution topology (§15) | execution isolated on demand (dynamic) |
| Integration | host integration contract (§16) | hosts implement interface points without restructuring |

---

## 16. Host Integration Contract (v0.6)

> **Trigger for this section:** every host so far had to
> re-invent integration glue — renamed annotations, remapped artifact stores,
> re-derived mode mappings. Two-way adapter friction violates the protocol's
> purpose (one definition, many implementations) and makes Anchorlaw heavier
> with every host. The fix is an **installable interface surface**: a host
> implements a fixed set of interface points and does NOT restructure its own
> framework.

### 16.1 Definition

A **Host** is any framework, platform, or project that runs Anchorlaw —
an Agent platform, a language toolchain.

A Host MUST implement these interface points to be Anchorlaw-compatible:

| Interface point | What the host provides | Default / form |
|-----------------|------------------------|----------------|
| **Execution point** | Run protocol actions: scan, test, noise management, verification | `anchorlaw` / `anchorlaw-scanner` CLI subcommands (or an equivalent runtime API) |
| **Artifact paths** | Configurable store for artifacts, investigations, noise cards | Default `.artifacts/`, `.investigations/`, noise store |
| **Confirm hook** | A path through which a human grants `confirmed` | Host's review UI / command |
| **Trigger point** | Load skills per the manifest (§14) and dispatch subprocesses per the execution topology (§15) | Host's skill/agent mechanism |

(v0.10; v0.11 amended) The confirm hook is exercised at **one** point inside
Anchorlaw: the **`confirmed` grant** — the human approves a delivery as
trustworthy ([§15.4](#154-consistency-contract)). The requirements-side human
authorization gate moved OUT in v0.11: requirements confirmation happens in
the external requirements protocol, and Anchorlaw receives **already-confirmed**
requirements + software specification as its input contract
([§15.1](#151-definition) stage 0) — the host handover IS the human's
authorization to implement. The Judge's nod at any pipeline stage is a
recommendation, never an authorization.

### 16.2 Boundary

- Anchorlaw MUST NOT require a Host to restructure its own framework.
  Compatibility is achieved by implementing the four interface points, not by
  reorganizing the host.
- A Host MUST NOT require Anchorlaw to fork or customize for it. If a protocol
  clause blocks a legitimate host use case, the host SHOULD file a rule
  challenge ([§12](#12-rule-challenge-process-third-law-v04)) or propose a new
  interface point — not fork the protocol.
- Artifact store paths, file formats (YAML/JSON), and model choices are
  implementation details ([§15.5](#155-interface-surface-audit)): a host MAY
  remap them without protocol change.

### 16.3 Integration Checklist

A Host claiming Anchorlaw compatibility MUST satisfy:

1. All protocol actions reachable through the execution point (CLI/API).
2. Artifacts persist and are indexed; paths configurable.
3. `confirmed` is grantable only by a human via the confirm hook.
4. Skills load via the manifest; `subprocess` skills dispatch to isolated subprocesses.
5. Anchor annotations follow §5 semantics (source provenance on `@anchor.test`).
6. Removal is clean per the Uninstall Guarantee (§2) — no behavioral residue.
