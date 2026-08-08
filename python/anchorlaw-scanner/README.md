# anchorlaw-scanner

> Defensive code pattern detection for Python — Anchorlaw Protocol Level 1

**Maturity: VERIFIED** — tested on real projects, 0 false positives in initial runs.

## What it does

Scans Python source code for **defensive patterns** — code constructs that signal the author was uncertain but chose to hide it rather than declare it.

| Pattern | Severity | What it catches |
|---------|----------|----------------|
| `swallowed-exception` | ERROR | `except: pass` — exception silently discarded |
| `bare-except` | ERROR | Blanket `except:` — catching unknown errors |
| `missing-anchor` | WARNING | Public function without `@anchor.test` or `@anchor.i_dont_know` |
| `defensive-null-chain` | WARNING | 3+ chained `if x is None: return None` |
| `trivial-test` | WARNING | Tautological assertions like `assert f(x) == f(x)` |
| `vague-todo` | INFO | `# TODO` without issue tracker reference |

## Install

```bash
pip install anchorlaw-scanner
```

## Usage

```bash
# Scan a file
anchorlaw-scanner check app.py

# Scan a directory
anchorlaw-scanner check src/

# Generate a health report
anchorlaw-scanner report my_project/
```

## The Principle

anchorlaw-scanner is based on a simple insight:

> Defensive code patterns expose the author's cognitive state — "I'm not sure about this, but I don't want to say I don't know."

The scanner doesn't judge. It surfaces the patterns so you can decide:
- "Yes, I know this is safe" → document why
- "No, I'm not sure" → add a `@anchor.i_dont_know` anchor
- "Actually, this is a real problem" → fix it

## Part of the Anchorlaw Protocol

This is Level 1 of the [Anchorlaw Protocol](https://github.com/unknowbug/anchorlaw) — a code verification protocol for vibe coding.

- **Level 1 (this package)**: Scanner — detect defensive patterns
- **Level 2+**: Anchors + Noise Cards — full verification protocol

For the full protocol including `@anchor.test` anchors, noise card tracking, and AI context injection, install the `anchorlaw` package.

## License

MIT
