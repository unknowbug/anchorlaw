# Anchorlaw Protocol

**[English](README.md) | [中文](README_zh.md)**

> **"Any claim must have a verifiable practice anchor."**
>
> — First Law, Materialist Practice Theory

Anchorlaw is a **code verification protocol for vibe coding** — not a test framework, not a linter.

It detects **defensive code patterns** that signal cognitive gaps and provides a **structured feedback loop** for AI-assisted development.

---

## Maturity (Per Component, Per First Law)

| Component | Python | TypeScript | Maturity |
|-----------|--------|-----------|----------|
| **Scanner** | ✅ [anchorlaw-scanner](python/anchorlaw-scanner/) | ✅ [anchorlaw-scanner](typescript/anchorlaw-scanner/) | **VERIFIED** — tested on real projects |
| **Anchors** | ✅ [anchorlaw](python/anchorlaw/) | — | **EXPERIMENTAL** — API stable, no efficacy data |
| **Source Provenance (v0.3/v0.7)** | ✅ `source` param + probe type (v0.7) | — | **SCOPED** — implemented in Python (source param, INVALID when missing/static on test, `probe:` type v0.7); 1 project (CoreSwap) produced sourced anchors |
| **Noise Cards** | ✅ [anchorlaw](python/anchorlaw/) | — | **UNVERIFIED** — schema defined, no accumulated data |
| **AI Context** | ✅ [anchorlaw](python/anchorlaw/) | — | **CONJECTURE** — format defined, no A/B test |
| **Degraded Verification (v0.3)** | — | — | **CONJECTURE** — modes defined, no project beyond the reference host has exercised Partial/Degraded paths |

