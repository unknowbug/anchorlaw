# Anchorlaw — Code Verification on DeepSeek Harness

**[English](README.md) | [中文](README_zh.md)**

> **"Any claim must have a verifiable practice anchor."**
>
> — First Law, Materialist Practice Theory

Anchorlaw is a **code verification toolchain for AI-assisted (vibe) coding**, maintained as a **DeepSeek Harness (DSH) host adaptation**: the `dsh/` subtree ships 11 protocol skills, 4 model tools, and the `anchorlaw` agent preset — install once, and every DSH session gets scan / report / noise-card / AI-context tooling. The underlying protocol (`spec/`, `python/`, `typescript/`) is language-neutral and drives the DSH tools. The Reasonix host format is **archived, not maintained** — see [Reasonix Version Archive](#reasonix-version-archive).

---

## Quick Start (DSH)

```powershell
# 1. install once (host-level default): preset + user skills + global tool mount
pwsh dsh/scripts/install.ps1
# 2. five-item self-check: toolchain / skill manifest / self-scan / installed artifacts / tool schemas
pwsh dsh/scripts/selfcheck.ps1
# 3. open a NEW DSH session → 4 anchorlaw_* tools + 11 anchor-* skills in every session
```

Per-project install (Reasonix-style): `pwsh dsh/scripts/install.ps1 -Project /path/to/project` — the 11 skills load only inside that project's sessions.

> Tools appear in **new** sessions (session composition is fixed at creation). The global mount is gated by a tool-schema check (2026-08-13 incident guard) — a malformed schema can never be installed.

## What You Get (DSH)

### 4 model tools — global, every session

| Tool | What it does |
|------|--------------|
| `anchorlaw_scan` | Level-1 defensive-pattern scanner (P1-P6; `lang` cpp/go/java → annotation extraction) |
| `anchorlaw_report` | Health report (scan findings + noise backlog + verdict) |
| `anchorlaw_ai_context` | Noise cards + curriculum export for LLM context injection |
| `anchorlaw_status` | Toolchain versions + discovered `anchor-*` skills |

### 11 protocol skills (`anchor-*`, DSH format)

L0-L4 action skills + execution roles (scout/worker/judge), loaded per scenario; skill bodies live in `dsh/skills/` (single source of truth, protocol §14 is the host-neutral spec). Trigger index and tool-call conventions: `dsh/AGENTS.md`.

### anchorlaw agent preset

Judge-driven four-stage pipeline persona (protocol §15.4): input contract → implementation spec → plan → parallel implementation → delivery. Acceptance criteria first, 3-round hard stop, `confirmed` granted **only by the human**; scout/worker/judge delegated through isolated subagents.

---

## Protocol Core (language-neutral backend)

The protocol itself lives at the repo root and is host-neutral — the DSH tools drive its CLI:

| Component | Where | State |
|-----------|-------|-------|
| **Spec** | `spec/protocol-v0.20.md` | Language-agnostic code-verification protocol (current) |
| **Python** | `python/anchorlaw-scanner` + `python/anchorlaw` | Scanner (verified) + anchors/noise/CLI (experimental) — the DSH tool backend |
| **TypeScript** | `typescript/anchorlaw-scanner` | TS/JS scanner (in development) |

### Component Maturity

| Component | Python | TypeScript | Maturity |
|-----------|--------|-----------|----------|
| **Scanner** | ✅ [anchorlaw-scanner](python/anchorlaw-scanner/) | ✅ [anchorlaw-scanner](typescript/anchorlaw-scanner/) | **VERIFIED** — tested on real projects |
| **Anchors** | ✅ [anchorlaw](python/anchorlaw/) | — | **EXPERIMENTAL** — API stable, no efficacy data |
| **Source Provenance (v0.3/v0.7)** | ✅ `source` param + probe type (v0.7) | — | **SCOPED** — implemented in Python; 1 project (CoreSwap) produced sourced anchors |
| **Noise Cards** | ✅ [anchorlaw](python/anchorlaw/) | — | **UNVERIFIED** — schema defined, no accumulated data |
| **AI Context** | ✅ [anchorlaw](python/anchorlaw/) | — | **CONJECTURE** — format defined, no A/B test |
| **Degraded Verification (v0.3)** | — | — | **CONJECTURE** — modes defined, not exercised beyond the reference host |

> **Honesty notice**: Components marked EXPERIMENTAL, UNVERIFIED, or CONJECTURE are working hypotheses. Their value has not been demonstrated through practice. Use them to help us test the hypotheses — not because we claim they work.

### Changelog

> **v0.20 (2026-09-01):** Evidence/conclusion continuity (from CoreSwap M11/M14/M16 practice) — three new clauses: ① **conclusion supersession chain** (§15.4): an overturned candidate+ conclusion is expressed as a supersession record (bidirectional links + reason; original text never rewritten), mechanically answering "what is the currently valid conclusion + its history"; ② **verification comparability statement** (§9.7): quantitative metrics MUST declare the comparison basis (carrier / coverage / comparability with prior metrics); ③ **host handover validation** (§16.3 checklist): handover items distinguish verified conclusions from unverified hypotheses, and the inheritor MUST run one cheap independent verification before using a direction-level conclusion as a premise. Evidence persistence and compaction process stay host/framework scope.
>
> **v0.19 (2026-08-15):** Verification-scope clarification — Anchorlaw is a VERIFICATION protocol, not a knowledge-accumulation protocol. The noise-card `discovery`/`curriculum` fields are reframed from "knowledge accumulation duty" to verification backtracking; §15.2 artifacts are the verification-reproducibility carrier (not "cross-session memory"); §14 is explicitly NOT the knowledge sink (that is a host / separate knowledge mechanism's job). The verification core (`@anchor.test` / `source` / staleness / health states / §9) is unchanged — it was the actual guard that let the seed contamination be traced, not misjudged as "Rust has no bug".
>
> **v0.18 (2026-08-13):** DSH host adaptation — DSH is the first host implementing the full §16 Host Integration Contract interface surface (11 skills, 4 tools, anchorlaw preset, host-level global tool mount, project-level install). Fix (2026-08-15): `anchorlaw noise resolve` accepts the short suffix id printed by `noise list`; 4 new unit tests. **v0.18 also archives the Reasonix host format** (`.reasonix/skills/` → `archive/reasonix/`); `dsh/skills/` became the single skill source of truth.
>
> **v0.17 (2026-08-12):** §12 challenge outcomes (Reasonix/Go audit) — parse-error marker (INFO, never a P1-P6 pattern); comment-form language claims downgraded (annotation-extraction ONLY); P7-P10 reliability-risk patterns defined.
>
> **v0.16 (2026-08-10):** Go/Java registered as comment-form languages; Rust declared not supported by design.
>
> **v0.15 (2026-08-10):** C-gate halted escalation — 3 unmet iterations on the same criterion MUST halt the pipeline; the Judge hands the full report to the human.
>
> **v0.14 (2026-08-10):** Input-contract layering — contract = confirmed requirements + technical constraints; architecture design is pipeline stage-1 output; §16.1 handover generalized to a protocol-neutral confirmation criterion.
>
> **v0.13 (2026-08-10):** §12 challenge outcome — constructiveness scoped to the input-contract domain (RE outside); §16.1 RE handover criterion; §9.4 retry cap → evidence saturation (3 rounds without new data-layer evidence).
>
> **v0.12 (2026-08-10):** C-gate mechanical fallback restored — iteration on the same criterion capped at 3, mechanical escalation to the human on iteration 4.
>
> **v0.11 (2026-08-10):** Input-contract boundary — requirements discovery removed from Anchorlaw (separate requirements protocol); four-stage Judge-driven pipeline.
>
> **v0.10 (2026-08-10):** Judge-driven programming — acceptance-criteria-first (§15.4); AGENTS.md became index-only.
>
> **v0.9 (2026-08-08):** Judge institutionalization — review gate mandatory at decision points; verification termination gates (external test set, three-tier opinions, 3-round cap).
>
> **v0.8 (2026-08-08):** Convergence-gate model — judge-only subagent role; `anchor.write`/`anchor.test` inline.
>
> **v0.7 (2026-08-08):** First-host practice feedback (CoreSwap 8576-24blocks) — source artifact + `probe` type (§5.5), retry-cap scope, executor separation, judge three-source baseline.
>
> **v0.6 (2026-08-08):** Agent Execution Topology (§15) + Host Integration Contract (§16).
>
> **v0.5 (2026-08-08):** Agent Skill Manifest (§14) — reference implementation then shipped in `.reasonix/skills/` (now archived).
>
> **v0.3 (2026-06-18):** Source Provenance, Degraded Verification modes, Verify retry cap. See [Protocol Spec v0.3](spec/protocol-v0.3.md).

---

## Reasonix Version Archive

The Reasonix host format (`.reasonix/skills/` — 11 `anchor.*` skills — and the Reasonix AGENTS.md) is **no longer maintained** since v0.18. It is archived under `archive/reasonix/`.

If you need to iterate on the Reasonix version: **fork this repository**, then run

```powershell
pwsh archive/reasonix/restore-reasonix.ps1
```

which restores `.reasonix/skills/` + the Reasonix `AGENTS.md` to the repo root — a complete Reasonix working copy to iterate from (see [`archive/reasonix/RESTORE.md`](archive/reasonix/RESTORE.md)). Upstream does not update it anymore.

---

## Project Structure

```
anchorlaw/
├── dsh/                           # DSH host adaptation (MAINTAINED)
│   ├── skills/                    # 11 anchor-* skills (single source of truth)
│   ├── plugins/                   # anchorlaw-tools.js — 4 model tools
│   ├── preset/                    # anchorlaw agent preset (Judge-driven pipeline)
│   ├── scripts/                   # install.ps1 / selfcheck.ps1
│   └── AGENTS.md                  # DSH maintenance entry
├── spec/
│   └── protocol-v0.20.md          # Language-neutral protocol (current)
├── python/                        # Protocol implementation (DSH tool backend)
│   ├── anchorlaw-scanner/         # Standalone scanner (Level 1, VERIFIED)
│   └── anchorlaw/                 # Anchors / noise / CLI (Level 2-4, EXPERIMENTAL)
├── typescript/
│   └── anchorlaw-scanner/         # TS/JS scanner (Level 1, IN DEVELOPMENT)
└── archive/
    └── reasonix/                  # Reasonix host format archive (unmaintained; fork & restore)
```

---

## Contributing

This project is actively seeking **practice data**, not pull request debates.

The most valuable contribution right now:
1. **Run the scanner** (`anchorlaw_scan` in DSH, or `anchorlaw-scanner check` from CLI) on your codebase. Report false positives.
2. **Use the anchors** on a real project for 2+ weeks. Tell us if they helped or hurt.
3. **Accumulate noise cards**. We need projects with 30+ cards to test AI context injection.

Start a discussion on [GitHub Discussions]() or open an issue with your findings.

---

## References

- [Protocol Specification v0.18](spec/protocol-v0.20.md)
- Degraded Verification: [§9 of the spec](spec/protocol-v0.20.md#9-degraded-verification-v03-draft)
- [Materialist Practice Theory](https://github.com/unknowbug/anchorlaw/wiki) — the philosophical foundation

---

> "This project does not promise eternal truth. It promises a set of tools forged in current historical conditions, open to being replaced by better ones. Its highest commitment is to make its users capable of questioning, improving, and ultimately transcending it."
>
> — First Law, Applied Reflexively
