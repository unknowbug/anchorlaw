# Practify Protocol

> **"Any claim must have a verifiable practice anchor."**
>
> — First Law, Materialist Practice Theory

Practify is a **code verification protocol for vibe coding** — not a test framework, not a linter.

It detects **defensive code patterns** that signal cognitive gaps and provides a **structured feedback loop** for AI-assisted development.

---

## Maturity (Per Component, Per First Law)

| Component | Python | TypeScript | Maturity |
|-----------|--------|-----------|----------|
| **Scanner** | ✅ [practify-scanner](python/practify-scanner/) | ✅ [practify-scanner](typescript/practify-scanner/) | **VERIFIED** — tested on real projects |
| **Anchors** | ✅ [practify](python/practify/) | — | **EXPERIMENTAL** — API stable, no efficacy data |
| **Noise Cards** | ✅ [practify](python/practify/) | — | **UNVERIFIED** — schema defined, no accumulated data |
| **AI Context** | ✅ [practify](python/practify/) | — | **CONJECTURE** — format defined, no A/B test |

> **Honesty notice**: Components marked EXPERIMENTAL, UNVERIFIED, or CONJECTURE are working hypotheses. Their value has not been demonstrated through practice. Use them to help us test the hypotheses — not because we claim they work.

---

## Quick Start

### Scanner (Immediate Value)

```bash
# Python
pip install practify-scanner
practify-scanner check src/

# TypeScript
npm install practify-scanner
npx practify-scanner check src/
```

The scanner finds:
- **Swallowed exceptions** — `except: pass` / `catch {}`
- **Bare exception handlers** — catching `Exception` / `any`
- **Missing anchors** — functions with no `@pract.test` or `@pract.i_dont_know`
- **Defensive null chains** — 3+ chained `if x is None: return None`
- **Trivial tests** — `assert f(x) == f(x)`
- **Vague TODOs** — `// TODO: fix` without ticket reference

### Full Protocol (Experimental)

```bash
pip install practify
```

```python
import practify as pract

@pract.test("empty list returns empty", lambda: process([]) == [])
@pract.test("keep positives", lambda: process([-1, 0, 3, -5]) == [3])
@pract.i_dont_know("behavior with massive lists (>1M items) not verified")
def process(data: list[int]) -> list[int]:
    return [x for x in data if x > 0]
```

---

## The Principle

Traditional development separates "writing code" from "writing tests." Vibe coding makes this separation costly — AI generates code fast, but verification happens later, manually, and feedback is lost between iterations.

Practify inverts this: **tests are part of the declaration, not an add-on.** A function without a test anchor or an `i_dont_know` declaration is flagged at scan time — not because it's buggy, but because it has no evidence of correctness.

When tests fail at runtime, failures are captured as **noise cards** — structured knowledge that accumulates over time and can be injected back into AI context for future code generation.

### "Only Offense, No Defense"

The protocol does not prohibit — it demands proof:
- Traditional: "You cannot divide by zero." (defensive)
- Practify: "Prove the divisor is non-zero, or handle the zero case." (offensive)

The single allowed defense is `@pract.i_dont_know` — an honest declaration that opens the battlefield for practice feedback.

---

## Project Structure

```
practify/
├── README.md                    <-- you are here
├── spec/
│   └── protocol-v0.1.md        # Language-agnostic protocol spec
├── python/
│   ├── practify-scanner/       # Standalone scanner (Level 1, VERIFIED)
│   └── practify/               # Full protocol (Level 2-4, EXPERIMENTAL)
└── typescript/
    └── practify-scanner/       # TS/JS scanner (Level 1, IN DEVELOPMENT)
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

- [Protocol Specification v0.1](spec/protocol-v0.1.md)
- [Materialist Practice Theory](https://github.com/practify/practify/wiki) — the philosophical foundation

---

> "This project does not promise eternal truth. It promises a set of tools forged in current historical conditions, open to being replaced by better ones. Its highest commitment is to make its users capable of questioning, improving, and ultimately transcending it."
>
> — First Law, Applied Reflexively