> **Honesty notice**: Components marked EXPERIMENTAL, UNVERIFIED, or CONJECTURE are working hypotheses. Their value has not been demonstrated through practice. Use them to help us test the hypotheses — not because we claim they work.
>
> **v0.18 update (2026-08-13):** DSH host adaptation — DeepSeek Harness (DSH) is the first host implementing the full §16 Host Integration Contract interface surface: the `dsh/` subtree ships 11 anchor-* skills (DSH format, kebab-case + whenToUse), 4 model tools (`anchorlaw_scan` / `anchorlaw_report` / `anchorlaw_ai_context` / `anchorlaw_status`) with a host-level global tool mount, the `anchorlaw` agent preset (Judge-driven pipeline, §15.4), and a project-level (Reasonix-style) install mode for per-project skill scoping. See [DSH Host Adaptation](#deepseek-harness-dsh-host-adaptation). Implementation fix (2026-08-15): `anchorlaw noise resolve` now accepts the short suffix id printed by `noise list` (previously only the full `noise-…` id resolved, contradicting the CLI help "Noise ID (or suffix)"); covered by 4 new unit tests.
>
> **v0.17 update (2026-08-12):** §12 challenge outcomes (Reasonix/Go audit) — ① parse-error marker: an unparseable source file is a tool-level `parse-error` (INFO), never a P1-P6 pattern (SyntaxError was misclassified as swallowed-exception); ② comment-form language claims downgraded: Go/Java/C++ registration means annotation-extraction ONLY, P1-P6 detection is not mapped to them; ③ four new language-agnostic reliability-risk patterns P7-P10 (LIFECYCLE / STATE_MACHINE / PATH-COORDINATION / COMPLEXITY) defined, implementations map them per language.
>
> **v0.16 update (2026-08-10):** Go/Java registered as comment-form languages (line comments `// @anchor.*`, same declaration site as C++; independent probe/test binary as validation carrier) and wired into the reference extractor (annotation-extraction). Rust declared not supported by design — its compiler, borrow checker, and test framework already provide the verification this protocol adds elsewhere; the proc-macros plan is abandoned (§2.4/§13).
>
> **v0.15 update (2026-08-10):** C-gate halted escalation — after 3 iterations on the same acceptance criterion without it being met (the review is still reporting unresolved issues), the pipeline MUST halt entirely: the Judge submits a detailed report of the review situation and unresolved issues to the human, who decides (criterion wrong → §12/amendment, approach wrong → planning, or otherwise). The Judge's round-4 pre-classification is removed — no further iteration, fix, or re-review without the human's decision (§15.4).
>
> **v0.14 update (2026-08-10):** Input-contract layering — the input contract is clarified as confirmed requirements + technical-constraint specification (customer-confirmable facts: claims, boundaries, terminology, technical constraints); architecture design (modularization, dependency direction, interfaces) is produced at pipeline stage 1, not carried in the input. §16.1's handover criterion generalized to a protocol-neutral input-contract confirmation criterion (semantic convergence) — no upstream framework is named or adapted to; the three protocols (requirements / Anchorlaw / reverse-engineering) are independently operable frameworks.
>
> **v0.13 update (2026-08-10):** §12 challenge outcome — "programming is constructive" is narrowed to the input-contract domain (registered in the §11 audit; reverse engineering explicitly OUTSIDE the domain — exploratory, unbounded verification; the two modes are complementary). §16.1 RE handover criterion: an input contract counts as *confirmed* only when the vanilla-behavior model has converged; mixed tasks enter Anchorlaw only for determined sub-portions. §9.4 retry cap upgraded to evidence saturation — 3 rounds WITHOUT new data-layer evidence, not 3 rounds.
>
> **v0.12 update (2026-08-10):** C-gate mechanical fallback restored — criteria-first remains the core (acceptance criteria determined before implementation; Judge-nod termination per stage), and iteration on the same acceptance criterion is capped at 3 with mechanical escalation to the human on iteration 4 (criterion wrong → §12 challenge/amendment; approach wrong → planning). The v0.10 Judge-nod-only form relied on the Judge recognizing persistent failure — the exact failure mode (repeated rounds without realizing) the gates exist to prevent (§15.4).
>
> **v0.11 update (2026-08-10):** Input-contract boundary — requirements discovery is REMOVED from Anchorlaw: it belongs to a separate requirements protocol (Scout-driven, human-dialogue based, Judge technical review), whose output (confirmed requirements + software specification) is Anchorlaw's stage-0 input contract. Anchorlaw runs a four-stage Judge-driven pipeline (input contract → implementation spec → plan → parallel implementation → delivery). Three-protocol closure: requirements protocol → Anchorlaw → RE framework (§15.1, §16.1).
>
> **v0.10 update (2026-08-10):** Judge-driven programming — programming is constructive, not exploratory like reverse engineering: the workflow is Judge-driven with acceptance-criteria-first (§15.4). Scout/Worker roles reinstated as general-protocol programming roles; AGENTS.md became index-only (no protocol-text mirroring — mirror drift was the root cause of the v0.9 review loops).
>
> **v0.9 update (2026-08-08):** Judge institutionalization — the review gate is a mandatory checkpoint at decision points, not only a closing gate: `confirmed` requires a prior judge opinion; major redirections (case reopening, root-cause determination, scope decisions) require judge review; self-review does not constitute the review gate; plans pre-place judge steps (§15.4). Verification termination gates: convergence terminates on mechanical criteria (external test set, three-tier review opinions with blocking limited to test/compile/claim contradictions, 3-round cap) — no more endless review loops (§15.4).
>
> **v0.8 update (2026-08-08):** Convergence-gate model — programming is linear convergence; the main agent writes with full context; the only sanctioned subagent role is the review gate (judge). `anchor.write`/`anchor.test` are `inline`.
>
> **v0.7 update (2026-08-08):** First-host practice feedback (CoreSwap 8576-24blocks) absorbed — source artifact requirement + `probe` source type (§5.5), retry-cap scope (§9.4), verification executor separation (§9.6), order-dependent semantic equivalence (§13), judge three-source baseline (§15.4).
>
> **v0.6 update (2026-08-08):** Agent Execution Topology (§15) + Host Integration Contract (§16) — the four-layer interface surface is complete: claim (§13), knowledge (§14), execution isolation (§15), host integration (§16). Subprocess skills keep the main session clean.
>
> **v0.5 update (2026-08-08):** Agent Skill Manifest (§14) — layered, single-responsibility skills move protocol knowledge to on-demand playbooks, fixing agent-side attention dilution. Reference implementation ships in `.reasonix/skills/`.
>
> **v0.3 update (2026-06-18):** Source Provenance, Degraded Verification modes, and Verify retry cap. See [Protocol Spec v0.3](spec/protocol-v0.3.md).

---

## Quick Start

### Scanner (Immediate Value)

```bash
# Python
pip install anchorlaw-scanner
anchorlaw-scanner check src/

# TypeScript
npm install anchorlaw-scanner
npx anchorlaw-scanner check src/

# C++ (@anchor 注释式标注提取验证 — annotation-extraction, Level 1)
anchorlaw-scanner check --lang cpp src/
```

The scanner finds:
- **Swallowed exceptions** — `except: pass` / `catch {}`
- **Bare exception handlers** — catching `Exception` / `any`
- **Missing anchors** — functions with no `@pt` or `@idk`
- **Defensive null chains** — 3+ chained `if x is None: return None`
- **Trivial tests** — `assert f(x) == f(x)`
- **Vague TODOs** — `// TODO: fix` without ticket reference

### Full Protocol (Experimental)

```bash
pip install anchorlaw
```

```python
from anchorlaw import test as pt, i_dont_know as idk

@pt("empty list returns empty",
    lambda: process([]) == [],
    source="trace:process#000, input=[] output=[] observed 2026-06-18")  # v0.3: source field records data origin
@pt("keep positives",
    lambda: process([-1, 0, 3, -5]) == [3],
    source="trace:process#001, output=[3] observed 2026-06-18")
@idk("behavior with massive lists (>1M items) not verified",
    source="static: not covered in traces")
def process(data: list[int]) -> list[int]:
    return [x for x in data if x > 0]
```

---

## DeepSeek Harness (DSH) Host Adaptation

Same protocol, single repository: the `dsh/` subtree is the DSH (DeepSeek Harness) host adaptation layer — the protocol core stays at the repo root, the DSH ecosystem adaptation lives in `dsh/` (maintained by the DSH agent 大肥鱼):

- **11 protocol skills** — `dsh/skills/` holds the DSH-format skills (`anchor-*`, kebab-case + `whenToUse`); bodies are derived from `.reasonix/skills/`, with byte-level consistency enforced by `dsh/tests/test_manifest.py`
- **Model tools** — `dsh/plugins/anchorlaw-tools.js` registers 4 tools: `anchorlaw_scan` (Level-1 scanner), `anchorlaw_report` (health report), `anchorlaw_ai_context` (noise cards + curriculum injection), `anchorlaw_status` (toolchain status)
- **Agent preset** — `dsh/preset/` packages the `anchorlaw` preset: the Judge-driven four-stage pipeline persona (spec §15.4), with scout/worker/judge delegated through isolated subagents

```powershell
# host-level (default): user-level preset + skills + GLOBAL tool mount into the
# active profile's cordis.patch.yml; regenerable — never hand-edit
pwsh dsh/scripts/install.ps1
# project-level (Reasonix-style): skills load only in <dir> sessions, not elsewhere
pwsh dsh/scripts/install.ps1 -Project /path/to/project
# five-item self-check: toolchain / skill manifest / scanner self-scan / installed artifacts / plugin tool schemas
pwsh dsh/scripts/selfcheck.ps1
```

Host-level install mounts the 4 `anchorlaw_*` tools globally: it appends an `insert` row to every profile's `cordis.patch.yml` under `<dshHome>/profiles/` (the ONLY user patch layer DSH reads; hot-reloaded) — `-Profile <name>` mounts one profile only — and copies the plugin to `<profile>/plugins/anchorlaw/`. The mount is gated by `dsh/tests/check_plugin_schema.mjs`, which verifies every tool's `parameters` is a compiled JSON-Schema object root — a flat spec would reach the LLM without a top-level type and break every session (2026-08-13 incident guard).

Project-level install places the 11 `anchor-*` skills under `<project>/.dsh/skills/` (DSH's native project-scoped root) — a session opened inside that project loads them, sessions elsewhere do not. DSH has no project-level plugin mechanism yet (upstream suggestion: [deepseek-ai/deepseek-harness discussion #306](https://github.com/deepseek-ai/deepseek-harness/discussions/306)); the `anchorlaw_*` tools come from the host-level global mount.

Maintenance entry: [`dsh/AGENTS.md`](dsh/AGENTS.md) — single source of truth; body edits go to `.reasonix/skills/`, `dsh/skills/` holds frontmatter adaptation only.

---

## The Principle

Traditional development separates "writing code" from "writing tests." Vibe coding makes this separation costly — AI generates code fast, but verification happens later, manually, and feedback is lost between iterations.

Anchorlaw inverts this: **tests are part of the declaration, not an add-on.** A function without a test anchor or an `i_dont_know` declaration is flagged at scan time — not because it's buggy, but because it has no evidence of correctness.

When tests fail at runtime, failures are captured as **noise cards** — structured knowledge that accumulates over time and can be injected back into AI context for future code generation.

### "Only Offense, No Defense"

The protocol does not prohibit — it demands proof:
- Traditional: "You cannot divide by zero." (defensive)
- Anchorlaw: "Prove the divisor is non-zero, or handle the zero case." (offensive)

The single allowed defense is `@idk` — an honest declaration that opens the battlefield for practice feedback.

---

## Project Structure

```
anchorlaw/
├── README.md                    <-- you are here
├── spec/
│   └── protocol-v0.18.md       # Language-agnostic protocol spec (current)
├── python/
│   ├── anchorlaw-scanner/       # Standalone scanner (Level 1, VERIFIED)
│   └── anchorlaw/               # Full protocol (Level 2-4, EXPERIMENTAL)
├── typescript/
│   └── anchorlaw-scanner/       # TS/JS scanner (Level 1, IN DEVELOPMENT)
└── dsh/
    ├── skills/                  # 11 DSH-format anchor-* skills (derived from .reasonix/skills/)
    ├── plugins/                 # anchorlaw-tools.js — 4 model tools
    ├── preset/                  # anchorlaw agent preset (Judge-driven pipeline)
    └── AGENTS.md                # DSH host adaptation maintenance entry
```

---

## Contributing

This project is actively seeking **practice data**, not pull request debates.

The most valuable contribution right now:
1. **Run the scanner** on your codebase. Report false positives.
2. **Use the anchors** on a real project for 2+ weeks. Tell us if they helped or hurt.
3. **Accumulate noise cards**. We need projects with 30+ cards to test AI context injection.

Start a discussion on [GitHub Discussions]() or open an issue with your findings.

---

## References

- [Protocol Specification v0.18](spec/protocol-v0.18.md)
- Degraded Verification: [§9 of the spec](spec/protocol-v0.18.md#9-degraded-verification-v03-draft) — three operating modes for when code can't compile
- [Materialist Practice Theory](https://github.com/unknowbug/anchorlaw/wiki) — the philosophical foundation

---

> "This project does not promise eternal truth. It promises a set of tools forged in current historical conditions, open to being replaced by better ones. Its highest commitment is to make its users capable of questioning, improving, and ultimately transcending it."
>
> — First Law, Applied Reflexively
