# anchorlaw-scanner (TypeScript)

> Defensive code pattern detection for TypeScript/JavaScript — Anchorlaw Protocol Level 1

**Maturity: IN DEVELOPMENT** — cross-language port of the [verified Python scanner](https://github.com/unknowbug/anchorlaw/tree/main/python/anchorlaw-scanner). Pattern detection accuracy validated on test files; not yet tested on large production codebases.

## What it does

Scans TypeScript/JavaScript source code for **defensive patterns** — code constructs that signal the author was uncertain but chose to hide it rather than declare it.

| Pattern | Severity | What it catches |
|---------|----------|----------------|
| `swallowed-exception` | ERROR | `catch {}` — exception silently discarded, or `catch (e) { console.log(e) }` |
| `bare-except` | ERROR | `catch (e: any)` / bare `catch` — catching unknown errors |
| `missing-anchor` | WARNING | Exported function without `@anchor.test` or `@anchor.i_dont_know` JSDoc annotation |
| `defensive-null-chain` | WARNING | 3+ chained `if (x === null) return null` patterns |
| `trivial-test` | WARNING | Tautological assertions like `expect(result).toBe(result)` |
| `vague-todo` | INFO | `// TODO` without issue tracker reference |

## Install

```bash
npm install anchorlaw-scanner
```

## Usage

```bash
# Scan a file
npx anchorlaw-scanner check src/app.ts

# Scan a directory
npx anchorlaw-scanner check src/

# Generate a health report
npx anchorlaw-scanner report .
```

### Programmatic API

```typescript
import { scanFile, scanDirectory, summarize } from "anchorlaw-scanner";

// Scan a single file
const patterns = scanFile("src/index.ts");
for (const p of patterns) {
  console.log(`[${p.patternType}] ${p.filePath}:${p.lineNumber}`);
  console.log(`  ${p.suggestion}`);
}

// Scan a directory
const results = scanDirectory("src/");
console.log(`Scanned ${results.size} files`);

// Summarize
const summary = summarize(patterns);
console.log(summary); // { total, byType, bySeverity }
```

## The Principle

anchorlaw-scanner is based on a simple insight:

> Defensive code patterns expose the author's cognitive state — "I'm not sure about this, but I don't want to say I don't know."

The scanner doesn't judge. It surfaces the patterns so you can decide:

- "Yes, I know this is safe" → document why
- "No, I'm not sure" → add a `@anchor.i_dont_know` JSDoc annotation
- "Actually, this is a real problem" → fix it

### Using JSDoc Annotations

The scanner checks for anchorlaw annotations in JSDoc comments:

```typescript
/**
 * Process a list of items, keeping only positive values.
 *
 * @anchor.test "empty list returns empty" — process([]) === []
 * @anchor.test "keep positives" — process([-1, 0, 3, -5]) === [3]
 * @anchor.i_dont_know "behavior with massive lists (>1M) not verified"
 */
export function process(data: number[]): number[] {
  return data.filter((x) => x > 0);
}
```

Without these annotations, `process` would trigger a `missing-anchor` warning — not because it's buggy, but because it has no verifiable evidence of correctness.

## Differences from the Python Scanner

| Aspect | Python | TypeScript |
|--------|--------|-----------|
| AST parser | `ast` (stdlib) | TypeScript Compiler API |
| Anchor detection | Decorators (`@anchor.test`) | JSDoc annotations (`@anchor.test`) |
| File types | `.py` | `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs` |
| Maturity | **Verified** | **In Development** |

The TypeScript port uses JSDoc annotations instead of decorators because:
1. TypeScript decorators are still experimental (Stage 3)
2. JSDoc annotations work in both `.ts` and `.js` files
3. No runtime dependency required — annotations are pure documentation until the anchor system is ported

## Part of the Anchorlaw Protocol

This is Level 1 of the [Anchorlaw Protocol](https://github.com/unknowbug/anchorlaw) — a code verification protocol for vibe coding.

- **Level 1 (this package)**: Scanner — detect defensive patterns
- **Level 2+**: Anchors + Noise Cards — full verification protocol

For the Python full protocol including `@anchor.test` decorators, noise card tracking, and AI context injection, see the [Python anchorlaw package](https://github.com/unknowbug/anchorlaw/tree/main/python/anchorlaw).

## Contributing

This port needs **practice data**:

1. **Run it on your TypeScript codebase** — report false positives
2. **Compare with the Python scanner** — same patterns on equivalent code should produce the same results
3. **Test on large codebases** — we need to validate performance and accuracy at scale

## License

MIT
