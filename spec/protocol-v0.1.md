# Practify Protocol v0.1

> **语言无关的代码验证协议规范**
>
> "任何声称都必须有可验证的实践锚点。"
>
> Status: **Working Draft**. Components are at different maturity levels — see [Maturity](#maturity).

---

## 1. Protocol Overview

Practify is a **three-layer code verification protocol** for vibe coding workflows:

| Layer | What it does | When it runs | Maturity |
|-------|-------------|-------------|----------|
| **Scanner** | Detects defensive code patterns via AST analysis | Compile-time (static) | **Verified** — tested on real projects, 0 false positives in initial runs |
| **Anchors** | Binds verifiable tests to function declarations | Compile-time (declarative) + Runtime (validation) | **Experimental** — API stable, efficacy data pending |
| **Noise Cards** | Accumulates runtime failures as structured knowledge | Runtime (continuous) | **Unverified** — schema defined, no project has accumulated >10 cards |

### Core Principle (First Law)

> Any claim must be convertible to a verifiable practice test, executable in finite steps with observable results. Otherwise it is invalid for the purpose of pursuing effectiveness.

In code: every public function must have either a `test` anchor or an `i_dont_know` declaration.

### "Only Offense, No Defense"

The protocol does not prohibit. It demands proof.
- Traditional: "You cannot divide by zero." (defensive)
- Practify: "Prove the divisor is non-zero, or handle the zero case." (offensive)

The single allowed defense is `i_dont_know` — an honest declaration of ignorance that opens the battlefield rather than closing it.

---

## 2. Noise Card JSON Schema

Noise cards are the **cross-language runtime layer**. Any language implementation of practify MUST produce noise cards conforming to this schema.

### 2.1 Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://practify.dev/noise-card-v0.1.json",
  "type": "object",
  "required": ["noise_id", "timestamp", "trigger", "function_name", "observed", "expected"],
  "properties": {
    "noise_id": {
      "type": "string",
      "description": "Globally unique identifier, e.g. 'noise-{uuid-prefix}' or '{project}-{seq}'"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of when the failure was observed"
    },
    "trigger": {
      "type": "string",
      "description": "Exact input or condition that triggered the failure, e.g. 'process([]) returned null'"
    },
    "function_name": {
      "type": "string",
      "description": "Fully qualified name of the function involved"
    },
    "observed": {
      "type": "string",
      "description": "What actually happened. Be specific — stack traces, return values, error messages."
    },
    "expected": {
      "type": "string",
      "description": "What should have happened according to the function's claimed behavior."
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
      "description": "A concise, reusable lesson that can be injected into AI context. Should be actionable: 'When handling external input, always validate type before processing' rather than 'type errors are bad'."
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
      "description": "Classification tags, e.g. 'type-safety', 'null-handling', 'concurrency'"
    },
    "context_snippet": {
      "type": "string",
      "description": "Code snippet surrounding the failure point (max 500 chars)"
    },
    "language": {
      "type": "string",
      "description": "Programming language this noise originated from, e.g. 'python', 'typescript', 'rust'"
    }
  }
}
```

### 2.2 Storage

Noise cards are stored as a JSON array in `.pract/noise_cards.json`:

```json
{
  "updated": "2026-06-17T12:00:00Z",
  "total": 42,
  "unresolved": 15,
  "cards": [
    { "...": "..." }
  ]
}
```

### 2.3 Cross-Language Notes

- The `language` field enables cross-language curriculum: a noise card from a Python project can inform AI context for a Rust project, since curriculum text is language-agnostic patterns.
- Implementations MUST use this exact schema for interoperability.
- Additional implementation-specific fields MAY be added under a `_meta` key.

---

## 3. AI Context Format

The AI context is the **primary vibe-coding interface** of practify. It is what gets injected into LLM system prompts.

### 3.1 Format Specification

```
# Historical Noise Cards (Practice Knowledge Base)
## Stats: {N} cards ({U} unresolved, {R} resolved)
## Note: These are cognitive boundaries discovered through past practice failures.
When generating code, actively avoid known problem patterns.

