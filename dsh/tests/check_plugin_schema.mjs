// check_plugin_schema.mjs — verify every anchorlaw-* tool declares a compiled
// JSON-Schema `parameters` object root before the plugin may be mounted.
//
// WHY THIS EXISTS (2026-08-13 incident): ctx.tools.register() projects
// `definition.parameters` VERBATIM to the model and does NOT compile it. The
// first version of plugins/anchorlaw-tools.js passed a flat per-property spec
// (defineTool input style). Mounted globally through a profile's
// cordis.patch.yml, the flat spec reached the LLM without a top-level
// `type: 'object'` and every session failed with
// "Invalid schema for function 'anchorlaw_ai_context': ... got 'type: null'".
// This check runs from scripts/selfcheck.ps1 (item 5) and before the global
// tool mount in scripts/install.ps1, so a bad schema can never be installed.
//
// Exit code 0 = pass; 1 = any tool fails the shape check.

import { pathToFileURL } from 'node:url'

const pluginPath = new URL('../plugins/anchorlaw-tools.js', import.meta.url)
const expected = new Set([
  'anchorlaw_scan',
  'anchorlaw_report',
  'anchorlaw_ai_context',
  'anchorlaw_status',
])

// Minimal ctx: subprocess present so apply() registers, effect() runs the
// registration immediately, tools.register() captures the definition.
const registered = []
const ctx = {
  get(name) {
    if (name === 'subprocess') {
      return {
        resolveExecutable: async () => 'python',
        spawn: () => ({
          done: Promise.resolve({ exitCode: 0 }),
          collected: {
            stdout: { readFrom: () => ({ text: '', nextOffset: 0 }) },
            stderr: { readFrom: () => ({ text: '', nextOffset: 0 }) },
          },
        }),
      }
    }
    return undefined
  },
  effect(fn) {
    fn()
  },
  tools: {
    register(definition) {
      registered.push(definition)
    },
  },
}

const plugin = await import(pluginPath.href)
plugin.apply(ctx, {})

const failures = []
const found = new Set(registered.map((d) => d.name))
for (const name of expected) {
  if (!found.has(name)) failures.push(`${name}: not registered (got ${[...found].sort().join(', ') || 'none'})`)
}
for (const def of registered) {
  const p = def.parameters
  if (p === null || typeof p !== 'object' || Array.isArray(p)) {
    failures.push(`${def.name}: parameters must be an object root (got ${String(p)})`)
    continue
  }
  if (p.type !== 'object') {
    failures.push(`${def.name}: parameters.type must be "object" (got ${JSON.stringify(p.type)})`)
  }
  if (p.properties === null || typeof p.properties !== 'object' || Array.isArray(p.properties)) {
    failures.push(`${def.name}: parameters.properties must be an object map`)
  }
}

if (failures.length > 0) {
  console.error(`FAIL (${failures.length}):`)
  for (const f of failures) console.error(`  - ${f}`)
  process.exit(1)
}

console.log(`OK: ${registered.length} anchorlaw tools declare compiled JSON-Schema parameters`)
