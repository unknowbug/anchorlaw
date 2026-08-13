// anchorlaw-tools — Anchorlaw protocol tools for DSH.
//
// ESM Cordis plugin file, import-free on purpose: the preset loader resolves
// entry modules through Node's ESM resolver from the preset's own directory,
// which cannot reach the harness's node_modules.
//
// Registers four model tools into the session's tool registry:
//   anchorlaw_scan        — Level 1 defensive-pattern scanner (anchorlaw-scanner check)
//   anchorlaw_report      — code health report (scanner + noise + verdict)
//   anchorlaw_ai_context  — noise cards + curriculum export for LLM injection
//   anchorlaw_status      — toolchain versions + discovered anchor-* skills
//
// Maintained by: 大肥鱼 (DSH agent). Source of truth: E:\PYTHON\Anchorlaw-dsh\plugins\.

export const name = 'anchorlaw-tools'
export const inject = ['tools']

export function apply(ctx, config) {
  // Optional capabilities, read with ctx.get and handled when absent.
  const subprocess = ctx.get('subprocess')
  const skills = ctx.get('skills')
  const fsService = ctx.get('fs')
  const sandboxPolicy = ctx.get('sandboxPolicy')
  if (subprocess === undefined) return

  let pythonPathPromise
  function pythonPath() {
    if (!pythonPathPromise) pythonPathPromise = subprocess.resolveExecutable('python')
    return pythonPathPromise
  }

  function readAll(reader) {
    if (!reader) return ''
    let text = ''
    let offset = 0
    for (;;) {
      const chunk = reader.readFrom(offset)
      text += chunk.text
      if (chunk.nextOffset <= offset) break
      offset = chunk.nextOffset
    }
    return text
  }

  async function runPython(args, cwd) {
    const py = await pythonPath()
    const handle = subprocess.spawn({
      argv: [py].concat(args),
      cwd,
      stdio: {
        stdin: 'ignore',
        stdout: { maxBytes: 256 * 1024, spill: { maxBytes: 2 * 1024 * 1024 } },
        stderr: { maxBytes: 64 * 1024, spill: { maxBytes: 512 * 1024 } },
      },
      graceMs: 2000,
    })
    const outcome = await handle.done
    return {
      exitCode: outcome.exitCode,
      stdout: readAll(handle.collected.stdout),
      stderr: readAll(handle.collected.stderr),
    }
  }

  // The calling agent's session workspace, then the sandbox root, then '.'.
  function sessionCwd(exec) {
    try {
      const agent = exec && exec.agent
      if (agent && agent.session && agent.session.header && agent.session.header.cwd) {
        return agent.session.header.cwd
      }
    } catch (error) {
      // fall through
    }
    if (sandboxPolicy && sandboxPolicy.workspaceRoot) return sandboxPolicy.workspaceRoot
    return '.'
  }

  async function absPath(p, cwd) {
    const raw = String(p)
    if (fsService !== undefined) {
      try {
        const target = await fsService.resolve(raw, { cwd })
        return fsService.processPath(target)
      } catch (error) {
        // fall through to raw path
      }
    }
    return raw
  }

  function renderText(v) {
    return [{ type: 'text', text: String(v) }]
  }

  function register(definition) {
    ctx.effect(() => ctx.tools.register(definition))
  }

  register({
    name: 'anchorlaw_scan',
    description: 'Run the Anchorlaw protocol scanner (Level 1) over a file or directory and return the defensive-pattern findings (P1-P6) with ERR/WARN/INFO severity. Non-zero exit code 1 means ERR-level patterns were found; the findings are still returned as text.',
    parameters: {
      path: { type: 'string', required: true, description: 'File or directory to scan, absolute or relative to the session workspace.' },
      lang: { type: 'string', enum: ['python', 'cpp', 'go', 'java'], default: 'python', description: 'python = defensive patterns; cpp/go/java = @anchor annotation-extraction.' },
      recursive: { type: 'boolean', default: true, description: 'Recursively scan subdirectories.' },
    },
    output: { schema: { type: 'string' }, render(_args, v) { return renderText(v) } },
    async execute(args, exec) {
      const cwd = sessionCwd(exec)
      const argv = ['-m', 'anchorlaw_scanner', 'check', await absPath(args.path, cwd)]
      if (args.lang && args.lang !== 'python') argv.push('--lang', String(args.lang))
      if (args.recursive === false) argv.push('--no-recursive')
      const r = await runPython(argv, cwd)
      let out = r.stdout
      if (r.stderr && r.stderr.trim()) out += '\n[stderr]\n' + r.stderr
      out += `\n[exit code: ${r.exitCode}]`
      return out
    },
  })

  register({
    name: 'anchorlaw_report',
    description: 'Run the Anchorlaw protocol health report (scanner findings + noise-card backlog + diagnostic verdict) for a file or directory.',
    parameters: {
      path: { type: 'string', required: true, description: 'File or directory to report on, absolute or relative to the session workspace.' },
    },
    output: { schema: { type: 'string' }, render(_args, v) { return renderText(v) } },
    async execute(args, exec) {
      const cwd = sessionCwd(exec)
      const r = await runPython(['-m', 'anchorlaw_scanner', 'report', await absPath(args.path, cwd)], cwd)
      let out = r.stdout
      if (r.stderr && r.stderr.trim()) out += '\n[stderr]\n' + r.stderr
      out += `\n[exit code: ${r.exitCode}]`
      return out
    },
  })

  register({
    name: 'anchorlaw_ai_context',
    description: 'Export Anchorlaw AI context injection text (noise cards + extracted curriculum) for the given functions. Requires an initialized .anchorlaw directory in the working directory.',
    parameters: {
      functions: { type: 'string', description: 'Comma-separated function names to filter noise cards for.' },
      limit: { type: 'number', default: 20, description: 'Maximum number of cards.' },
      all: { type: 'boolean', default: false, description: 'Include resolved cards.' },
    },
    output: { schema: { type: 'string' }, render(_args, v) { return renderText(v) } },
    async execute(args, exec) {
      const cwd = sessionCwd(exec)
      const argv = ['-m', 'anchorlaw', 'ai-context']
      if (args.functions) argv.push('--functions', String(args.functions))
      if (args.limit != null) argv.push('--limit', String(args.limit))
      if (args.all) argv.push('--all')
      const r = await runPython(argv, cwd)
      let out = r.stdout
      if (r.stderr && r.stderr.trim()) out += '\n[stderr]\n' + r.stderr
      out += `\n[exit code: ${r.exitCode}]`
      return out
    },
  })

  register({
    name: 'anchorlaw_status',
    description: 'Report the Anchorlaw toolchain status: session workspace, python + anchorlaw-scanner + anchorlaw versions, and the list of installed anchor-* skills visible to the current session.',
    parameters: {},
    output: { schema: { type: 'string' }, render(_args, v) { return renderText(v) } },
    async execute(_args, exec) {
      const lines = []
      const cwd = sessionCwd(exec)
      lines.push(`[session workspace: ${cwd}]`)
      try {
        const code = 'import anchorlaw_scanner as s, anchorlaw as a; print("anchorlaw-scanner", getattr(s, "__version__", "?")); print("anchorlaw", a.__version__)'
        const r = await runPython(['-c', code], cwd)
        lines.push(r.stdout.trim() || '(no version output)')
        if (r.stderr && r.stderr.trim()) lines.push('[stderr] ' + r.stderr.trim())
        lines.push(`[exit code: ${r.exitCode}]`)
      } catch (error) {
        lines.push('python check failed: ' + error.message)
      }
      if (skills !== undefined) {
        try {
          const list = await skills.list({ cwd, scope: exec && exec.agent })
          const anchors = list.filter((s) => typeof s.name === 'string' && s.name.startsWith('anchor-'))
          lines.push('')
          lines.push(`anchor skills discovered: ${anchors.length}`)
          for (const s of anchors) lines.push(`  - ${s.name}: ${s.description}`)
        } catch (error) {
          lines.push('skills.list failed: ' + error.message)
        }
      }
      return lines.join('\n')
    },
  })
}