### Noise #1
[{STATUS}] Noise {short_id}
  Function: {function_name}
  Trigger: {trigger}
  Observed: {observed}
  Expected: {expected}
  Discovery: {discovery}
  Pattern: {curriculum}
  Regression test: {converted_to_test}

---
### Noise #2
...
```

Where `{STATUS}` is `[RESOLVED]` or `[UNRESOLVED]`.

### 3.2 Injection Strategy

For vibe coding:
1. When AI is about to generate/modify code in a project with practify noise cards, inject the AI context for functions being touched.
2. If no specific functions are known, inject the most recent 10 unresolved cards.
3. Also inject the curriculum from resolved cards as a "coding patterns" section.

### 3.3 Curriculum Extract

```
# Coding Patterns Extracted from Practice Noise
1. {curriculum from resolved card 1}
2. {curriculum from resolved card 2}
...
```

---

## 4. Anchor Semantics

Anchors are **language-specific in implementation** but share common semantics across languages.

### 4.1 Test Anchor

| Property | Description |
|----------|-------------|
| **Purpose** | A verifiable practice test bound to a function declaration |
| **Semantics** | "I claim this function behaves correctly under condition X, and here is a reproducible test that proves it." |
| **Required fields** | `description` (human-readable), `test_fn` (executable predicate returning boolean) |
| **Compile-time check** | Every public function MUST have at least one test anchor OR one i_dont_know anchor |
| **Runtime check** | Test anchors SHOULD be executable via `practify test` |

### 4.2 I-Don't-Know Anchor

| Property | Description |
|----------|-------------|
| **Purpose** | Honest declaration of a cognitive boundary |
| **Semantics** | "This function has edge cases I haven't verified yet. I am actively inviting practice feedback on these boundaries." |
| **Required fields** | `what` (specific description of what is unknown) |
| **Difference from TODO** | TODO is "I know what to do but haven't done it." I-don't-know is "I don't yet know what the correct behavior is." |

### 4.3 Anchor Health States

| State | Condition | Meaning |
|-------|----------|---------|
| `healthy` | All tests pass | Function's claimed behavior is verified |
| `unverified` | Only i_dont_know anchors, no tests | Exploration zone — behavior not yet determined |
| `degrading` | Has tests but some fail | Previously verified behavior is now broken — possible regression or environment change |
| `skeleton` | No anchors at all | Violation of First Law — function claims correctness with no evidence |

### 4.4 Language-Specific Notes

- **Python**: Implemented via decorators (`@pract.test`, `@pract.i_dont_know`)
- **Rust**: Could be implemented via proc macros (`#[pract::test]`, `#[pract::i_dont_know]`)
- **TypeScript**: Could be implemented via decorators or JSDoc annotations
- **Go**: Could be implemented via code generation from comments

---

## 5. Scanner Pattern Catalog

The scanner detects **defensive code patterns** — signals that the author is uncertain but refusing to say "I don't know."

### 5.1 Pattern Definitions

#### P1: Swallowed Exception

| Property | Value |
|----------|-------|
| **Severity** | ERROR |
| **Definition** | An exception handler whose body performs no meaningful error handling (just `pass`, or a single log/print call) |
| **Signal** | "I don't know what errors can occur here, and I don't want to think about it." |
| **Suggestion** | "You are swallowing an exception. Is this known to be safe (document why)? Or do you not know how to handle it (use @i_dont_know)?" |
| **AST pattern** | Try/catch where catch body is empty or contains only a log statement |
| **Cross-language** | `except: pass` (Python), `catch {}` (JS), `catch (_) {}` (Rust with empty block), `} catch (Exception e) { log.debug(...) }` (Java) |

#### P2: Bare Exception Handler

