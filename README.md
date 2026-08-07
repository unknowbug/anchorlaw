# Anchorlaw Protocol

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
| **Source Provenance (v0.3)** | — | — | **CONJECTURE** — field defined, 0 RE projects have produced sourced anchors |
| **Noise Cards** | ✅ [anchorlaw](python/anchorlaw/) | — | **UNVERIFIED** — schema defined, no accumulated data |
| **AI Context** | ✅ [anchorlaw](python/anchorlaw/) | — | **CONJECTURE** — format defined, no A/B test |
| **Degraded Verification (v0.3)** | — | — | **CONJECTURE** — modes defined, no RE project has exercised Partial/Degraded paths |

> **Honesty notice**: Components marked EXPERIMENTAL, UNVERIFIED, or CONJECTURE are working hypotheses. Their value has not been demonstrated through practice. Use them to help us test the hypotheses — not because we claim they work.
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
import anchorlaw as pract

@pt("empty list returns empty",
    lambda: process([]) == [],
    source="manual: expected behavior")  # v0.3: source field records data origin
@pt("keep positives",
    lambda: process([-1, 0, 3, -5]) == [3],
    source="trace:process#001, output=[3] observed 2026-06-18")
@idk("behavior with massive lists (>1M items) not verified",
    source="static: not covered in traces")
def process(data: list[int]) -> list[int]:
    return [x for x in data if x > 0]
```

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
│   └── protocol-v0.3.md        # Language-agnostic protocol spec (current)
├── python/
│   ├── anchorlaw-scanner/       # Standalone scanner (Level 1, VERIFIED)
│   └── anchorlaw/               # Full protocol (Level 2-4, EXPERIMENTAL)
└── typescript/
    └── anchorlaw-scanner/       # TS/JS scanner (Level 1, IN DEVELOPMENT)
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

- [Protocol Specification v0.3](spec/protocol-v0.3.md)
- Degraded Verification: [§9 of the spec](spec/protocol-v0.3.md#9-degraded-verification-v03-draft) — three operating modes for when code can't compile
- [Materialist Practice Theory](https://github.com/unknowbug/anchorlaw/wiki) — the philosophical foundation

---

> "This project does not promise eternal truth. It promises a set of tools forged in current historical conditions, open to being replaced by better ones. Its highest commitment is to make its users capable of questioning, improving, and ultimately transcending it."
>
> — First Law, Applied Reflexively