| Property | Value |
|----------|-------|
| **Severity** | ERROR |
| **Definition** | Catching an overly broad exception type (e.g., Python `except:`, Java `catch (Exception e)`, Rust `catch (_)` when not intentional) |
| **Signal** | "I don't know what specific errors can occur, so I'll catch everything." |
| **Cross-language** | `except:` (Python bare), `catch (Exception e)` (Java/C# — broad), `catch(_)` (Rust) |

#### P3: Missing Practice Anchor

| Property | Value |
|----------|-------|
| **Severity** | WARNING |
| **Definition** | A public function without a test anchor or i_dont_know declaration |
| **Signal** | "This function claims to do something, but has no verifiable evidence." |
| **Cross-language** | Language-specific decorator/attribute detection |

#### P4: Defensive Null Propagation

| Property | Value |
|----------|-------|
| **Severity** | WARNING |
| **Definition** | Chained null/None checks that propagate null rather than handling it — pattern: `if x == null: return null` repeated 3+ times in a function |
| **Signal** | "I'm pushing the null problem to my caller instead of solving it." |
| **Cross-language** | `if x is None: return None` (Python), `if (x == null) return null;` (JS/Java/C#), `if x.is_none() { return None; }` (Rust) |

#### P5: Trivially True Test

| Property | Value |
|----------|-------|
| **Severity** | WARNING |
| **Definition** | A test assertion that is always true regardless of implementation, e.g., `assert f(x) == f(x)` |
| **Signal** | "I'm simulating a test without actually testing anything." |
| **Cross-language** | Self-comparison assertions in any language |

#### P6: Vague TODO

| Property | Value |
|----------|-------|
| **Severity** | INFO |
| **Definition** | A TODO/FIXME comment without an issue tracker reference or specific action plan |
| **Signal** | "I know there's a problem but I won't commit to fixing it." |
| **Cross-language** | Comment parsing in any language |

### 5.2 Pattern Detection Rules

Implementations MUST detect P1-P3 (high signal). P4-P6 are RECOMMENDED.

Each implementation MUST:
1. Return patterns with file path, line number, code snippet, and suggestion
2. Classify each pattern by severity (ERROR, WARNING, INFO)
3. NOT produce patterns that cannot be fixed (no "this code is ugly" — only "this code hides a cognitive gap")

---

## 6. Implementation Compliance Levels

| Level | Requirements |
|-------|-------------|
| **Level 1 — Scanner** | Implements P1-P3 pattern detection in the target language. Exposes a CLI. |
| **Level 2 — Anchors** | Level 1 + language-appropriate anchor system (test/i_dont_know decorators or equivalents) |
| **Level 3 — Noise** | Level 2 + noise card creation and AI context export conforming to the schema |
| **Level 4 — Full Protocol** | Level 3 + runtime noise card accumulation integrated with the language's test runner |

---

## 7. Maturity

| Component | Maturity | Evidence |
|-----------|----------|----------|
| Scanner (Python) | **Verified** | Tested on real projects. 38 findings, 0 false positives in initial run. |
| Scanner (TypeScript) | **In Development** | Implementation in progress. |
| Anchors (Python) | **Experimental** | API stable. No efficacy data from real projects. |
| Noise Cards (Python) | **Unverified** | Schema defined. No project has accumulated significant noise data. |
| AI Context Injection | **Conjecture** | Format defined. No A/B test has been conducted. |
| Full Protocol | **Conjecture** | End-to-end workflow not yet demonstrated on a real project. |

---

## 8. Versioning

- Protocol versions are `v{major}.{minor}`.
- Minor version changes MUST be backward-compatible (old noise cards remain readable).
- Major version changes MAY break schema compatibility.
- Current version: **v0.1** — pre-stable, all components subject to change based on practice feedback.

---

> "This specification is a working hypothesis. Its truth will be determined not by argument, but by whether it produces more reliable code in practice."
>
> — First Law, Applied Reflexively
